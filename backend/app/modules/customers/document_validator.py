from app.modules.customers.customer_model import DocumentType


def _calculate_digit(
    digits: list[int],
    weights: list[int],
) -> int:
    total = sum(
        digit * weight
        for digit, weight in zip(
            digits,
            weights,
            strict=True,
        )
    )

    remainder = total % 11

    return 0 if remainder < 2 else 11 - remainder


def is_valid_cpf(document: str) -> bool:
    if len(document) != 11:
        return False

    if not document.isdigit():
        return False

    if document == document[0] * 11:
        return False

    digits = [
        int(value)
        for value in document
    ]

    first_digit = _calculate_digit(
        digits[:9],
        list(range(10, 1, -1)),
    )

    second_digit = _calculate_digit(
        digits[:9] + [first_digit],
        list(range(11, 1, -1)),
    )

    return digits[-2:] == [
        first_digit,
        second_digit,
    ]


def is_valid_cnpj(document: str) -> bool:
    if len(document) != 14:
        return False

    if not document.isdigit():
        return False

    if document == document[0] * 14:
        return False

    digits = [
        int(value)
        for value in document
    ]

    first_digit = _calculate_digit(
        digits[:12],
        [
            5,
            4,
            3,
            2,
            9,
            8,
            7,
            6,
            5,
            4,
            3,
            2,
        ],
    )

    second_digit = _calculate_digit(
        digits[:12] + [first_digit],
        [
            6,
            5,
            4,
            3,
            2,
            9,
            8,
            7,
            6,
            5,
            4,
            3,
            2,
        ],
    )

    return digits[-2:] == [
        first_digit,
        second_digit,
    ]


def validate_document(
    document_type: DocumentType,
    document: str,
) -> bool:
    if document_type == DocumentType.CPF:
        return is_valid_cpf(document)

    if document_type == DocumentType.CNPJ:
        return is_valid_cnpj(document)

    return False