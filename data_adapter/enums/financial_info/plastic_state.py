from enum import StrEnum


class PlasticState(StrEnum):
    DELIVERED = "Entregado"
    RENEWED = "Renovado"
    NOT_RENEWED = "No renovado"
    REISSUED = "Reexpedido"
    STOLEN = "Hurtado"
    LOST = "Extraviado"
    NOT_DELIVERED = "No entregado"
    RETURNED = "Devuelto"
    UNKNOWN = "Desconocido"
