

from enum import StrEnum


class ObligationType(StrEnum):
    NO_INFORMATION = "No se encuentra información en este campo"
    COMMERCIAL = "Comerciales"
    CONSUMPTION = "Consumo"
    MORTGAGE = "Hipotecario"
    OTHER = "Otro"
    MICRO_CREDIT = "Microcrédito"
    PAYROLL_LOAN = "Libranza"
    INSURANCE = "Seguros"
    PUBLIC = "Estatal"
    UNKNOWN = "Desconocido"