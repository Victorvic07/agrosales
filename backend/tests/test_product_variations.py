from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.modules.products.variation_model import ProductVariation
from app.modules.products.variation_repository import ProductVariationRepository
from app.modules.products.variation_schemas import (
    ProductVariationCreate,
    ProductVariationStatusUpdate,
    ProductVariationUpdate,
)
from app.modules.products.variation_service import (
    InvalidMinimumPriceError,
    ProductVariationNotFoundError,
    ProductVariationService,
)


def test_product_variation_table_name() -> None:
    assert ProductVariation.__tablename__ == "product_variations"


def test_product_variation_defaults_to_active() -> None:
    default = ProductVariation.__table__.c.is_active.default

    assert default is not None
    assert default.arg is True


def test_product_variation_accepts_valid_values() -> None:
    variation = ProductVariationCreate(
        product_id=uuid4(),
        internal_code="TOM-ITA-20-A",
        classification="Categoria A",
        package_type="Caixa 20 kg",
        unit_of_measure="CAIXA",
        weight_or_volume=Decimal("20"),
        standard_price=Decimal("160"),
        minimum_price=Decimal("145"),
        minimum_stock=Decimal("10"),
        commission_percentage=Decimal("3"),
    )

    assert variation.standard_price == Decimal("160")
    assert variation.commission_percentage == Decimal("3")


def test_product_variation_rejects_invalid_commission() -> None:
    with pytest.raises(ValidationError):
        ProductVariationCreate(
            product_id=uuid4(),
            internal_code="TOM-ITA-20-A",
            package_type="Caixa 20 kg",
            unit_of_measure="CAIXA",
            standard_price=Decimal("160"),
            minimum_price=Decimal("145"),
            commission_percentage=Decimal("150"),
        )


def test_product_variation_update_rejects_product_id() -> None:
    with pytest.raises(ValidationError):
        ProductVariationUpdate(
            product_id=uuid4(),
        )


def test_product_variation_update_rejects_internal_code() -> None:
    with pytest.raises(ValidationError):
        ProductVariationUpdate(
            internal_code="NOVO-CODIGO",
        )


def test_product_variation_update_accepts_editable_fields() -> None:
    variation = ProductVariationUpdate(
        classification="Premium",
        package_type="Saco 25 kg",
        unit_of_measure="SACO",
        weight_or_volume=Decimal("25"),
        standard_price=Decimal("180"),
        minimum_price=Decimal("165"),
        minimum_stock=Decimal("12"),
        commission_percentage=Decimal("4"),
        barcode="789000000001",
        qr_code="VAR-001",
    )

    assert variation.classification == "Premium"
    assert variation.package_type == "Saco 25 kg"
    assert variation.standard_price == Decimal("180")
    assert variation.minimum_price == Decimal("165")


def test_product_variation_update_allows_partial_payload() -> None:
    variation = ProductVariationUpdate(
        classification="Premium",
    )

    assert variation.classification == "Premium"
    assert variation.standard_price is None
    assert variation.minimum_price is None


def test_product_variation_status_update_accepts_boolean() -> None:
    status_update = ProductVariationStatusUpdate(
        is_active=False,
    )

    assert status_update.is_active is False


@pytest.mark.asyncio
async def test_repository_updates_only_provided_fields() -> None:
    session = AsyncMock()
    repository = ProductVariationRepository(session)

    variation = ProductVariation(
        id=uuid4(),
        product_id=uuid4(),
        internal_code="TOM-001",
        classification=None,
        package_type="Caixa",
        unit_of_measure="CAIXA",
        weight_or_volume=None,
        standard_price=Decimal("100"),
        minimum_price=Decimal("90"),
        minimum_stock=Decimal("0"),
        commission_percentage=Decimal("0"),
        barcode=None,
        qr_code=None,
        is_active=True,
    )

    data = ProductVariationUpdate(
        classification="Premium",
        standard_price=Decimal("110"),
    )

    result = await repository.update(
        variation,
        data,
    )

    assert result.classification == "Premium"
    assert result.standard_price == Decimal("110")
    assert result.minimum_price == Decimal("90")

    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(
        variation,
    )


@pytest.mark.asyncio
async def test_repository_updates_status() -> None:
    session = AsyncMock()
    repository = ProductVariationRepository(session)

    variation = ProductVariation(
        id=uuid4(),
        product_id=uuid4(),
        internal_code="TOM-001",
        classification=None,
        package_type="Caixa",
        unit_of_measure="CAIXA",
        weight_or_volume=None,
        standard_price=Decimal("100"),
        minimum_price=Decimal("90"),
        minimum_stock=Decimal("0"),
        commission_percentage=Decimal("0"),
        barcode=None,
        qr_code=None,
        is_active=True,
    )

    result = await repository.update_status(
        variation,
        False,
    )

    assert result.is_active is False

    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(
        variation,
    )


