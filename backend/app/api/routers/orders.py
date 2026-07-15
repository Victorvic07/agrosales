from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import (
    get_customer_repository,
    get_order_repository,
    get_product_variation_repository,
    get_reservation_repository,
    require_roles,
)
from app.core.enums import UserRole
from app.database.session import get_db_session
from app.modules.customers.customer_repository import CustomerRepository
from app.modules.inventory.reservation_repository import ReservationRepository
from app.modules.inventory.reservation_service import InsufficientAvailableStockError
from app.modules.orders.order_confirmation_service import (
    InactiveCustomerError as ConfirmationInactiveCustomerError,
    OrderCannotBeConfirmedError,
    OrderConfirmationService,
    OrderNotFoundError as ConfirmationOrderNotFoundError,
    OrderWithoutItemsError,
)
from app.modules.orders.order_item_model import OrderItem
from app.modules.orders.order_model import Order
from app.modules.orders.order_repository import OrderRepository
from app.modules.orders.order_schemas import (
    OrderCreate,
    OrderItemCreate,
    OrderItemRead,
    OrderItemUpdate,
    OrderRead,
    OrderUpdate,
)
from app.modules.orders.order_service import (
    InactiveCustomerError,
    InvalidDiscountError,
    OrderItemNotFoundError,
    OrderNotEditableError,
    OrderNotFoundError,
    OrderService,
    PriceBelowMinimumError,
    ProductVariationNotFoundError,
)
from app.modules.products.variation_repository import ProductVariationRepository
from app.modules.users.model import User

router = APIRouter(prefix="/orders", tags=["Pedidos"])


def build_service(
    order_repository: OrderRepository,
    customer_repository: CustomerRepository,
    variation_repository: ProductVariationRepository,
) -> OrderService:
    return OrderService(
        order_repository=order_repository,
        customer_repository=customer_repository,
        variation_repository=variation_repository,
    )


def raise_order_error(error: Exception) -> None:
    if isinstance(
        error,
        (
            OrderNotFoundError,
            OrderItemNotFoundError,
            ProductVariationNotFoundError,
        ),
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    if isinstance(error, OrderNotEditableError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    if isinstance(
        error,
        (
            InactiveCustomerError,
            PriceBelowMinimumError,
            InvalidDiscountError,
        ),
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error

    raise error


@router.get("", response_model=list[OrderRead])
async def list_orders(
    repository: Annotated[OrderRepository, Depends(get_order_repository)],
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
) -> list[Order]:
    return await repository.list_all()


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(
    order_id: UUID,
    repository: Annotated[OrderRepository, Depends(get_order_repository)],
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
) -> Order:
    order = await repository.get_by_id(order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido não encontrado",
        )
    return order


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(
    data: OrderCreate,
    order_repository: Annotated[OrderRepository, Depends(get_order_repository)],
    customer_repository: Annotated[
        CustomerRepository,
        Depends(get_customer_repository),
    ],
    variation_repository: Annotated[
        ProductVariationRepository,
        Depends(get_product_variation_repository),
    ],
    current_user: Annotated[
        User,
        Depends(
            require_roles(
                UserRole.ADMINISTRADOR,
                UserRole.PRODUTOR,
                UserRole.VENDEDOR,
            )
        ),
    ],
) -> Order:
    service = build_service(
        order_repository,
        customer_repository,
        variation_repository,
    )
    try:
        return await service.create_order(data=data, seller_id=current_user.id)
    except Exception as error:
        raise_order_error(error)
        raise


@router.patch("/{order_id}", response_model=OrderRead)
async def update_order(
    order_id: UUID,
    data: OrderUpdate,
    order_repository: Annotated[OrderRepository, Depends(get_order_repository)],
    customer_repository: Annotated[
        CustomerRepository,
        Depends(get_customer_repository),
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
                UserRole.VENDEDOR,
            )
        ),
    ],
) -> Order:
    service = build_service(
        order_repository,
        customer_repository,
        variation_repository,
    )
    try:
        return await service.update_order(order_id, data)
    except Exception as error:
        raise_order_error(error)
        raise


@router.post(
    "/{order_id}/items",
    response_model=OrderItemRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_order_item(
    order_id: UUID,
    data: OrderItemCreate,
    order_repository: Annotated[OrderRepository, Depends(get_order_repository)],
    customer_repository: Annotated[
        CustomerRepository,
        Depends(get_customer_repository),
    ],
    variation_repository: Annotated[
        ProductVariationRepository,
        Depends(get_product_variation_repository),
    ],
    current_user: Annotated[
        User,
        Depends(
            require_roles(
                UserRole.ADMINISTRADOR,
                UserRole.PRODUTOR,
                UserRole.VENDEDOR,
            )
        ),
    ],
) -> OrderItem:
    service = build_service(
        order_repository,
        customer_repository,
        variation_repository,
    )
    try:
        return await service.add_item(
            order_id=order_id,
            data=data,
            user_role=current_user.role,
        )
    except Exception as error:
        raise_order_error(error)
        raise


@router.patch("/{order_id}/items/{item_id}", response_model=OrderItemRead)
async def update_order_item(
    order_id: UUID,
    item_id: UUID,
    data: OrderItemUpdate,
    order_repository: Annotated[OrderRepository, Depends(get_order_repository)],
    customer_repository: Annotated[
        CustomerRepository,
        Depends(get_customer_repository),
    ],
    variation_repository: Annotated[
        ProductVariationRepository,
        Depends(get_product_variation_repository),
    ],
    current_user: Annotated[
        User,
        Depends(
            require_roles(
                UserRole.ADMINISTRADOR,
                UserRole.PRODUTOR,
                UserRole.VENDEDOR,
            )
        ),
    ],
) -> OrderItem:
    service = build_service(
        order_repository,
        customer_repository,
        variation_repository,
    )
    try:
        return await service.update_item(
            order_id=order_id,
            item_id=item_id,
            data=data,
            user_role=current_user.role,
        )
    except Exception as error:
        raise_order_error(error)
        raise


@router.delete("/{order_id}/items/{item_id}", response_model=OrderRead)
async def delete_order_item(
    order_id: UUID,
    item_id: UUID,
    order_repository: Annotated[OrderRepository, Depends(get_order_repository)],
    customer_repository: Annotated[
        CustomerRepository,
        Depends(get_customer_repository),
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
                UserRole.VENDEDOR,
            )
        ),
    ],
) -> Order:
    service = build_service(
        order_repository,
        customer_repository,
        variation_repository,
    )
    try:
        return await service.delete_item(order_id=order_id, item_id=item_id)
    except Exception as error:
        raise_order_error(error)
        raise


@router.post(
    "/{order_id}/confirm",
    response_model=OrderRead,
    status_code=status.HTTP_200_OK,
)
async def confirm_order(
    order_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    order_repository: Annotated[OrderRepository, Depends(get_order_repository)],
    customer_repository: Annotated[
        CustomerRepository,
        Depends(get_customer_repository),
    ],
    reservation_repository: Annotated[
        ReservationRepository,
        Depends(get_reservation_repository),
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
) -> Order:
    service = OrderConfirmationService(
        session=session,
        order_repository=order_repository,
        customer_repository=customer_repository,
        reservation_repository=reservation_repository,
    )

    try:
        return await service.confirm(order_id)
    except ConfirmationOrderNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except OrderCannotBeConfirmedError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    except (
        OrderWithoutItemsError,
        ConfirmationInactiveCustomerError,
        InsufficientAvailableStockError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error