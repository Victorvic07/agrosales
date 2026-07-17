from enum import StrEnum


class ProductUnit(StrEnum):
    UNIDADE = "UNIDADE"
    QUILOGRAMA = "QUILOGRAMA"
    GRAMA = "GRAMA"
    LITRO = "LITRO"
    MILILITRO = "MILILITRO"
    CAIXA = "CAIXA"
    PACOTE = "PACOTE"
    OUTRO = "OUTRO"


class ProductStatus(StrEnum):
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"
    DESCONTINUADO = "DESCONTINUADO"