from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.modules.inventory.reservation_model import (
    ReservationStatus,
    StockReservation,
)
from app.modules.inventory.reservation_schemas import (
    StockReservationAllocationRead,
    StockReservationCreate,
    StockReservationRequest,
    StockReservationSummaryRead,
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


def test_stock_reservation_accepts_optional_order_item_id() -> None:
    reservation = StockReservation(
        id=uuid4(),
        lot_id=uuid4(),
        order_item_id=uuid4(),
        quantity=Decimal("10"),
        status=ReservationStatus.ACTIVE,
    )

    assert reservation.order_item_id is not None


def test_stock_reservation_allows_manual_reservation_without_order() -> None:
    reservation = StockReservation(
        id=uuid4(),
        lot_id=uuid4(),
        order_item_id=None,
        quantity=Decimal("10"),
        status=ReservationStatus.ACTIVE,
    )

    assert reservation.order_item_id is None