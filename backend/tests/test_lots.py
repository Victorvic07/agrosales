from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.modules.inventory.lot_model import Lot
from app.modules.inventory.lot_schemas import LotCreate


def test_lot_table_name() -> None:
    assert Lot.__tablename__ == "lots"


def test_lot_available_quantity() -> None:
    lot = Lot(
        product_variation_id=uuid4(),
        code="LOTE-001",
        production_date=date(2026, 7, 10),
        expiration_date=date(2026, 7, 20),
        physical_quantity=Decimal("100"),
        reserved_quantity=Decimal("30"),
    )

    assert lot.available_quantity == Decimal("70")


def test_lot_rejects_expiration_before_production() -> None:
    with pytest.raises(ValidationError):
        LotCreate(
            product_variation_id=uuid4(),
            code="LOTE-001",
            production_date=date(2026, 7, 20),
            expiration_date=date(2026, 7, 10),
            physical_quantity=Decimal("100"),
        )


def test_lot_rejects_reserved_quantity_above_physical() -> None:
    with pytest.raises(ValidationError):
        LotCreate(
            product_variation_id=uuid4(),
            code="LOTE-001",
            production_date=date(2026, 7, 10),
            expiration_date=date(2026, 7, 20),
            physical_quantity=Decimal("100"),
            reserved_quantity=Decimal("120"),
        )