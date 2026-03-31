from enum import StrEnum


class CardholderRole(StrEnum):
    PRINCIPAL = "Principal"
    AUTHORIZED_USER_CARD = "Amparada"
    CO_HOLDER = "Cotitular"
    UNKNOWN = "Desconocido"
