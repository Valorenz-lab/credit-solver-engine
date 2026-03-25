from enum import StrEnum


class PaymentStatus(StrEnum):
    """
    Tabla 4 — Estado de pago acumulado (EstadoPago.codigo).
    Códigos de 2 dígitos observados en XMLs reales de Datacredito.
    """
    NORMAL = "Normal"
    MORA_30 = "Mora 30 días"
    MORA_60 = "Mora 60 días"
    MORA_90 = "Mora 90 días"
    MORA_120_MAS = "Mora más de 120 días"
    CASTIGADA = "Cartera castigada"
    DUDOSO_RECAUDO = "Dudoso recaudo"
    ACUERDO_PAGO = "Acuerdo de pago"
    REESTRUCTURADA = "Reestructurada / Normalizada"
    SALDO_A_FAVOR = "Saldo a favor"
    UNKNOWN = "Desconocido"
