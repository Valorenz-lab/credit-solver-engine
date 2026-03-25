from enum import StrEnum


class PaymentBehavior(StrEnum):
    """Table 5 — Payment behavior (comportamiento field). Each character represents one month."""
    ON_TIME = "Al día"
    PAST_DUE_30 = "Mora 30 días"
    PAST_DUE_60 = "Mora 60 días"
    PAST_DUE_90 = "Mora 90 días"
    PAST_DUE_120 = "Mora 120 días"
    PAST_DUE_150 = "Mora 150 días"
    PAST_DUE_180 = "Mora 180 días"
    DOUBTFUL_COLLECTION = "Dudoso recaudo"
    WRITTEN_OFF = "Cartera castigada"
    NO_INFORMATION = "Sin información"
