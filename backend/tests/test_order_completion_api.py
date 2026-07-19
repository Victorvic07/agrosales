from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.api.dependencies import (
    get_current_user,
    get_order_repository,
    get_reservation_repository,
)
from app.core.enums import UserRole
from app.database.session import get_db_session
from app.main import app
from app.modules.inventory.lot_model import Lot
from app.modules.inventory.movement_model import (
    InventoryMovement,
    MovementType,
)
from app.modules.inventory.reservation_model import (
    ReservationStatus,
    StockReservation,
)
from app.modules.orders.order_model import Order, OrderStatus
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


def test_vendor_cannot_complete_order(client) -> None:
    app.dependency_overrides[get_current_user] = (
        lambda: make_user(UserRole.VENDEDOR)
    )

    try:
        response = client.post(
            f"/api/v1/orders/{uuid4()}/complete"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403


def test_returns_404_when_completing_unknown_order(client) -> None:
    order_repository = AsyncMock()
    order_repository.get_by_id_for_update.return_value = None

    reservation_repository = AsyncMock()

    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()

    async def override_session():
        yield session

    app.dependency_overrides[get_current_user] = (
        lambda: make_user(UserRole.PRODUTOR)
    )
    app.dependency_overrides[get_order_repository] = (
        lambda: order_repository
    )
    app.dependency_overrides[get_reservation_repository] = (
        lambda: reservation_repository
    )
    app.dependency_overrides[get_db_session] = override_session

    try:
        response = client.post(
            f"/api/v1/orders/{uuid4()}/complete"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Pedido não encontrado"

    reservation_repository.list_active_by_order.assert_not_awaited()
    session.commit.assert_not_awaited()
    session.rollback.assert_awaited_once()


def test_rejects_completion_of_unconfirmed_order(client) -> None:
    order_id = uuid4()

    order = Order(
        id=order_id,
        customer_id=uuid4(),
        seller_id=uuid4(),
        status=OrderStatus.DRAFT,
        subtotal=Decimal("100"),
        discount_total=Decimal("0"),
        total_amount=Decimal("100"),
    )

    order_repository = AsyncMock()
    order_repository.get_by_id_for_update.return_value = order

    reservation_repository = AsyncMock()

    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()

    async def override_session():
        yield session

    app.dependency_overrides[get_current_user] = (
        lambda: make_user(UserRole.ADMINISTRADOR)
    )
    app.dependency_overrides[get_order_repository] = (
        lambda: order_repository
    )
    app.dependency_overrides[get_reservation_repository] = (
        lambda: reservation_repository
    )
    app.dependency_overrides[get_db_session] = override_session

    try:
        response = client.post(
            f"/api/v1/orders/{order_id}/complete"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Apenas pedidos confirmados podem ser concluídos"
    )

    reservation_repository.list_active_by_order.assert_not_awaited()
    session.commit.assert_not_awaited()
    session.rollback.assert_awaited_once()


def test_returns_422_when_stock_balance_is_inconsistent(client) -> None:
    order_id = uuid4()

    order = Order(
        id=order_id,
        customer_id=uuid4(),
        seller_id=uuid4(),
        status=OrderStatus.CONFIRMED,
        subtotal=Decimal("100"),
        discount_total=Decimal("0"),
        total_amount=Decimal("100"),
    )

    lot = Lot(
        id=uuid4(),
        product_variation_id=uuid4(),
        code="LOTE-001",
        physical_quantity=Decimal("5"),
        reserved_quantity=Decimal("10"),
    )

    reservation = StockReservation(
        id=uuid4(),
        lot_id=lot.id,
        quantity=Decimal("10"),
        status=ReservationStatus.ACTIVE,
    )
    reservation.lot = lot

    order_repository = AsyncMock()
    order_repository.get_by_id_for_update.return_value = order

    reservation_repository = AsyncMock()
    reservation_repository.list_active_by_order.return_value = [
        reservation
    ]

    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()

    async def override_session():
        yield session

    app.dependency_overrides[get_current_user] = (
        lambda: make_user(UserRole.PRODUTOR)
    )
    app.dependency_overrides[get_order_repository] = (
        lambda: order_repository
    )
    app.dependency_overrides[get_reservation_repository] = (
        lambda: reservation_repository
    )
    app.dependency_overrides[get_db_session] = override_session

    try:
        response = client.post(
            f"/api/v1/orders/{order_id}/complete"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "Saldo de estoque do lote está inconsistente"
    )

    assert order.status == OrderStatus.CONFIRMED
    assert reservation.status == ReservationStatus.ACTIVE
    assert lot.physical_quantity == Decimal("5")
    assert lot.reserved_quantity == Decimal("10")

    session.commit.assert_not_awaited()
    session.rollback.assert_awaited_once()


def test_completes_confirmed_order_successfully(client) -> None:
    order_id = uuid4()
    now = datetime.now(UTC)
    current_user = make_user(UserRole.PRODUTOR)

    order = Order(
        id=order_id,
        customer_id=uuid4(),
        seller_id=uuid4(),
        status=OrderStatus.CONFIRMED,
        subtotal=Decimal("100"),
        discount_total=Decimal("0"),
        total_amount=Decimal("100"),
        created_at=now,
        updated_at=now,
    )

    lot = Lot(
        id=uuid4(),
        product_variation_id=uuid4(),
        code="LOTE-001",
        physical_quantity=Decimal("100"),
        reserved_quantity=Decimal("20"),
    )

    reservation = StockReservation(
        id=uuid4(),
        lot_id=lot.id,
        quantity=Decimal("10"),
        status=ReservationStatus.ACTIVE,
    )
    reservation.lot = lot

    order_repository = AsyncMock()
    order_repository.get_by_id_for_update.return_value = order

    reservation_repository = AsyncMock()
    reservation_repository.list_active_by_order.return_value = [
        reservation
    ]

    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()

    async def override_session():
        yield session

    app.dependency_overrides[get_current_user] = (
        lambda: current_user
    )
    app.dependency_overrides[get_order_repository] = (
        lambda: order_repository
    )
    app.dependency_overrides[get_reservation_repository] = (
        lambda: reservation_repository
    )
    app.dependency_overrides[get_db_session] = override_session

    try:
        response = client.post(
            f"/api/v1/orders/{order_id}/complete"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    assert order.status == OrderStatus.COMPLETED
    assert order.completed_at is not None

    assert reservation.status == ReservationStatus.CONSUMED

    assert lot.physical_quantity == Decimal("90")
    assert lot.reserved_quantity == Decimal("10")

    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(order)

    movements = [
        call.args[0]
        for call in session.add.call_args_list
        if isinstance(call.args[0], InventoryMovement)
    ]

    assert len(movements) == 1

    movement = movements[0]

    assert movement.lot_id == lot.id
    assert movement.user_id == current_user.id
    assert movement.movement_type is MovementType.SALE
    assert movement.quantity == reservation.quantity
    assert movement.previous_balance == Decimal("100")
    assert movement.new_balance == Decimal("90")
    assert movement.reason == f"Baixa do pedido {order.id}"