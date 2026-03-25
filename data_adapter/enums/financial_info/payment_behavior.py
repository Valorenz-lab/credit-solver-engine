from enum import StrEnum


class PaymentBehavior(StrEnum):
    """Tabla 5 — Comportamiento de pago. Cada carácter del vector comportamiento representa un mes."""
    AL_DIA = "Al día"
    MORA_30 = "Mora 30 días"
    MORA_60 = "Mora 60 días"
    MORA_90 = "Mora 90 días"
    MORA_120 = "Mora 120 días"
    MORA_150 = "Mora 150 días"
    MORA_180 = "Mora 180 días"
    DUDOSO_RECAUDO = "Dudoso recaudo"
    CASTIGADA = "Cartera castigada"
    SIN_INFORMACION = "Sin información"
