from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.modules.inventory.lot_model import ExpirationState, Lot, LotStatus
from app.modules.inventory.lot_schemas import (
    LotCreate,
    LotRead,
    LotStatusUpdate,
    LotUpdate,
)


def test_lot_table_name() -> None:
    assert Lot.__tablename__ == "lots"


def test_lot_status_has_only_active_and_inactive_values() -> None:
    assert list(LotStatus) == [LotStatus.ACTIVE, LotStatus.INACTIVE]


def test_lot_available_quantity() -> None:
    lot = Lot(
        product_variation_id=uuid4(),
        code="LOTE-001",
        production_date=date.today(),
        expiration_date=date.today() + timedelta(days=31),
        physical_quantity=Decimal("100"),
        reserved_quantity=Decimal("30"),
    )

    assert lot.available_quantity == Decimal("70")


@pytest.mark.parametrize(
    ("expiration_date", "expected_state"),
    [
        (date.today() - timedelta(days=1), ExpirationState.EXPIRED),
        (date.today(), ExpirationState.EXPIRES_TODAY),
        (date.today() + timedelta(days=30), ExpirationState.EXPIRING_SOON),
        (date.today() + timedelta(days=31), ExpirationState.REGULAR),
    ],
)
def test_lot_expiration_state(
    expiration_date: date,
    expected_state: ExpirationState,
) -> None:
    lot = Lot(
        product_variation_id=uuid4(),
        code="LOTE-001",
        production_date=date.today() - timedelta(days=1),
        expiration_date=expiration_date,
    )

    assert lot.expiration_state is expected_state


def test_lot_create_requires_reason_for_positive_initial_quantity() -> None:
    with pytest.raises(ValidationError, match="motivo"):
        LotCreate(
            product_variation_id=uuid4(),
            code="LOTE-001",
            production_date=date.today(),
            expiration_date=date.today() + timedelta(days=1),
            initial_quantity=Decimal("1"),
            initial_entry_reason="   ",
        )


def test_lot_create_allows_zero_initial_quantity_without_reason() -> None:
    lot = LotCreate(
        product_variation_id=uuid4(),
        code="LOTE-001",
        production_date=date.today(),
        expiration_date=date.today(),
    )

    assert lot.initial_quantity == Decimal("0")
    assert lot.initial_entry_reason is None


@pytest.mark.parametrize(
    ("production_date", "expiration_date"),
    [
        (date.today(), date.today() - timedelta(days=1)),
        (date.today() + timedelta(days=2), date.today() + timedelta(days=1)),
    ],
)
def test_lot_create_rejects_invalid_expiration_dates(
    production_date: date,
    expiration_date: date,
) -> None:
    with pytest.raises(ValidationError):
        LotCreate(
            product_variation_id=uuid4(),
            code="LOTE-001",
            production_date=production_date,
            expiration_date=expiration_date,
        )


@pytest.mark.parametrize(
    ("production_date", "expiration_date"),
    [
        (None, date.today() - timedelta(days=1)),
        (date.today() + timedelta(days=2), date.today() + timedelta(days=1)),
    ],
)
def test_lot_update_rejects_invalid_expiration_dates(
    production_date: date | None,
    expiration_date: date,
) -> None:
    with pytest.raises(ValidationError):
        LotUpdate(
            production_date=production_date,
            expiration_date=expiration_date,
        )


def test_lot_status_update_uses_lot_status() -> None:
    assert LotStatusUpdate(status="INACTIVE").status is LotStatus.INACTIVE


def test_lot_read_includes_persisted_and_calculated_fields() -> None:
    now = datetime.now(UTC)
    lot = Lot(
        id=uuid4(),
        product_variation_id=uuid4(),
        code="LOTE-001",
        production_date=date.today(),
        expiration_date=date.today() + timedelta(days=31),
        physical_quantity=Decimal("100"),
        reserved_quantity=Decimal("30"),
        status=LotStatus.ACTIVE,
        created_at=now,
        updated_at=now,
    )

    result = LotRead.model_validate(lot)

    assert result.available_quantity == Decimal("70")
    assert result.expiration_state is ExpirationState.REGULAR
    assert result.created_at == now
    assert result.updated_at == now
