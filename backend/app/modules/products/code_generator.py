from typing import Protocol

PRODUCT_CODE_PREFIX = "PRD-"
PRODUCT_CODE_DIGITS = 6
PRODUCT_CODE_MAX_NUMBER = 999999


class ProductCodeLimitError(Exception):
    pass


class ProductCodeRepository(Protocol):
    async def get_last_generated_code(
        self,
    ) -> str | None:
        pass

    async def exists_by_code(
        self,
        code: str,
    ) -> bool:
        pass


def generate_next_product_code(
    last_code: str | None,
) -> str:
    if last_code is None:
        return f"{PRODUCT_CODE_PREFIX}000001"

    if not last_code.startswith(PRODUCT_CODE_PREFIX):
        raise ValueError("Código de produto inválido")

    numeric_part = last_code.removeprefix(
        PRODUCT_CODE_PREFIX
    )

    if (
        len(numeric_part) != PRODUCT_CODE_DIGITS
        or not numeric_part.isdigit()
    ):
        raise ValueError("Código de produto inválido")

    current_number = int(numeric_part)

    if current_number >= PRODUCT_CODE_MAX_NUMBER:
        raise ProductCodeLimitError(
            "O limite de códigos automáticos foi atingido"
        )

    next_number = current_number + 1

    return (
        f"{PRODUCT_CODE_PREFIX}"
        f"{next_number:0{PRODUCT_CODE_DIGITS}d}"
    )


async def generate_unique_product_code(
    repository: ProductCodeRepository,
) -> str:
    last_code = await repository.get_last_generated_code()

    candidate = generate_next_product_code(last_code)

    while await repository.exists_by_code(candidate):
        candidate = generate_next_product_code(candidate)

    return candidate