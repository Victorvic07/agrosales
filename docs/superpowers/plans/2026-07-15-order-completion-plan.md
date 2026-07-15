# Conclusão de Pedido — Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Concluir pedidos confirmados, consumir reservas ativas e reduzir o estoque físico e reservado dos lotes em uma única transação.

**Architecture:** O `OrderCompletionService` coordenará pedido, reservas e lotes. Somente pedidos `CONFIRMED` poderão ser concluídos. Para cada reserva ativa, o serviço reduzirá `physical_quantity` e `reserved_quantity`, marcará a reserva como `CONSUMED` e finalizará o pedido.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy Async, PostgreSQL 17, Pytest.

## Regras

- Apenas `ADMINISTRADOR` e `PRODUTOR` podem concluir.
- `VENDEDOR` recebe `403`.
- Pedido inexistente retorna `404`.
- Apenas pedidos `CONFIRMED` podem ser concluídos.
- Cada reserva `ACTIVE` deve virar `CONSUMED`.
- Para cada reserva:
  - `physical_quantity -= reservation.quantity`
  - `reserved_quantity -= reservation.quantity`
- Nenhum saldo pode ficar negativo.
- O pedido deve receber:
  - `status = COMPLETED`
  - `completed_at = datetime.now(timezone.utc)`
- A operação usa um único `commit`.
- Qualquer falha executa `rollback`.

## Arquivos

### Criar

```text
backend/app/modules/orders/order_completion_service.py
backend/tests/test_order_completion_service.py
backend/tests/test_order_completion_api.py
```

### Alterar

```text
backend/app/api/routers/orders.py
```

## Tarefa 1 — Serviço

Criar `OrderCompletionService` com:

```python
async def complete(
    self,
    order_id: UUID,
) -> Order
```

Erros:

```text
OrderNotFoundError
OrderCannotBeCompletedError
InvalidStockBalanceError
```

Testes:

- conclui pedido confirmado;
- reduz estoque físico;
- reduz estoque reservado;
- marca reserva como `CONSUMED`;
- rejeita pedido fora de `CONFIRMED`;
- rollback em saldo inconsistente;
- executa apenas um commit.

## Tarefa 2 — Endpoint

Adicionar:

```text
POST /api/v1/orders/{order_id}/complete
```

Permissões:

```text
ADMINISTRADOR
PRODUTOR
```

Mapeamento:

```text
404 — pedido não encontrado
409 — pedido não pode ser concluído
422 — saldo de estoque inconsistente
403 — vendedor
```

## Tarefa 3 — Verificação

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
POST /api/v1/orders/{order_id}/complete
```

Resultado esperado:

- pedido `COMPLETED`;
- `completed_at` preenchido;
- reservas `CONSUMED`;
- `physical_quantity` reduzido;
- `reserved_quantity` reduzido.
