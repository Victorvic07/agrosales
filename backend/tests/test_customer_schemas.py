import pytest
from pydantic import ValidationError

from app.modules.customers.customer_model import (
    CustomerType,
    DocumentType,
)
from app.modules.customers.customer_schemas import (
    CustomerCreate,
    CustomerStatusUpdate,
)


def test_customer_create_normalizes_document_and_zip_code() -> None:
    payload = CustomerCreate(
        customer_type=CustomerType.INDIVIDUAL,
        document_type=DocumentType.CPF,
        document="529.982.247-25",
        name="Cliente Teste",
        phone="(67) 99999-9999",
        zip_code="79000-000",
        state="ms",
    )

    assert payload.document == "52998224725"
    assert payload.phone == "67999999999"
    assert payload.zip_code == "79000000"
    assert payload.state == "MS"


def test_customer_create_rejects_empty_name() -> None:
    with pytest.raises(ValidationError):
        CustomerCreate(
            customer_type=CustomerType.INDIVIDUAL,
            document_type=DocumentType.CPF,
            document="52998224725",
            name="   ",
        )


def test_customer_status_update_accepts_boolean() -> None:
    payload = CustomerStatusUpdate(is_active=False)

    assert payload.is_active is False