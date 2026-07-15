from uuid import UUID

from app.modules.customers.customer_model import Customer
from app.modules.customers.customer_repository import (
    CustomerRepository,
)
from app.modules.customers.customer_schemas import (
    CustomerCreate,
    CustomerUpdate,
)
from app.modules.customers.document_validator import (
    validate_document,
)


class CustomerNotFoundError(Exception):
    pass


class CustomerDocumentAlreadyExistsError(Exception):
    pass


class InvalidCustomerDocumentError(Exception):
    pass


class CustomerService:
    def __init__(
        self,
        repository: CustomerRepository,
    ) -> None:
        self.repository = repository

    def _validate_document(
        self,
        document_type,
        document: str,
    ) -> None:
        if not validate_document(
            document_type,
            document,
        ):
            raise InvalidCustomerDocumentError(
                "CPF ou CNPJ inválido"
            )

    async def create(
        self,
        data: CustomerCreate,
    ) -> Customer:
        self._validate_document(
            data.document_type,
            data.document,
        )

        existing = await self.repository.get_by_document(
            data.document
        )

        if existing is not None:
            raise CustomerDocumentAlreadyExistsError(
                "Já existe um cliente com esse documento"
            )

        return await self.repository.create(data)

    async def update(
        self,
        customer_id: UUID,
        data: CustomerUpdate,
    ) -> Customer:
        customer = await self.repository.get_by_id(
            customer_id
        )

        if customer is None:
            raise CustomerNotFoundError(
                "Cliente não encontrado"
            )

        document_type = (
            data.document_type
            if data.document_type is not None
            else customer.document_type
        )

        document = (
            data.document
            if data.document is not None
            else customer.document
        )

        self._validate_document(
            document_type,
            document,
        )

        if document != customer.document:
            existing = await self.repository.get_by_document(
                document
            )

            if existing is not None:
                raise CustomerDocumentAlreadyExistsError(
                    "Já existe um cliente com esse documento"
                )

        return await self.repository.update(
            customer,
            data,
        )

    async def set_active(
        self,
        customer_id: UUID,
        is_active: bool,
    ) -> Customer:
        customer = await self.repository.get_by_id(
            customer_id
        )

        if customer is None:
            raise CustomerNotFoundError(
                "Cliente não encontrado"
            )

        return await self.repository.set_active(
            customer,
            is_active,
        )