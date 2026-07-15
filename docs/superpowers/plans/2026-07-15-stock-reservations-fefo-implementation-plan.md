# Reserva FEFO Persistente Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar `POST /api/v1/stock-reservations`, aplicando FEFO, atualizando `reserved_quantity` e persistindo uma reserva por lote em uma única transação.

**Architecture:** O repository busca lotes elegíveis com bloqueio de linha e adiciona reservas à sessão sem executar commit. O application service valida a variação, aplica FEFO, atualiza os lotes, cria as reservas e controla commit/rollback. O router trata autorização, entrada e conversão de erros para HTTP.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy Async, PostgreSQL 17, Pydantic, Pytest, Docker Compose.

## Global Constraints

- Endpoint: `POST /api/v1/stock-reservations`.
- Apenas `ADMINISTRADOR` e `PRODUTOR` podem criar reservas.
- `VENDEDOR` recebe `403 Forbidden`.
- Quantidade deve ser maior que zero.
- Variação inexistente ou inativa retorna `404`.
- Estoque insuficiente retorna `422`.
- Lotes vencidos, inativos, esgotados ou sem saldo são ignorados.
- Ordenação FEFO: vencimento, data de produção e código.
- Cada lote utilizado gera uma linha em `stock_reservations`.
- `reserved_quantity` e reservas são persistidos em uma única transação.
- Falhas executam rollback e não deixam alterações parciais.
- A busca de lotes usa bloqueio de linha no PostgreSQL.

---

## File Structure

### Novos arquivos

- `backend/app/modules/inventory/reservation_repository.py`: busca e bloqueia lotes; adiciona reservas à sessão.
- `backend/app/modules/inventory/reservation_application_service.py`: coordena validação, FEFO, persistência e transação.
- `backend/app/api/routers/stock_reservations.py`: expõe o endpoint HTTP.
- `backend/tests/test_stock_reservations_api.py`: testa contrato, permissões e respostas.
- `backend/tests/test_reservation_application_service.py`: testa regra e transação.

### Arquivos modificados

- `backend/app/modules/inventory/reservation_schemas.py`: schemas de entrada, alocação e resposta.
- `backend/app/api/dependencies.py`: factories dos repositories.
- `backend/app/main.py`: registro do router.

---

### Task 1: Schemas da API

**Files:**
- Modify: `backend/app/modules/inventory/reservation_schemas.py`
- Test: `backend/tests/test_stock_reservations.py`

**Interfaces:**
- Produces:
  - `StockReservationRequest`
  - `StockReservationAllocationRead`
  - `StockReservationSummaryRead`

- [ ] **Step 1: Escrever os testes dos schemas**

Adicionar em `backend/tests/test_stock_reservations.py`:

```python
from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.modules.inventory.reservation_schemas import (
    StockReservationAllocationRead,
    StockReservationRequest,
    StockReservationSummaryRead,
)


def test_stock_reservation_request_accepts_positive_quantity() -> None:
    payload = StockReservationRequest(
        product_variation_id=uuid4(),
        quantity=Decimal("50"),
    )

    assert payload.quantity == Decimal("50")


def test_stock_reservation_request_rejects_zero_quantity() -> None:
    with pytest.raises(ValidationError):
        StockReservationRequest(
            product_variation_id=uuid4(),
            quantity=Decimal("0"),
        )


def test_stock_reservation_summary_contains_allocations() -> None:
    variation_id = uuid4()
    reservation_id = uuid4()
    lot_id = uuid4()

    response = StockReservationSummaryRead(
        product_variation_id=variation_id,
        requested_quantity=Decimal("50"),
        reserved_quantity=Decimal("50"),
        allocations=[
            StockReservationAllocationRead(
                reservation_id=reservation_id,
                lot_id=lot_id,
                lot_code="LOTE-001",
                quantity=Decimal("50"),
                expiration_date=date(2026, 7, 20),
            )
        ],
    )

    assert response.allocations[0].reservation_id == reservation_id
    assert response.reserved_quantity == Decimal("50")
```

- [ ] **Step 2: Rodar os testes e verificar falha**

No PC principal:

```powershell
cd "C:\Projetos\agrosales\backend"
python -m pytest tests\test_stock_reservations.py -v
```

Esperado: falha de importação porque os novos schemas ainda não existem.

- [ ] **Step 3: Implementar os schemas**

Substituir `backend/app/modules/inventory/reservation_schemas.py` por:

