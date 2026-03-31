from enum import StrEnum


class PaymentFrequency(StrEnum):
    NO_INFORMED = "No informado"
    MONTHLY = "Mensual"
    BIMONTHLY = "Bimestral"
    QUARTERLY = "Trimestral"
    BI_ANNUALLY = "Semestral"
    ANNUALLY = "Anual"
    AT_EXPIRATION = "Al vencimiento"
    OTHER = "Otro"
    UNKNOWN = "Desconocido"
