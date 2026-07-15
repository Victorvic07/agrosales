from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.modules.customers.customer_model import (
    Customer,
    CustomerType,
    DocumentType,
)
from app.modules.customers.customer_schemas import (
    CustomerCreate,
)
from app.modules.customers.customer_service import (
    CustomerDocumentAlreadyExistsError,
    CustomerService,
    InvalidCustomerDocumentError,
)


@pytest.mark.asyncio
async def test_service_creates_valid_customer() -> None:
    repository = MagicMock()
    repository.get_by_document = AsyncMock(
        return_value=None
    )

    created_customer = Customer(
        id=uuid4(),
        customer_type=CustomerType.INDIVIDUAL,
        document_type=DocumentType.CPF,
        document="52998224725",
        name="Cliente Teste",
        is_active=True,
    )

    repository.create = AsyncMock(
        return_value=created_customer
    )

    service = CustomerService(repository)

    result = await service.create(
        CustomerCreate(
            customer_type=CustomerType.INDIVIDUAL,
            document_type=DocumentType.CPF,
            document="529.982.247-25",
            name="Cliente Teste",
        )
    )

    assert result.document == "52998224725"
    repository.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_service_rejects_invalid_document() -> None:
    service = CustomerService(MagicMock())

    with pytest.raises(
        InvalidCustomerDocumentError
    ):
        await service.create(
            CustomerCreate(
                customer_type=CustomerType.INDIVIDUAL,
                document_type=DocumentType.CPF,
                document="11111111111",
                name="Cliente Inválido",
            )
        )


@pytest.mark.asyncio
async def test_service_rejects_duplicate_document() -> None:
    repository = MagicMock()
    repository.get_by_document = AsyncMock(
        return_value=MagicMock()
    )

    service = CustomerService(repository)

    with pytest.raises(
        CustomerDocumentAlreadyExistsError
    ):
        await service.create(
            CustomerCreate(
                customer_type=CustomerType.COMPANY,
                document_type=DocumentType.CNPJ,
                document="11222333000181",
                name="Empresa Duplicada",
            )
        )