@pytest.mark.asyncio
async def test_service_updates_variation() -> None:
    variation = ProductVariation(
        id=uuid4(),
        product_id=uuid4(),
        internal_code="TOM-001",
        classification=None,
        package_type="Caixa",
        unit_of_measure="CAIXA",
        weight_or_volume=None,
        standard_price=Decimal("100"),
        minimum_price=Decimal("90"),
        minimum_stock=Decimal("0"),
        commission_percentage=Decimal("0"),
        barcode=None,
        qr_code=None,
        is_active=True,
    )

    variation_repository = AsyncMock()
    variation_repository.get_by_id.return_value = variation
    variation_repository.update.return_value = variation

    service = ProductVariationService(
        variation_repository=variation_repository,
        product_repository=AsyncMock(),
    )

    data = ProductVariationUpdate(
        classification="Premium",
        standard_price=Decimal("110"),
        minimum_price=Decimal("100"),
    )

    result = await service.update(
        variation.id,
        data,
    )

    assert result is variation

    variation_repository.update.assert_awaited_once_with(
        variation,
        data,
    )


@pytest.mark.asyncio
async def test_service_rejects_minimum_price_above_updated_standard_price() -> None:
    variation = ProductVariation(
        id=uuid4(),
        product_id=uuid4(),
        internal_code="TOM-001",
        classification=None,
        package_type="Caixa",
        unit_of_measure="CAIXA",
        weight_or_volume=None,
        standard_price=Decimal("100"),
        minimum_price=Decimal("90"),
        minimum_stock=Decimal("0"),
        commission_percentage=Decimal("0"),
        barcode=None,
        qr_code=None,
        is_active=True,
    )

    variation_repository = AsyncMock()
    variation_repository.get_by_id.return_value = variation

    service = ProductVariationService(
        variation_repository=variation_repository,
        product_repository=AsyncMock(),
    )

    with pytest.raises(
        InvalidMinimumPriceError,
        match=(
            "O preço mínimo não pode ser maior "
            "que o preço padrão"
        ),
    ):
        await service.update(
            variation.id,
            ProductVariationUpdate(
                standard_price=Decimal("80"),
            ),
        )

    variation_repository.update.assert_not_awaited()


@pytest.mark.asyncio
async def test_service_rejects_updated_minimum_price_above_existing_standard_price() -> None:
    variation = ProductVariation(
        id=uuid4(),
        product_id=uuid4(),
        internal_code="TOM-001",
        classification=None,
        package_type="Caixa",
        unit_of_measure="CAIXA",
        weight_or_volume=None,
        standard_price=Decimal("100"),
        minimum_price=Decimal("90"),
        minimum_stock=Decimal("0"),
        commission_percentage=Decimal("0"),
        barcode=None,
        qr_code=None,
        is_active=True,
    )

    variation_repository = AsyncMock()
    variation_repository.get_by_id.return_value = variation

    service = ProductVariationService(
        variation_repository=variation_repository,
        product_repository=AsyncMock(),
    )

    with pytest.raises(InvalidMinimumPriceError):
        await service.update(
            variation.id,
            ProductVariationUpdate(
                minimum_price=Decimal("101"),
            ),
        )

    variation_repository.update.assert_not_awaited()


@pytest.mark.asyncio
async def test_service_raises_when_variation_does_not_exist() -> None:
    variation_repository = AsyncMock()
    variation_repository.get_by_id.return_value = None

    service = ProductVariationService(
        variation_repository=variation_repository,
        product_repository=AsyncMock(),
    )

    with pytest.raises(
        ProductVariationNotFoundError,
        match="Variação de produto não encontrada",
    ):
        await service.update(
            uuid4(),
            ProductVariationUpdate(
                classification="Premium",
            ),
        )


@pytest.mark.asyncio
async def test_service_updates_status() -> None:
    variation = ProductVariation(
        id=uuid4(),
        product_id=uuid4(),
        internal_code="TOM-001",
        classification=None,
        package_type="Caixa",
        unit_of_measure="CAIXA",
        weight_or_volume=None,
        standard_price=Decimal("100"),
        minimum_price=Decimal("90"),
        minimum_stock=Decimal("0"),
        commission_percentage=Decimal("0"),
        barcode=None,
        qr_code=None,
        is_active=True,
    )

    variation_repository = AsyncMock()
    variation_repository.get_by_id.return_value = variation
    variation_repository.update_status.return_value = variation

    service = ProductVariationService(
        variation_repository=variation_repository,
        product_repository=AsyncMock(),
    )

    result = await service.update_status(
        variation.id,
        False,
    )

    assert result is variation

    variation_repository.update_status.assert_awaited_once_with(
        variation,
        False,
    )


@pytest.mark.asyncio
async def test_service_status_raises_when_variation_does_not_exist() -> None:
    variation_repository = AsyncMock()
    variation_repository.get_by_id.return_value = None

    service = ProductVariationService(
        variation_repository=variation_repository,
        product_repository=AsyncMock(),
    )

    with pytest.raises(
        ProductVariationNotFoundError,
        match="Variação de produto não encontrada",
    ):
        await service.update_status(
            uuid4(),
            False,
        )

    variation_repository.update_status.assert_not_awaited()