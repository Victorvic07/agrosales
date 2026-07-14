from enum import StrEnum


class UserRole(StrEnum):
    ADMINISTRADOR = "ADMINISTRADOR"
    PRODUTOR = "PRODUTOR"
    VENDEDOR = "VENDEDOR"