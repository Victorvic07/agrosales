# Confirmação de Pedido com FEFO — Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Confirmar pedidos em `DRAFT`, reservar todos os itens por FEFO, vincular reservas aos itens e garantir rollback completo se qualquer item falhar.

**Architecture:** Uma migração adicionará `order_item_id` em `stock_reservations`. O `OrderConfirmationService` coordenará pedido, cliente, lotes, reservas e transação. O router terá um endpoint específico de confirmação acessível somente para `ADMINISTRADOR` e `PRODUTOR`.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy Async, PostgreSQL 17, Alembic, Pydantic e Pytest.

## Global Constraints

- Apenas pedidos `DRAFT` podem ser confirmados.
- O pedido precisa ter pelo menos um item.
- O cliente precisa continuar ativo.
- Cada item será reservado usando FEFO.
- Cada reserva será vinculada a `order_item_id`.
- Se um item não tiver estoque, nenhuma reserva permanecerá.
- O pedido continuará `DRAFT` quando houver falha.
- O sucesso altera o pedido para `CONFIRMED` e preenche `confirmed_at`.
- A operação inteira usa um único `commit`.
- Falhas executam `rollback`.
- Apenas `ADMINISTRADOR` e `PRODUTOR` podem confirmar.
- `VENDEDOR` recebe `403`.

---

## Estrutura de arquivos

### Criar

```text
backend/app/modules/orders/order_confirmation_service.py
backend/app/migrations/versions/0009_link_reservations_to_order_items.py
backend/tests/test_order_confirmation_service.py
backend/tests/test_order_confirmation_api.py
backend/tests/test_order_reservation_migration.py
```

### Alterar

```text
backend/app/modules/inventory/reservation_model.py
backend/app/modules/inventory/reservation_repository.py
backend/app/api/routers/orders.py
```

---

## Tarefa 1 — Vínculo entre reserva e item

- [ ] Adicionar `order_item_id: UUID | None` ao modelo `StockReservation`.
- [ ] Criar FK para `order_items.id`.
- [ ] Adicionar índice.
- [ ] Manter o campo opcional para preservar reservas manuais já existentes.
- [ ] Criar teste de modelo.
- [ ] Commit:

```powershell
git commit -m "feat: vincula reservas aos itens do pedido"
```

---

## Tarefa 2 — Migração 0009

Criar:

```text
backend/app/migrations/versions/0009_link_reservations_to_order_items.py
```

A migração deve:

```text
down_revision = "0008"
```

E executar:

```python
op.add_column(
    "stock_reservations",
    sa.Column(
        "order_item_id",
        postgresql.UUID(as_uuid=True),
        nullable=True,
    ),
)
```

Também deve criar:

- chave estrangeira para `order_items.id`;
- índice `ix_stock_reservations_order_item_id`.

O downgrade deve remover índice, FK e coluna.

Commit:

```powershell
git commit -m "feat: adiciona migracao de reservas por item"
```

---

## Tarefa 3 — Repository para confirmação

Adicionar ao `ReservationRepository`:

```python
def add(self, reservation: StockReservation) -> None
```

Manter o método de busca FEFO existente:

```python
async def get_eligible_lots(
    product_variation_id: UUID,
    reference_date: date,
) -> list[Lot]
```

Adicionar ao `OrderRepository` uma busca com bloqueio:

```python
async def get_by_id_for_update(
    order_id: UUID,
) -> Order | None
```

A consulta deve:

- carregar os itens com `selectinload`;
- usar `with_for_update()`.

Commit:

```powershell
git commit -m "feat: adiciona bloqueio para confirmar pedidos"
```

---

## Tarefa 4 — Serviço de confirmação

Criar:

```text
backend/app/modules/orders/order_confirmation_service.py
```

Erros:

```text
OrderNotFoundError
OrderCannotBeConfirmedError
OrderWithoutItemsError
InactiveCustomerError
```

Interface principal:

```python
async def confirm(
    self,
    order_id: UUID,
    reference_date: date | None = None,
) -> Order
```

Fluxo:

1. buscar pedido com bloqueio;
2. validar existência;
3. validar status `DRAFT`;
4. validar ao menos um item;
5. validar cliente ativo;
6. para cada item:
   - buscar lotes elegíveis;
   - aplicar FEFO;
   - atualizar `reserved_quantity`;
   - criar `StockReservation` com `order_item_id`;
7. alterar status para `CONFIRMED`;
8. preencher `confirmed_at`;
9. executar um único `commit`;
10. atualizar e retornar o pedido.

Em qualquer exceção:

```python
await session.rollback()
raise
```

Testes obrigatórios:

- confirma pedido com um item;
- divide um item entre vários lotes;
- cria reservas com `order_item_id`;
- confirma vários itens;
- rollback quando o segundo item falha;
- pedido permanece `DRAFT` em falha;
- rejeita pedido sem itens;
- rejeita cliente inativo;
- rejeita pedido fora de `DRAFT`;
- executa somente um `commit`.

Commit:

```powershell
git commit -m "feat: adiciona confirmacao transacional de pedidos"
```

---

## Tarefa 5 — Endpoint de confirmação

Adicionar em:

```text
backend/app/api/routers/orders.py
```

Endpoint:

```text
POST /api/v1/orders/{order_id}/confirm
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
409 — pedido fora de DRAFT
422 — pedido sem itens
422 — cliente inativo
422 — estoque insuficiente
403 — vendedor
```

Testes:

- vendedor recebe `403`;
- pedido inexistente recebe `404`;
- falta de estoque recebe `422`;
- confirmação bem-sucedida retorna `CONFIRMED`.

Commit:

```powershell
git commit -m "feat: adiciona endpoint de confirmacao de pedidos"
```

---

## Tarefa 6 — Verificação completa

No PC principal:

```powershell
cd "C:\Projetos\agrosales\backend"
python -m pytest -v
```

No notebook com Docker:

```powershell
cd "\\192.168.100.37\Projetos\agrosales"
docker compose up -d --build api
docker compose exec api alembic upgrade head
docker compose exec api alembic current
```

Esperado:

```text
0009 (head)
```

Validar estrutura:

```powershell
docker compose exec db psql -U agrosales -d agrosales -c "\d stock_reservations"
```

Validar no Swagger:

```text
POST /api/v1/orders/{order_id}/confirm
```

Conferir banco:

```powershell
docker compose exec db psql -U agrosales -d agrosales -c "SELECT id, order_item_id, lot_id, quantity, status FROM stock_reservations ORDER BY created_at DESC;"
```

E:

```powershell
docker compose exec db psql -U agrosales -d agrosales -c "SELECT id, status, confirmed_at FROM orders ORDER BY created_at DESC;"
```

Resultado esperado:

- pedido `CONFIRMED`;
- `confirmed_at` preenchido;
- reservas `ACTIVE`;
- cada reserva ligada ao item;
- `reserved_quantity` atualizado.
