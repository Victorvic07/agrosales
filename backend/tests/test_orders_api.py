from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.api.dependencies import (
    get_current_user,
    get_customer_repository,
    get_order_repository,
    get_order_status_history_repository,
    get_product_variation_repository,
    get_reservation_repository,
)
from app.core.enums import UserRole
from app.database.session import get_db_session
from app.main import app
from app.modules.orders.order_cancellation_service import (
    OrderCannotBeCancelledError,
)
from app.modules.orders.order_completion_service import (
    OrderCannotBeCompletedError,
)
from app.modules.orders.order_confirmation_service import (
    OrderCannotBeConfirmedError,
)
from app.modules.orders.order_model import OrderStatus
from app.modules.users.model import User


def make_user(
    role: UserRole,
) -> User:
    return User(
        id=uuid4(),
        name="Usuário",
        email=f"{role.value.lower()}@agrosales.com",
        password_hash="hash",
        role=role,
        is_active=True,
    )


def test_rejects_order_with_inactive_customer(
    client,
) -> None:
    customer_repository = AsyncMock()
    customer_repository.get_by_id.return_value = None

    app.dependency_overrides[get_current_user] = (
        lambda: make_user(UserRole.VENDEDOR)
    )

    app.dependency_overrides[get_customer_repository] = (
        lambda: customer_repository
    )

    app.dependency_overrides[get_order_repository] = (
        lambda: AsyncMock()
    )

    app.dependency_overrides[
        get_product_variation_repository
    ] = lambda: AsyncMock()

    app.dependency_overrides[
        get_order_status_history_repository
    ] = lambda: MagicMock()

    response = client.post(
        "/api/v1/orders",
        json={
            "customer_id": str(uuid4()),
            "notes": None,
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "Cliente não encontrado ou inativo"
    )


def test_rejects_zero_item_quantity(
    client,
) -> None:
    app.dependency_overrides[get_current_user] = (
        lambda: make_user(UserRole.PRODUTOR)
    )

    response = client.post(
        f"/api/v1/orders/{uuid4()}/items",
        json={
            "product_variation_id": str(uuid4()),
            "quantity": "0",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 422


def test_confirmation_passes_user_and_history_repository(
    client,
) -> None:
    order_id = uuid4()
    current_user = make_user(UserRole.PRODUTOR)

    session = AsyncMock()
    order_repository = MagicMock()
    customer_repository = MagicMock()
    reservation_repository = MagicMock()
    history_repository = MagicMock()

    app.dependency_overrides[get_current_user] = (
        lambda: current_user
    )
    app.dependency_overrides[get_db_session] = (
        lambda: session
    )
    app.dependency_overrides[get_order_repository] = (
        lambda: order_repository
    )
    app.dependency_overrides[get_customer_repository] = (
        lambda: customer_repository
    )
    app.dependency_overrides[get_reservation_repository] = (
        lambda: reservation_repository
    )
    app.dependency_overrides[
        get_order_status_history_repository
    ] = lambda: history_repository

    service = MagicMock()
    service.confirm = AsyncMock(
        side_effect=OrderCannotBeConfirmedError(
            "Pedido não pode ser confirmado"
        )
    )

    with patch(
        "app.api.routers.orders.OrderConfirmationService",
        return_value=service,
    ) as service_class:
        response = client.post(
            f"/api/v1/orders/{order_id}/confirm"
        )

    app.dependency_overrides.clear()

    assert response.status_code == 409

    service_class.assert_called_once_with(
        session=session,
        order_repository=order_repository,
        customer_repository=customer_repository,
        reservation_repository=reservation_repository,
        history_repository=history_repository,
    )

    service.confirm.assert_awaited_once_with(
        order_id,
        changed_by_user_id=current_user.id,
    )


def test_cancellation_passes_user_and_history_repository(
    client,
) -> None:
    order_id = uuid4()
    current_user = make_user(UserRole.PRODUTOR)

    session = AsyncMock()
    order_repository = MagicMock()
    reservation_repository = MagicMock()
    history_repository = MagicMock()

    app.dependency_overrides[get_current_user] = (
        lambda: current_user
    )
    app.dependency_overrides[get_db_session] = (
        lambda: session
    )
    app.dependency_overrides[get_order_repository] = (
        lambda: order_repository
    )
    app.dependency_overrides[get_reservation_repository] = (
        lambda: reservation_repository
    )
    app.dependency_overrides[
        get_order_status_history_repository
    ] = lambda: history_repository

    service = MagicMock()
    service.cancel = AsyncMock(
        side_effect=OrderCannotBeCancelledError(
            "Pedido não pode ser cancelado"
        )
    )

    with patch(
        "app.api.routers.orders.OrderCancellationService",
        return_value=service,
    ) as service_class:
        response = client.post(
            f"/api/v1/orders/{order_id}/cancel"
        )

    app.dependency_overrides.clear()

    assert response.status_code == 409

    service_class.assert_called_once_with(
        session=session,
        order_repository=order_repository,
        reservation_repository=reservation_repository,
        history_repository=history_repository,
    )

    service.cancel.assert_awaited_once_with(
        order_id,
        changed_by_user_id=current_user.id,
    )


def test_completion_passes_user_and_history_repository(
    client,
) -> None:
    order_id = uuid4()
    current_user = make_user(UserRole.PRODUTOR)

    session = AsyncMock()
    order_repository = MagicMock()
    reservation_repository = MagicMock()
    history_repository = MagicMock()

    app.dependency_overrides[get_current_user] = (
        lambda: current_user
    )
    app.dependency_overrides[get_db_session] = (
        lambda: session
    )
    app.dependency_overrides[get_order_repository] = (
        lambda: order_repository
    )
    app.dependency_overrides[get_reservation_repository] = (
        lambda: reservation_repository
    )
    app.dependency_overrides[
        get_order_status_history_repository
    ] = lambda: history_repository

    service = MagicMock()
    service.complete = AsyncMock(
        side_effect=OrderCannotBeCompletedError(
            "Pedido não pode ser concluído"
        )
    )

    with patch(
        "app.api.routers.orders.OrderCompletionService",
        return_value=service,
    ) as service_class:
        response = client.post(
            f"/api/v1/orders/{order_id}/complete"
        )

    app.dependency_overrides.clear()

    assert response.status_code == 409

    service_class.assert_called_once_with(
        session=session,
        order_repository=order_repository,
        reservation_repository=reservation_repository,
        history_repository=history_repository,
    )

    service.complete.assert_awaited_once_with(
        order_id,
        changed_by_user_id=current_user.id,
    )


def test_get_order_history_returns_chronological_history(
    client,
) -> None:
    order_id = uuid4()
    user_id = uuid4()
    current_user = make_user(UserRole.VENDEDOR)

    order_repository = MagicMock()
    order_repository.get_by_id = AsyncMock(
        return_value=MagicMock(id=order_id)
    )

    history_repository = MagicMock()
    history_repository.list_by_order = AsyncMock(
        return_value=[
            SimpleNamespace(
                id=uuid4(),
                order_id=order_id,
                previous_status=None,
                new_status=OrderStatus.DRAFT,
                changed_by_user_id=user_id,
                created_at=datetime.now(timezone.utc),
            ),
            SimpleNamespace(
                id=uuid4(),
                order_id=order_id,
                previous_status=OrderStatus.DRAFT,
                new_status=OrderStatus.CONFIRMED,
                changed_by_user_id=user_id,
                created_at=datetime.now(timezone.utc),
            ),
        ]
    )

    app.dependency_overrides[get_current_user] = (
        lambda: current_user
    )
    app.dependency_overrides[get_order_repository] = (
        lambda: order_repository
    )
    app.dependency_overrides[
        get_order_status_history_repository
    ] = lambda: history_repository

    response = client.get(
        f"/api/v1/orders/{order_id}/history"
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2
    assert body[0]["previous_status"] is None
    assert body[0]["new_status"] == OrderStatus.DRAFT.value
    assert body[1]["previous_status"] == OrderStatus.DRAFT.value
    assert body[1]["new_status"] == OrderStatus.CONFIRMED.value

    order_repository.get_by_id.assert_awaited_once_with(order_id)
    history_repository.list_by_order.assert_awaited_once_with(
        order_id
    )


def test_get_order_history_returns_404_for_missing_order(
    client,
) -> None:
    order_id = uuid4()

    order_repository = MagicMock()
    order_repository.get_by_id = AsyncMock(
        return_value=None
    )

    history_repository = MagicMock()
    history_repository.list_by_order = AsyncMock()

    app.dependency_overrides[get_current_user] = (
        lambda: make_user(UserRole.VENDEDOR)
    )
    app.dependency_overrides[get_order_repository] = (
        lambda: order_repository
    )
    app.dependency_overrides[
        get_order_status_history_repository
    ] = lambda: history_repository

    response = client.get(
        f"/api/v1/orders/{order_id}/history"
    )

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Pedido não encontrado"
    )

    history_repository.list_by_order.assert_not_awaited()