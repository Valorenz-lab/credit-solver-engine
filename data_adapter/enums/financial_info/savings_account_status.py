from enum import StrEnum


class SavingsAccountStatus(StrEnum):
    ACTIVE = "Activa - Vigente"
    CANCELLED_BAD_USE = "Cancelada Mal manejo - Cerrada"
    PAID_OFF = "Saldada - Cerrada"
    SEIZED = "Embargada - Vigente"
    SEIZED_ACTIVE = "Embargada-Activa - Vigente"
    INACTIVE = "Inactiva - Cerrada"
    UNKNOWN = "Desconocido"