```python
from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.inventory.reservation_model import ReservationStatus


class StockReservationCreate(BaseModel):
    lot_id: UUID
    quantity: Decimal = Field(gt=0)


class StockReservationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    lot_id: UUID
    quantity: Decimal
    status: ReservationStatus


class StockReservationRequest(BaseModel):
    product_variation_id: UUID
    quantity: Decimal = Field(gt=0)


class StockReservationAllocationRead(BaseModel):
    reservation_id: UUID
    lot_id: UUID
    lot_code: str
    quantity: Decimal
    expiration_date: date


class StockReservationSummaryRead(BaseModel):
    product_variation_id: UUID
    requested_quantity: Decimal
    reserved_quantity: Decimal
    allocations: list[StockReservationAllocationRead]
```

- [ ] **Step 4: Rodar os testes**

```powershell
python -m pytest tests\test_stock_reservations.py -v
```

Esperado: todos os testes do arquivo passando.

- [ ] **Step 5: Commit**

```powershell
cd "C:\Projetos\agrosales"
git add backend\app\modules\inventory\reservation_schemas.py backend\tests\test_stock_reservations.py
git commit -m "feat: adiciona schemas da reserva FEFO"
```

---

### Task 2: Repository de reservas e lotes elegíveis

**Files:**
- Create: `backend/app/modules/inventory/reservation_repository.py`
- Test: `backend/tests/test_reservation_repository.py`

**Interfaces:**
- Produces:
  - `ReservationRepository(session: AsyncSession)`
  - `get_eligible_lots(product_variation_id: UUID, reference_date: date) -> list[Lot]`
  - `add(reservation: StockReservation) -> None`

- [ ] **Step 1: Criar teste do repository**

Criar `backend/tests/test_reservation_repository.py`:

```python
from datetime import date
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.modules.inventory.reservation_repository import (
    ReservationRepository,
)


@pytest.mark.asyncio
async def test_repository_returns_scalar_lots() -> None:
    session = MagicMock()
    scalars_result = MagicMock()
    scalars_result.all.return_value = ["lot-1", "lot-2"]
    session.scalars = AsyncMock(return_value=scalars_result)

    repository = ReservationRepository(session)

    result = await repository.get_eligible_lots(
        product_variation_id=uuid4(),
        reference_date=date(2026, 7, 15),
    )

    assert result == ["lot-1", "lot-2"]
    session.scalars.assert_awaited_once()


def test_repository_adds_reservation_to_session() -> None:
    session = MagicMock()
    repository = ReservationRepository(session)
    reservation = MagicMock()

    repository.add(reservation)

    session.add.assert_called_once_with(reservation)
```

- [ ] **Step 2: Rodar e confirmar falha**

```powershell
cd "C:\Projetos\agrosales\backend"
python -m pytest tests\test_reservation_repository.py -v
```

Esperado: erro de importação.

- [ ] **Step 3: Implementar o repository**

Criar `backend/app/modules/inventory/reservation_repository.py`:

```python
from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.lot_model import Lot
from app.modules.inventory.reservation_model import StockReservation


class ReservationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_eligible_lots(
        self,
        product_variation_id: UUID,
        reference_date: date,
    ) -> list[Lot]:
        statement = (
            select(Lot)
            .where(
                Lot.product_variation_id == product_variation_id,
                Lot.expiration_date >= reference_date,
                Lot.status.in_(("ACTIVE", "NEAR_EXPIRATION")),
                Lot.physical_quantity > Lot.reserved_quantity,
            )
            .order_by(
                Lot.expiration_date.asc(),
                Lot.production_date.asc(),
                Lot.code.asc(),
            )
            .with_for_update()
        )

        result = await self.session.scalars(statement)
        return list(result.all())

    def add(self, reservation: StockReservation) -> None:
        self.session.add(reservation)
```

- [ ] **Step 4: Rodar testes**

```powershell
python -m pytest tests\test_reservation_repository.py -v
```

Esperado: 2 testes passando.

- [ ] **Step 5: Commit**

```powershell
cd "C:\Projetos\agrosales"
git add backend\app\modules\inventory\reservation_repository.py backend\tests\test_reservation_repository.py
git commit -m "feat: adiciona repository de reservas"
```

---

### Task 3: Application service transacional

**Files:**
- Create: `backend/app/modules/inventory/reservation_application_service.py`
- Test: `backend/tests/test_reservation_application_service.py`

**Interfaces:**
- Consumes:
  - `ReservationRepository`
  - `ProductVariationRepository`
  - `FefoReservationService`
- Produces:
  - `ProductVariationNotFoundError`
  - `ReservationApplicationService.create(data: StockReservationRequest) -> StockReservationSummaryRead`

- [ ] **Step 1: Criar testes do service**

Criar `backend/tests/test_reservation_application_service.py`:

