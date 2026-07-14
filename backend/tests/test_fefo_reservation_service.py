from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from app.modules.inventory.lot_model import Lot
from app.modules.inventory.reservation_service import (
    FefoReservationService,
    InsufficientAvailableStockError,
)


def create_lot(
    code: str,
    expiration_date: date,
    physical_quantity: Decimal,
    reserved_quantity: Decimal = Decimal("0"),
    status: str = "ACTIVE",
) -> Lot:
    return Lot(
        id=uuid4(),
        product_variation_id=uuid4(),
        code=code,
        production_date=date(2026, 7, 1),
        expiration_date=expiration_date,
        physical_quantity=physical_quantity,
        reserved_quantity=reserved_quantity,
        status=status,
    )


def test_fefo_reserves_lot_that_expires_first() -> None:
    first_lot = create_lot(
        code="LOTE-001",
        expiration_date=date(2026, 7, 20),
        physical_quantity=Decimal("40"),
    )

    second_lot = create_lot(
        code="LOTE-002",
        expiration_date=date(2026, 7, 30),
        physical_quantity=Decimal("100"),
    )

    service = FefoReservationService()

    allocations = service.reserve(
        lots=[second_lot, first_lot],
        requested_quantity=Decimal("30"),
        today=date(2026, 7, 14),
    )

    assert len(allocations) == 1
    assert allocations[0].lot_id == first_lot.id
    assert allocations[0].quantity == Decimal("30")
    assert first_lot.reserved_quantity == Decimal("30")
    assert second_lot.reserved_quantity == Decimal("0")


def test_fefo_can_split_reservation_between_lots() -> None:
    first_lot = create_lot(
        code="LOTE-001",
        expiration_date=date(2026, 7, 20),
        physical_quantity=Decimal("30"),
    )

    second_lot = create_lot(
        code="LOTE-002",
        expiration_date=date(2026, 7, 30),
        physical_quantity=Decimal("80"),
    )

    service = FefoReservationService()

    allocations = service.reserve(
        lots=[first_lot, second_lot],
        requested_quantity=Decimal("50"),
        today=date(2026, 7, 14),
    )

    assert len(allocations) == 2
    assert allocations[0].quantity == Decimal("30")
    assert allocations[1].quantity == Decimal("20")
    assert first_lot.reserved_quantity == Decimal("30")
    assert second_lot.reserved_quantity == Decimal("20")


def test_fefo_ignores_expired_and_depleted_lots() -> None:
    expired_lot = create_lot(
        code="LOTE-VENCIDO",
        expiration_date=date(2026, 7, 10),
        physical_quantity=Decimal("100"),
    )

    depleted_lot = create_lot(
        code="LOTE-ESGOTADO",
        expiration_date=date(2026, 7, 20),
        physical_quantity=Decimal("100"),
        status="DEPLETED",
    )

    valid_lot = create_lot(
        code="LOTE-VALIDO",
        expiration_date=date(2026, 7, 25),
        physical_quantity=Decimal("50"),
    )

    service = FefoReservationService()

    allocations = service.reserve(
        lots=[expired_lot, depleted_lot, valid_lot],
        requested_quantity=Decimal("20"),
        today=date(2026, 7, 14),
    )

    assert allocations[0].lot_id == valid_lot.id
    assert expired_lot.reserved_quantity == Decimal("0")
    assert depleted_lot.reserved_quantity == Decimal("0")
    assert valid_lot.reserved_quantity == Decimal("20")


def test_fefo_does_not_change_lots_when_stock_is_insufficient() -> None:
    first_lot = create_lot(
        code="LOTE-001",
        expiration_date=date(2026, 7, 20),
        physical_quantity=Decimal("20"),
    )

    second_lot = create_lot(
        code="LOTE-002",
        expiration_date=date(2026, 7, 30),
        physical_quantity=Decimal("10"),
    )

    service = FefoReservationService()

    with pytest.raises(
        InsufficientAvailableStockError,
        match="Estoque disponível insuficiente",
    ):
        service.reserve(
            lots=[first_lot, second_lot],
            requested_quantity=Decimal("50"),
            today=date(2026, 7, 14),
        )

    assert first_lot.reserved_quantity == Decimal("0")
    assert second_lot.reserved_quantity == Decimal("0")