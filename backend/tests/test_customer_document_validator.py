from app.modules.customers.customer_model import DocumentType
from app.modules.customers.document_validator import (
    is_valid_cnpj,
    is_valid_cpf,
    validate_document,
)


def test_accepts_valid_cpf() -> None:
    assert is_valid_cpf("52998224725") is True


def test_rejects_invalid_cpf() -> None:
    assert is_valid_cpf("11111111111") is False
    assert is_valid_cpf("52998224724") is False


def test_accepts_valid_cnpj() -> None:
    assert is_valid_cnpj("11222333000181") is True


def test_rejects_invalid_cnpj() -> None:
    assert is_valid_cnpj("11111111111111") is False
    assert is_valid_cnpj("11222333000180") is False


def test_dispatches_validation_by_document_type() -> None:
    assert validate_document(
        DocumentType.CPF,
        "52998224725",
    ) is True

    assert validate_document(
        DocumentType.CNPJ,
        "11222333000181",
    ) is True