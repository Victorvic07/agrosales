# Order Status History Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Registrar e consultar todo o histórico de mudanças de status dos pedidos, incluindo o usuário responsável por cada ação.

**Architecture:** Uma nova tabela `order_status_history` armazenará cada transição de status. A criação, confirmação, cancelamento e conclusão do pedido gravarão o histórico na mesma transação da mudança principal. Um endpoint separado listará o histórico em ordem cronológica.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy Async, Alembic, PostgreSQL 17, Pytest.

## Global Constraints

- Registrar `null -> DRAFT` na criação do pedido.
- Registrar `DRAFT -> CONFIRMED` na confirmação.
- Registrar `DRAFT/CONFIRMED -> CANCELLED` no cancelamento.
- Registrar `CONFIRMED -> COMPLETED` na conclusão.
- Salvar `changed_by_user_id` em todas as transições.
- Gravar histórico e mudança do pedido na mesma transação.
- Executar rollback integral em qualquer falha.
- Expor `GET /api/v1/orders/{order_id}/history`.
- Permitir consulta para `ADMINISTRADOR`, `PRODUTOR` e `VENDEDOR`.
- Retornar registros em `created_at ASC`.
- Retornar `404` para pedido inexistente.

---

## File Structure

### Criar

- `backend/app/modules/orders/order_status_history_model.py`
- `backend/app/modules/orders/order_status_history_repository.py`
- `backend/app/modules/orders/order_status_history_schemas.py`
- `backend/alembic/versions/0010_create_order_status_history.py`
- `backend/tests/test_order_status_history_model.py`
- `backend/tests/test_order_status_history_repository.py`
- `backend/tests/test_order_status_history_creation.py`
- `backend/tests/test_order_status_history_transitions.py`
- `backend/tests/test_order_status_history_api.py`

### Modificar

- `backend/app/api/dependencies.py`
- `backend/app/api/routers/orders.py`
- `backend/app/modules/orders/order_service.py`
- `backend/app/modules/orders/order_confirmation_service.py`
- `backend/app/modules/orders/order_cancellation_service.py`
- `backend/app/modules/orders/order_completion_service.py`
- `backend/app/modules/orders/order_model.py`
- `backend/app/modules/users/model.py`

---

### Task 1: Modelo e migration

**Files:**
- Create: `backend/app/modules/orders/order_status_history_model.py`
- Create: `backend/alembic/versions/0010_create_order_status_history.py`
- Modify: `backend/app/modules/orders/order_model.py`
- Modify: `backend/app/modules/users/model.py`
- Test: `backend/tests/test_order_status_history_model.py`

**Interfaces:**
- Produces: `OrderStatusHistory`.

- [ ] Criar o teste do modelo.
- [ ] Rodar e confirmar `ModuleNotFoundError`.
- [ ] Criar o modelo com `id`, `order_id`, `previous_status`, `new_status`, `changed_by_user_id` e `created_at`.
- [ ] Adicionar os relacionamentos em `Order` e `User`.
- [ ] Criar a migration `0010`.
- [ ] Rodar o teste e confirmar `1 passed`.
- [ ] Commit: `feat: adiciona modelo de historico de status`.

### Modelo esperado

```python
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.modules.orders.order_model import OrderStatus


class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    order_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    previous_status: Mapped[OrderStatus | None] = mapped_column(
        Enum(
            OrderStatus,
            name="order_status_history_previous_status",
        ),
        nullable=True,
    )
    new_status: Mapped[OrderStatus] = mapped_column(
        Enum(
            OrderStatus,
            name="order_status_history_new_status",
        ),
        nullable=False,
    )
    changed_by_user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    order = relationship("Order", back_populates="status_history")
    changed_by_user = relationship(
        "User",
        back_populates="order_status_changes",
    )
```

---

### Task 2: Repository e schemas

**Files:**
- Create: `backend/app/modules/orders/order_status_history_repository.py`
- Create: `backend/app/modules/orders/order_status_history_schemas.py`
- Test: `backend/tests/test_order_status_history_repository.py`

