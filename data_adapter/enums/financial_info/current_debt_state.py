from enum import StrEnum


class CurrentDebtState(StrEnum):
    """Current state of an obligation in EndeudamientoActual/Cuenta. Free text from Datacredito — mapped from observed XML values."""
    ON_TIME = "Al día"
    PAST_DUE_30 = "En mora 30 días"
    PAST_DUE_60 = "En mora 60 días"
    PAST_DUE_90 = "En mora 90 días"
    PAST_DUE_120 = "En mora 120 días o más"
    WRITTEN_OFF = "Cartera castigada"
    DOUBTFUL_COLLECTION = "Dudoso recaudo"
    UNKNOWN = "Desconocido"
