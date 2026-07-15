from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import (
    get_customer_repository,
    require_roles,
)
from app.core.enums import UserRole
from app.modules.customers.customer_model import Customer
from app.modules.customers.customer_repository import (
    CustomerRepository,
)
from app.modules.customers.customer_schemas import (
    CustomerCreate,
    CustomerRead,
    CustomerStatusUpdate,
    CustomerUpdate,
)
from app.modules.customers.customer_service import (
    CustomerDocumentAlreadyExistsError,
    CustomerNotFoundError,
    CustomerService,
    InvalidCustomerDocumentError,
)
from app.modules.users.model import User

router = APIRouter(
    prefix="/customers",
    tags=["Clientes"],
)


def build_service(
    repository: CustomerRepository,
) -> CustomerService:
    return CustomerService(repository)


def raise_customer_error(error: Exception) -> None:
    if isinstance(error, CustomerNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    if isinstance(
        error,
        CustomerDocumentAlreadyExistsError,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    if isinstance(error, InvalidCustomerDocumentError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error

    raise error


@router.get(
    "",
    response_model=list[CustomerRead],
)
async def list_customers(
    repository: Annotated[
        CustomerRepository,
        Depends(get_customer_repository),
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
    include_inactive: bool = Query(default=False),
) -> list[Customer]:
    return await repository.list_all(include_inactive)


@router.get(
    "/{customer_id}",
    response_model=CustomerRead,
)
async def get_customer(
    customer_id: UUID,
    repository: Annotated[
        CustomerRepository,
        Depends(get_customer_repository),
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
) -> Customer:
    customer = await repository.get_by_id(customer_id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado",
        )

    return customer


@router.post(
    "",
    response_model=CustomerRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_customer(
    data: CustomerCreate,
    repository: Annotated[
        CustomerRepository,
        Depends(get_customer_repository),
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
) -> Customer:
    try:
        return await build_service(repository).create(data)
    except Exception as error:
        raise_customer_error(error)
        raise


@router.patch(
    "/{customer_id}",
    response_model=CustomerRead,
)
async def update_customer(
    customer_id: UUID,
    data: CustomerUpdate,
    repository: Annotated[
        CustomerRepository,
        Depends(get_customer_repository),
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
) -> Customer:
    try:
        return await build_service(repository).update(
            customer_id,
            data,
        )
    except Exception as error:
        raise_customer_error(error)
        raise


@router.patch(
    "/{customer_id}/status",
    response_model=CustomerRead,
)
async def update_customer_status(
    customer_id: UUID,
    data: CustomerStatusUpdate,
    repository: Annotated[
        CustomerRepository,
        Depends(get_customer_repository),
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
) -> Customer:
    try:
        return await build_service(repository).set_active(
            customer_id,
            data.is_active,
        )
    except Exception as error:
        raise_customer_error(error)
        raise