from enum import StrEnum


class GlobalDebtCreditType(StrEnum):
    COMMERCIAL = "Comercial"
    MORTGAGE = "Hipotecario"
    MICROCREDIT = "Microcrédito"
    CONSUMER = "Consumo"
    UNKNOWN = "Desconocido"