**Interfaces:**
- `add(history: OrderStatusHistory) -> None`
- `list_by_order(order_id: UUID) -> list[OrderStatusHistory]`
- `OrderStatusHistoryRead`

- [ ] Criar o teste do repository.
- [ ] Rodar e confirmar falha.
- [ ] Implementar `add`.
- [ ] Implementar `list_by_order` com `created_at ASC`.
- [ ] Criar `OrderStatusHistoryRead`.
- [ ] Rodar teste e confirmar `1 passed`.
- [ ] Commit: `feat: adiciona repository do historico de status`.

```python
class OrderStatusHistoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def add(self, history: OrderStatusHistory) -> None:
        self.session.add(history)

    async def list_by_order(
        self,
        order_id: UUID,
    ) -> list[OrderStatusHistory]:
        statement = (
            select(OrderStatusHistory)
            .where(OrderStatusHistory.order_id == order_id)
            .order_by(OrderStatusHistory.created_at.asc())
        )

        result = await self.session.scalars(statement)
        return list(result.all())
```

---

### Task 3: Dependência do repository

**Files:**
- Modify: `backend/app/api/dependencies.py`

- [ ] Importar `OrderStatusHistoryRepository`.
- [ ] Criar `get_order_status_history_repository`.
- [ ] Validar com `python -m py_compile app\api\dependencies.py`.
- [ ] Commit: `feat: adiciona dependencia do historico de status`.

```python
def get_order_status_history_repository(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> OrderStatusHistoryRepository:
    return OrderStatusHistoryRepository(session)
```

---

### Task 4: Registrar criação

**Files:**
- Modify: `backend/app/modules/orders/order_service.py`
- Modify: `backend/app/api/routers/orders.py`
- Test: `backend/tests/test_order_status_history_creation.py`

- [ ] Criar teste para `null -> DRAFT`.
- [ ] Confirmar que falha.
- [ ] Injetar `history_repository` no `OrderService`.
- [ ] Criar `OrderStatusHistory` usando `seller_id`.
- [ ] Manter o histórico no mesmo commit da criação.
- [ ] Atualizar dependências no router.
- [ ] Rodar testes de pedidos.
- [ ] Commit: `feat: registra criacao do pedido no historico`.

```python
history = OrderStatusHistory(
    order=order,
    previous_status=None,
    new_status=OrderStatus.DRAFT,
    changed_by_user_id=seller_id,
)

self.history_repository.add(history)
```

---

### Task 5: Registrar confirmação

**Files:**
- Modify: `backend/app/modules/orders/order_confirmation_service.py`
- Modify: `backend/app/api/routers/orders.py`
- Test: `backend/tests/test_order_status_history_transitions.py`
- Test: `backend/tests/test_order_confirmation_service.py`

- [ ] Criar teste `DRAFT -> CONFIRMED`.
- [ ] Confirmar falha.
- [ ] Injetar `history_repository`.
- [ ] Alterar assinatura para `confirm(order_id, changed_by_user_id)`.
- [ ] Salvar `previous_status` antes da mudança.
- [ ] Criar o histórico antes do commit.
- [ ] Passar `current_user.id` no endpoint.
- [ ] Rodar testes.
- [ ] Commit: `feat: registra confirmacao no historico`.

---

### Task 6: Registrar cancelamento

**Files:**
- Modify: `backend/app/modules/orders/order_cancellation_service.py`
- Modify: `backend/app/api/routers/orders.py`
- Test: `backend/tests/test_order_status_history_transitions.py`
- Test: `backend/tests/test_order_cancellation_service.py`

- [ ] Criar testes `DRAFT -> CANCELLED` e `CONFIRMED -> CANCELLED`.
- [ ] Confirmar falha.
- [ ] Injetar `history_repository`.
- [ ] Alterar assinatura para `cancel(order_id, changed_by_user_id)`.
- [ ] Gravar histórico antes do commit.
- [ ] Passar `current_user.id` no endpoint.
- [ ] Rodar testes.
- [ ] Commit: `feat: registra cancelamento no historico`.

