from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.modules.inventory.reservation_model import (
    ReservationStatus,
    StockReservation,
)
from app.modules.inventory.reservation_schemas import (
    StockReservationCreate,
)


def test_stock_reservation_table_name() -> None:
    assert StockReservation.__tablename__ == "stock_reservations"


def test_reservation_status_values_are_correct() -> None:
    assert {status.value for status in ReservationStatus} == {
        "ACTIVE",
        "RELEASED",
        "CONSUMED",
        "CANCELLED",
    }


def test_stock_reservation_accepts_positive_quantity() -> None:
    reservation = StockReservationCreate(
        lot_id=uuid4(),
        quantity=Decimal("25"),
    )

    assert reservation.quantity == Decimal("25")


def test_stock_reservation_rejects_zero_quantity() -> None:
    with pytest.raises(ValidationError):
        StockReservationCreate(
            lot_id=uuid4(),
            quantity=Decimal("0"),
        )