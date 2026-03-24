from enum import StrEnum


class ContractType(StrEnum):
    NOT_REPORTED = "No reportado"
    FIXED_TERM = "Término fijo"
    INDEFINITE = "Indefinido"
    UNKNOWN = "Desconocido"
