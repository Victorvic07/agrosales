from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.customers.customer_model import Customer
from app.modules.customers.customer_schemas import (
    CustomerCreate,
    CustomerUpdate,
)


class CustomerRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def get_by_id(
        self,
        customer_id: UUID,
    ) -> Customer | None:
        return await self.session.get(
            Customer,
            customer_id,
        )

    async def get_by_document(
        self,
        document: str,
    ) -> Customer | None:
        statement = select(Customer).where(
            Customer.document == document
        )

        return await self.session.scalar(statement)

    async def list_all(
        self,
        include_inactive: bool = False,
    ) -> list[Customer]:
        statement = select(Customer)

        if not include_inactive:
            statement = statement.where(
                Customer.is_active.is_(True)
            )

        statement = statement.order_by(
            Customer.name.asc()
        )

        result = await self.session.scalars(statement)

        return list(result.all())

    async def create(
        self,
        data: CustomerCreate,
    ) -> Customer:
        customer = Customer(
            **data.model_dump()
        )

        self.session.add(customer)

        await self.session.commit()
        await self.session.refresh(customer)

        return customer

    async def update(
        self,
        customer: Customer,
        data: CustomerUpdate,
    ) -> Customer:
        values = data.model_dump(
            exclude_unset=True
        )

        for field, value in values.items():
            setattr(customer, field, value)

        await self.session.commit()
        await self.session.refresh(customer)

        return customer

    async def set_active(
        self,
        customer: Customer,
        is_active: bool,
    ) -> Customer:
        customer.is_active = is_active

        await self.session.commit()
        await self.session.refresh(customer)

        return customer