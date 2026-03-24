from enum import StrEnum


class OriginState(StrEnum):
    NORMAL = "Normal"
    RESTRUCTURED = "Reestructurado"
    REFINANCED = "Refinanciado"
    TRANSFERRED = "Trasladado"
    PURCHASED = "Comprado"
    UNKNOWN = "Desconocido"
