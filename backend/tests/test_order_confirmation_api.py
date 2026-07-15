from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.api.dependencies import (
    get_current_user,
    get_customer_repository,
    get_order_repository,
    get_reservation_repository,
)
from app.core.enums import UserRole
from app.database.session import get_db_session
from app.main import app
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


def test_vendor_cannot_confirm_order(client) -> None:
    app.dependency_overrides[get_current_user] = (
        lambda: make_user(UserRole.VENDEDOR)
    )

    response = client.post(
        f"/api/v1/orders/{uuid4()}/confirm"
    )

    app.dependency_overrides.clear()

    assert response.status_code == 403


def test_returns_404_when_confirming_unknown_order(client) -> None:
    order_repository = AsyncMock()
    order_repository.get_by_id_for_update.return_value = None

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
    app.dependency_overrides[get_customer_repository] = (
        lambda: AsyncMock()
    )
    app.dependency_overrides[get_reservation_repository] = (
        lambda: AsyncMock()
    )
    app.dependency_overrides[get_db_session] = override_session

    response = client.post(
        f"/api/v1/orders/{uuid4()}/confirm"
    )

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Pedido não encontrado"


def test_rejects_order_without_items(client) -> None:
    order_id = uuid4()

    order = Order(
        id=order_id,
        customer_id=uuid4(),
        seller_id=uuid4(),
        status=OrderStatus.DRAFT,
        subtotal=Decimal("0"),
        discount_total=Decimal("0"),
        total_amount=Decimal("0"),
    )
    order.items = []

    order_repository = AsyncMock()
    order_repository.get_by_id_for_update.return_value = order

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
    app.dependency_overrides[get_customer_repository] = (
        lambda: AsyncMock()
    )
    app.dependency_overrides[get_reservation_repository] = (
        lambda: AsyncMock()
    )
    app.dependency_overrides[get_db_session] = override_session

    response = client.post(
        f"/api/v1/orders/{order_id}/confirm"
    )

    app.dependency_overrides.clear()

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "O pedido precisa ter ao menos um item"
    )