---

### Task 7: Registrar conclusão

**Files:**
- Modify: `backend/app/modules/orders/order_completion_service.py`
- Modify: `backend/app/api/routers/orders.py`
- Test: `backend/tests/test_order_status_history_transitions.py`
- Test: `backend/tests/test_order_completion_service.py`

- [ ] Criar teste `CONFIRMED -> COMPLETED`.
- [ ] Confirmar falha.
- [ ] Injetar `history_repository`.
- [ ] Alterar assinatura para `complete(order_id, changed_by_user_id)`.
- [ ] Gravar histórico antes do commit.
- [ ] Passar `current_user.id` no endpoint.
- [ ] Rodar testes.
- [ ] Commit: `feat: registra conclusao no historico`.

---

### Task 8: Endpoint de consulta

**Files:**
- Modify: `backend/app/api/routers/orders.py`
- Test: `backend/tests/test_order_status_history_api.py`

**Interfaces:**
- Produces: `GET /api/v1/orders/{order_id}/history`

- [ ] Criar o arquivo de teste com o comando:

```powershell
cd "C:\Projetosgrosalesackend"

New-Item -ItemType File -Force `
  "tests	est_order_status_history_api.py"
```

- [ ] Testar `200`, ordenação cronológica e `404`.
- [ ] Confirmar falha `404` por rota inexistente.
- [ ] Implementar a rota.
- [ ] Testar acesso para `ADMINISTRADOR`, `PRODUTOR` e `VENDEDOR`.
- [ ] Rodar todos os testes do endpoint.
- [ ] Commit: `feat: adiciona consulta do historico de status`.

```python
@router.get(
    "/{order_id}/history",
    response_model=list[OrderStatusHistoryRead],
)
async def list_order_status_history(
    order_id: UUID,
    order_repository: Annotated[
        OrderRepository,
        Depends(get_order_repository),
    ],
    history_repository: Annotated[
        OrderStatusHistoryRepository,
        Depends(get_order_status_history_repository),
    ],
    _: Annotated[
        User,
        Depends(
            require_roles(
                UserRole.ADMINISTRADOR,
                UserRole.PRODUTOR,
                UserRole.VENDEDOR,
            )
        ),
    ],
) -> list[OrderStatusHistory]:
    order = await order_repository.get_by_id(order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido não encontrado",
        )

    return await history_repository.list_by_order(order_id)
```

---

### Task 9: Verificação final

- [ ] No **PC principal**, rodar:

```powershell
cd "C:\Projetosgrosalesackend"
python -m pytest -v
```

- [ ] No **notebook com Docker**, rodar:

```powershell
cd "\192.168.100.37\Projetosgrosales"

docker compose up -d --build api
docker compose exec api alembic upgrade head
docker compose exec api alembic current
docker compose logs api --tail 50
```

- [ ] Confirmar `0010 (head)`.
- [ ] Testar no Swagger:

```text
POST /api/v1/orders
POST /api/v1/orders/{order_id}/items
POST /api/v1/orders/{order_id}/confirm
POST /api/v1/orders/{order_id}/complete
GET  /api/v1/orders/{order_id}/history
```

- [ ] Confirmar:

```text
null -> DRAFT
DRAFT -> CONFIRMED
CONFIRMED -> COMPLETED
```

- [ ] Conferir no banco:

```powershell
docker compose exec db psql -U agrosales -d agrosales -c "
SELECT
    order_id,
    previous_status,
    new_status,
    changed_by_user_id,
    created_at
FROM order_status_history
ORDER BY created_at ASC;
"
```

- [ ] Commit final:

```powershell
cd "C:\Projetosgrosales"

git status
git add .
git commit -m "feat: adiciona historico de status dos pedidos"
git push
```