```python
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.modules.inventory.lot_model import Lot
from app.modules.inventory.reservation_application_service import (
    ProductVariationNotFoundError,
    ReservationApplicationService,
)
from app.modules.inventory.reservation_service import (
    InsufficientAvailableStockError,
)
from app.modules.inventory.reservation_schemas import (
    StockReservationRequest,
)
from app.modules.products.variation_model import ProductVariation


def make_lot(
    code: str,
    expiration_date: date,
    quantity: str,
) -> Lot:
    return Lot(
        id=uuid4(),
        product_variation_id=uuid4(),
        code=code,
        production_date=date(2026, 7, 1),
        expiration_date=expiration_date,
        physical_quantity=Decimal(quantity),
        reserved_quantity=Decimal("0"),
        status="ACTIVE",
    )


@pytest.mark.asyncio
async def test_service_creates_split_fefo_reservation() -> None:
    variation_id = uuid4()
    variation = ProductVariation(
        id=variation_id,
        product_id=uuid4(),
        internal_code="TOM-ITA-20-A",
        package_type="Caixa",
        unit_of_measure="CAIXA",
        standard_price=Decimal("160"),
        minimum_price=Decimal("145"),
        is_active=True,
    )

    first_lot = make_lot("LOTE-001", date(2026, 7, 20), "30")
    second_lot = make_lot("LOTE-002", date(2026, 7, 30), "80")
    first_lot.product_variation_id = variation_id
    second_lot.product_variation_id = variation_id

    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock(
        side_effect=lambda reservation: setattr(
            reservation,
            "id",
            uuid4(),
        )
    )

    reservation_repository = MagicMock()
    reservation_repository.get_eligible_lots = AsyncMock(
        return_value=[first_lot, second_lot]
    )

    variation_repository = MagicMock()
    variation_repository.get_by_id = AsyncMock(return_value=variation)

    service = ReservationApplicationService(
        session=session,
        reservation_repository=reservation_repository,
        variation_repository=variation_repository,
    )

    result = await service.create(
        StockReservationRequest(
            product_variation_id=variation_id,
            quantity=Decimal("50"),
        ),
        reference_date=date(2026, 7, 15),
    )

    assert result.reserved_quantity == Decimal("50")
    assert [item.quantity for item in result.allocations] == [
        Decimal("30"),
        Decimal("20"),
    ]
    assert first_lot.reserved_quantity == Decimal("30")
    assert second_lot.reserved_quantity == Decimal("20")
    assert reservation_repository.add.call_count == 2
    session.commit.assert_awaited_once()
    session.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_service_rolls_back_when_stock_is_insufficient() -> None:
    variation_id = uuid4()
    variation = MagicMock(is_active=True)

    lot = make_lot("LOTE-001", date(2026, 7, 20), "10")
    lot.product_variation_id = variation_id

    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    reservation_repository = MagicMock()
    reservation_repository.get_eligible_lots = AsyncMock(
        return_value=[lot]
    )

    variation_repository = MagicMock()
    variation_repository.get_by_id = AsyncMock(return_value=variation)

    service = ReservationApplicationService(
        session=session,
        reservation_repository=reservation_repository,
        variation_repository=variation_repository,
    )

    with pytest.raises(InsufficientAvailableStockError):
        await service.create(
            StockReservationRequest(
                product_variation_id=variation_id,
                quantity=Decimal("50"),
            ),
            reference_date=date(2026, 7, 15),
        )

    assert lot.reserved_quantity == Decimal("0")
    session.commit.assert_not_awaited()
    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_service_rejects_inactive_variation() -> None:
    session = MagicMock()
    session.rollback = AsyncMock()

    variation_repository = MagicMock()
    variation_repository.get_by_id = AsyncMock(
        return_value=MagicMock(is_active=False)
    )

    service = ReservationApplicationService(
        session=session,
        reservation_repository=MagicMock(),
        variation_repository=variation_repository,
    )

    with pytest.raises(ProductVariationNotFoundError):
        await service.create(
            StockReservationRequest(
                product_variation_id=uuid4(),
                quantity=Decimal("10"),
            )
        )

    session.rollback.assert_awaited_once()
```

- [ ] **Step 2: Rodar e confirmar falha**

```powershell
cd "C:\Projetos\agrosales\backend"
python -m pytest tests\test_reservation_application_service.py -v
```

Esperado: erro de importação.

- [ ] **Step 3: Implementar o application service**

Criar `backend/app/modules/inventory/reservation_application_service.py`:

