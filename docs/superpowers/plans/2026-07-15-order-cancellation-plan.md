# Cancelamento de Pedido — Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Permitir o cancelamento de pedidos em `DRAFT` ou `CONFIRMED`, liberando reservas ativas e reduzindo `reserved_quantity` dos lotes em uma única transação.

**Architecture:** O `OrderCancellationService` coordenará pedido, reservas e lotes. Pedidos em `DRAFT` serão cancelados sem alterar estoque. Pedidos em `CONFIRMED` terão reservas `ACTIVE` alteradas para `RELEASED`, com devolução do saldo reservado aos lotes. O router exporá um endpoint restrito a `ADMINISTRADOR` e `PRODUTOR`.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy Async, PostgreSQL 17, Pytest.

## Global Constraints

- Apenas `ADMINISTRADOR` e `PRODUTOR` podem cancelar.
- `VENDEDOR` recebe `403`.
- Pedido inexistente retorna `404`.
- Pedidos `COMPLETED` não podem ser cancelados.
- Pedidos `CANCELLED` não podem ser cancelados novamente.
- Pedido `DRAFT` pode ser cancelado sem alterar estoque.
- Pedido `CONFIRMED` deve liberar todas as reservas `ACTIVE`.
- Cada reserva liberada muda para `RELEASED`.
- Para cada reserva liberada:
  - `lot.reserved_quantity -= reservation.quantity`
- Nenhum saldo reservado pode ficar negativo.
- A operação deve usar um único `commit`.
- Qualquer falha executa `rollback`.
- O pedido deve receber:
  - `status = CANCELLED`
  - `cancelled_at = datetime.now(timezone.utc)`

---

## Estrutura de arquivos

### Criar

```text
backend/app/modules/orders/order_cancellation_service.py
backend/tests/test_order_cancellation_service.py
backend/tests/test_order_cancellation_api.py
```

### Alterar

```text
backend/app/modules/inventory/reservation_repository.py
backend/app/api/routers/orders.py
```

---

## Tarefa 1 — Consultar reservas ativas por pedido

Adicionar ao `ReservationRepository`:

```python
async def list_active_by_order(
    self,
    order_id: UUID,
) -> list[StockReservation]
```

A consulta deve:

- juntar `stock_reservations` com `order_items`;
- filtrar `OrderItem.order_id == order_id`;
- filtrar `StockReservation.status == ReservationStatus.ACTIVE`;
- carregar o lote com `selectinload(StockReservation.lot)`;
- usar `with_for_update()`.

Teste:

- retorna somente reservas ativas do pedido;
- chama `session.scalars`.

Commit:

```powershell
git commit -m "feat: adiciona consulta de reservas ativas por pedido"
```

---

## Tarefa 2 — Serviço de cancelamento

Criar:

```text
backend/app/modules/orders/order_cancellation_service.py
```

Erros:

```text
OrderNotFoundError
OrderCannotBeCancelledError
InvalidReservedStockError
```

Interface:

```python
async def cancel(
    self,
    order_id: UUID,
) -> Order
```

Fluxo:

1. buscar pedido com `get_by_id_for_update`;
2. validar existência;
3. rejeitar `COMPLETED`;
4. rejeitar `CANCELLED`;
5. se `DRAFT`:
   - mudar para `CANCELLED`;
   - preencher `cancelled_at`;
   - commit;
6. se `CONFIRMED`:
   - buscar reservas ativas;
   - para cada reserva:
     - validar que `lot` existe;
     - validar `reserved_quantity >= reservation.quantity`;
     - reduzir `reserved_quantity`;
     - alterar status para `RELEASED`;
   - alterar pedido para `CANCELLED`;
   - preencher `cancelled_at`;
   - commit;
7. em qualquer exceção:
   - rollback;
   - relançar.

Testes:

- cancela pedido `DRAFT`;
- cancela pedido `CONFIRMED`;
- libera várias reservas;
- reduz `reserved_quantity`;
- altera reserva para `RELEASED`;
- rejeita pedido `COMPLETED`;
- rejeita pedido já cancelado;
- rollback quando o saldo reservado é inconsistente;
- executa apenas um commit.

Commit:

```powershell
git commit -m "feat: adiciona cancelamento transacional de pedidos"
```

---

## Tarefa 3 — Endpoint de cancelamento

Adicionar em:

```text
backend/app/api/routers/orders.py
```

Endpoint:

```text
POST /api/v1/orders/{order_id}/cancel
```

Resposta:

```text
200 OK
```

Permissões:

```python
require_roles(
    UserRole.ADMINISTRADOR,
    UserRole.PRODUTOR,
)
```

Mapeamento:

```text
404 — pedido não encontrado
409 — pedido não pode ser cancelado
422 — saldo reservado inconsistente
403 — vendedor
```

Testes:

- vendedor recebe `403`;
- pedido inexistente retorna `404`;
- pedido concluído retorna `409`;
- cancelamento bem-sucedido retorna `CANCELLED`.

Commit:

```powershell
git commit -m "feat: adiciona endpoint de cancelamento de pedidos"
```

---

## Tarefa 4 — Verificação completa

No PC principal:

```powershell
cd "C:\Projetos\agrosales\backend"
python -m pytest -v
```

No notebook com Docker:

```powershell
cd "\\192.168.100.37\Projetos\agrosales"
docker compose up -d --build api
docker compose logs api --tail 50
```

Validar no Swagger:

```text
POST /api/v1/orders/{order_id}/cancel
```

Conferir pedidos:

```powershell
docker compose exec db psql -U agrosales -d agrosales -c "SELECT id, status, cancelled_at FROM orders ORDER BY created_at DESC;"
```

Conferir reservas:

```powershell
docker compose exec db psql -U agrosales -d agrosales -c "SELECT id, order_item_id, lot_id, quantity, status FROM stock_reservations ORDER BY created_at DESC;"
```

Conferir lotes:

```powershell
docker compose exec db psql -U agrosales -d agrosales -c "SELECT id, code, physical_quantity, reserved_quantity FROM lots ORDER BY expiration_date;"
```

Resultado esperado:

- pedido `CANCELLED`;
- `cancelled_at` preenchido;
- reservas do pedido em `RELEASED`;
- `reserved_quantity` devolvido corretamente;
- nenhuma alteração parcial.
