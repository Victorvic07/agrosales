from unittest.mock import AsyncMock

import pytest

from app.modules.products.code_generator import (
    ProductCodeLimitError,
    generate_next_product_code,
    generate_unique_product_code,
)


def test_generates_first_product_code() -> None:
    code = generate_next_product_code(None)

    assert code == "PRD-000001"


def test_increments_last_product_code() -> None:
    code = generate_next_product_code("PRD-000009")

    assert code == "PRD-000010"


def test_rejects_invalid_product_code() -> None:
    with pytest.raises(ValueError):
        generate_next_product_code("PRODUTO-10")


def test_rejects_code_above_supported_limit() -> None:
    with pytest.raises(ProductCodeLimitError):
        generate_next_product_code("PRD-999999")


@pytest.mark.asyncio
async def test_generates_unique_code_without_collision() -> None:
    repository = AsyncMock()
    repository.get_last_generated_code.return_value = "PRD-000010"
    repository.exists_by_code.return_value = False

    code = await generate_unique_product_code(repository)

    assert code == "PRD-000011"

    repository.exists_by_code.assert_awaited_once_with(
        "PRD-000011"
    )


@pytest.mark.asyncio
async def test_skips_codes_that_already_exist() -> None:
    repository = AsyncMock()
    repository.get_last_generated_code.return_value = "PRD-000010"

    repository.exists_by_code.side_effect = [
        True,
        True,
        False,
    ]

    code = await generate_unique_product_code(repository)

    assert code == "PRD-000013"

    assert repository.exists_by_code.await_count == 3