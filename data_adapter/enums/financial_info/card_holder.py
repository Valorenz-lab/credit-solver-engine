

from enum import StrEnum


class CardHolder(StrEnum):
    PRINCIPAL = "Principal",
    AUTHORIZED_USER_CARD = "Amparada"
    CO_TITULAR = "Cotitular"
    UNKNOWN = "Desconocido"