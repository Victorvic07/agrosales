from datetime import date

from app.modules.inventory.lot_model import Lot
from app.modules.inventory.lot_repository import LotRepository
from app.modules.inventory.lot_schemas import LotCreate
from app.modules.products.variation_repository import (
    ProductVariationRepository,
)


class ProductVariationNotFoundError(Exception):
    pass


class LotAlreadyExistsError(Exception):
    pass


class ExpiredLotError(Exception):
    pass


class LotService:
    def __init__(
        self,
        lot_repository: LotRepository,
        variation_repository: ProductVariationRepository,
    ) -> None:
        self.lot_repository = lot_repository
        self.variation_repository = variation_repository

    async def create(self, data: LotCreate) -> Lot:
        variation = await self.variation_repository.get_by_id(
            data.product_variation_id
        )

        if variation is None or not variation.is_active:
            raise ProductVariationNotFoundError(
                "Variação de produto não encontrada ou inativa"
            )

        existing_lot = await self.lot_repository.get_by_code(data.code)

        if existing_lot is not None:
            raise LotAlreadyExistsError(
                "Já existe um lote com esse código"
            )

        if data.expiration_date < date.today():
            raise ExpiredLotError(
                "Não é permitido cadastrar um lote já vencido"
            )

        return await self.lot_repository.create(data)