```python
from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.reservation_model import (
    ReservationStatus,
    StockReservation,
)
from app.modules.inventory.reservation_repository import (
    ReservationRepository,
)
from app.modules.inventory.reservation_service import (
    FefoReservationService,
)
from app.modules.inventory.reservation_schemas import (
    StockReservationAllocationRead,
    StockReservationRequest,
    StockReservationSummaryRead,
)
from app.modules.products.variation_repository import (
    ProductVariationRepository,
)


class ProductVariationNotFoundError(Exception):
    pass


class ReservationApplicationService:
    def __init__(
        self,
        session: AsyncSession,
        reservation_repository: ReservationRepository,
        variation_repository: ProductVariationRepository,
    ) -> None:
        self.session = session
        self.reservation_repository = reservation_repository
        self.variation_repository = variation_repository
        self.fefo_service = FefoReservationService()

    async def create(
        self,
        data: StockReservationRequest,
        reference_date: date | None = None,
    ) -> StockReservationSummaryRead:
        try:
            variation = await self.variation_repository.get_by_id(
                data.product_variation_id
            )

            if variation is None or not variation.is_active:
                raise ProductVariationNotFoundError(
                    "Variação de produto não encontrada ou inativa"
                )

            today = reference_date or date.today()

            lots = await self.reservation_repository.get_eligible_lots(
                product_variation_id=data.product_variation_id,
                reference_date=today,
            )

            allocations = self.fefo_service.reserve(
                lots=lots,
                requested_quantity=data.quantity,
                today=today,
            )

            lots_by_id = {lot.id: lot for lot in lots}
            response_allocations: list[
                StockReservationAllocationRead
            ] = []

            reservations: list[tuple[StockReservation, object]] = []

            for allocation in allocations:
                lot = lots_by_id[allocation.lot_id]

                reservation = StockReservation(
                    lot_id=lot.id,
                    quantity=allocation.quantity,
                    status=ReservationStatus.ACTIVE,
                )

                self.reservation_repository.add(reservation)
                reservations.append((reservation, lot))

            await self.session.commit()

            for reservation, _ in reservations:
                await self.session.refresh(reservation)

            for reservation, lot in reservations:
                response_allocations.append(
                    StockReservationAllocationRead(
                        reservation_id=reservation.id,
                        lot_id=lot.id,
                        lot_code=lot.code,
                        quantity=reservation.quantity,
                        expiration_date=lot.expiration_date,
                    )
                )

            return StockReservationSummaryRead(
                product_variation_id=data.product_variation_id,
                requested_quantity=data.quantity,
                reserved_quantity=sum(
                    (
                        item.quantity
                        for item in response_allocations
                    ),
                    start=Decimal("0"),
                ),
                allocations=response_allocations,
            )

        except Exception:
            await self.session.rollback()
            raise
```

- [ ] **Step 4: Rodar testes**

```powershell
python -m pytest tests\test_reservation_application_service.py -v
```

Esperado: 3 testes passando.

- [ ] **Step 5: Commit**

```powershell
cd "C:\Projetos\agrosales"
git add backend\app\modules\inventory\reservation_application_service.py backend\tests\test_reservation_application_service.py
git commit -m "feat: adiciona servico transacional de reservas"
```

---

### Task 4: Dependências e router da API

**Files:**
- Modify: `backend/app/api/dependencies.py`
- Create: `backend/app/api/routers/stock_reservations.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_stock_reservations_api.py`

**Interfaces:**
- Produces:
  - `get_reservation_repository`
  - `POST /api/v1/stock-reservations`

- [ ] **Step 1: Criar testes da API**

Criar `backend/tests/test_stock_reservations_api.py`:

```python
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.api.dependencies import (
    get_current_user,
    get_product_variation_repository,
    get_reservation_repository,
)
from app.core.enums import UserRole
from app.database.session import get_db_session
from app.main import app
from app.modules.users.model import User


def make_user(role: UserRole) -> User:
    return User(
        id=uuid4(),
        name="Usuário",
        email=f"{role.value.lower()}@agrosales.com",
        password_hash="hash",
        role=role,
        is_active=True,
    )


def test_vendor_cannot_create_stock_reservation(client) -> None:
    app.dependency_overrides[get_current_user] = lambda: make_user(
        UserRole.VENDEDOR
    )

    response = client.post(
        "/api/v1/stock-reservations",
        json={
            "product_variation_id": str(uuid4()),
            "quantity": "50",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 403


def test_rejects_zero_stock_reservation_quantity(client) -> None:
    app.dependency_overrides[get_current_user] = lambda: make_user(
        UserRole.PRODUTOR
    )

    response = client.post(
        "/api/v1/stock-reservations",
        json={
            "product_variation_id": str(uuid4()),
            "quantity": "0",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 422
```

