from app.modules.customers.customer_model import (
    Customer,
    CustomerType,
    DocumentType,
)


def test_customer_table_name() -> None:
    assert Customer.__tablename__ == "customers"


def test_customer_type_values() -> None:
    assert {item.value for item in CustomerType} == {
        "INDIVIDUAL",
        "COMPANY",
    }


def test_document_type_values() -> None:
    assert {item.value for item in DocumentType} == {
        "CPF",
        "CNPJ",
    }