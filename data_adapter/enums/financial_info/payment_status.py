from enum import StrEnum


class PaymentStatus(StrEnum):
    """Table 4 — Accumulated payment status (EstadoPago.codigo). Two-digit codes observed in real Datacredito XMLs."""

    NORMAL = "Normal"
    PAST_DUE_30 = "Mora 30 días"
    PAST_DUE_60 = "Mora 60 días"
    PAST_DUE_90 = "Mora 90 días"
    PAST_DUE_120_PLUS = "Mora más de 120 días"
    WRITTEN_OFF = "Cartera castigada"
    DOUBTFUL_COLLECTION = "Dudoso recaudo"
    PAYMENT_AGREEMENT = "Acuerdo de pago"
    RESTRUCTURED = "Reestructurada / Normalizada"
    CREDIT_BALANCE = "Saldo a favor"
    UNKNOWN = "Desconocido"
