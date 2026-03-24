from enum import StrEnum


class CreditCardClass(StrEnum):
    CLASSIC = "Clásica"
    GOLD = "Gold"
    PLATINUM = "Platinum"
    OTHER = "Otra"
    UNKNOWN = "Desconocido"