- [ ] **Step 2: Rodar e confirmar falha**

```powershell
cd "C:\Projetos\agrosales\backend"
python -m pytest tests\test_stock_reservations_api.py -v
```

Esperado: erro de importação ou rota não encontrada.

- [ ] **Step 3: Adicionar dependência**

Em `backend/app/api/dependencies.py`, adicionar:

```python
from app.modules.inventory.reservation_repository import (
    ReservationRepository,
)
```

E:

```python
def get_reservation_repository(
    session: SessionDependency,
) -> ReservationRepository:
    return ReservationRepository(session)
```

- [ ] **Step 4: Criar router**

Criar `backend/app/api/routers/stock_reservations.py`:

```python
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import (
    get_product_variation_repository,
    get_reservation_repository,
    require_roles,
)
from app.core.enums import UserRole
from app.database.session import get_db_session
from app.modules.inventory.reservation_application_service import (
    ProductVariationNotFoundError,
    ReservationApplicationService,
)
from app.modules.inventory.reservation_repository import (
    ReservationRepository,
)
from app.modules.inventory.reservation_service import (
    InsufficientAvailableStockError,
)
from app.modules.inventory.reservation_schemas import (
    StockReservationRequest,
    StockReservationSummaryRead,
)
from app.modules.products.variation_repository import (
    ProductVariationRepository,
)
from app.modules.users.model import User

router = APIRouter(
    prefix="/stock-reservations",
    tags=["Reservas de estoque"],
)


@router.post(
    "",
    response_model=StockReservationSummaryRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_stock_reservation(
    data: StockReservationRequest,
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
    reservation_repository: Annotated[
        ReservationRepository,
        Depends(get_reservation_repository),
    ],
    variation_repository: Annotated[
        ProductVariationRepository,
        Depends(get_product_variation_repository),
    ],
    _: Annotated[
        User,
        Depends(
            require_roles(
                UserRole.ADMINISTRADOR,
                UserRole.PRODUTOR,
            )
        ),
    ],
) -> StockReservationSummaryRead:
    service = ReservationApplicationService(
        session=session,
        reservation_repository=reservation_repository,
        variation_repository=variation_repository,
    )

    try:
        return await service.create(data)

    except ProductVariationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except InsufficientAvailableStockError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error
```

- [ ] **Step 5: Registrar router no main**

Em `backend/app/main.py`, adicionar:

```python
from app.api.routers.stock_reservations import (
    router as stock_reservations_router,
)
```

E:

```python
app.include_router(
    stock_reservations_router,
    prefix=settings.api_v1_prefix,
)
```

- [ ] **Step 6: Rodar testes da API**

```powershell
python -m pytest tests\test_stock_reservations_api.py -v
```

Esperado: 2 testes passando.

- [ ] **Step 7: Commit**

```powershell
cd "C:\Projetos\agrosales"
git add backend\app\api\dependencies.py backend\app\api\routers\stock_reservations.py backend\app\main.py backend\tests\test_stock_reservations_api.py
git commit -m "feat: adiciona endpoint de reservas FEFO"
```

---

### Task 5: Verificação completa e Docker

**Files:**
- Verify: todos os arquivos da funcionalidade.

- [ ] **Step 1: Rodar toda a suíte**

No PC principal:

```powershell
cd "C:\Projetos\agrosales\backend"
python -m pytest -v
```

Esperado: todos os testes passando.

- [ ] **Step 2: Rebuild da API**

No notebook com Docker:

```powershell
cd "\\192.168.100.37\Projetos\agrosales"
docker compose up -d --build api
docker compose logs api --tail 50
```

Esperado: API iniciada sem traceback.

- [ ] **Step 3: Validar no Swagger**

No PC principal, abrir:

```text
http://192.168.100.30:8000/docs
```

Testar:

```json
{
  "product_variation_id": "UUID-REAL",
  "quantity": 50
}
```

Esperado: `201 Created`, com `reserved_quantity` igual à quantidade solicitada e uma ou mais alocações.

- [ ] **Step 4: Conferir banco**

No notebook com Docker:

```powershell
docker compose exec db psql -U agrosales -d agrosales -c "SELECT id, lot_id, quantity, status FROM stock_reservations ORDER BY created_at DESC;"
```

E:

```powershell
docker compose exec db psql -U agrosales -d agrosales -c "SELECT id, code, physical_quantity, reserved_quantity FROM lots ORDER BY expiration_date;"
```

Esperado: reservas persistidas e `reserved_quantity` atualizado.

- [ ] **Step 5: Push final**

No PC principal:

```powershell
cd "C:\Projetos\agrosales"
git push
```
