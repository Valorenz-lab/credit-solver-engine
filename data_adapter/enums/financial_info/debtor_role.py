

from enum import StrEnum


class DebtorRole(StrEnum):
    DEBTOR = "Deudor"
    CO_DEBTOR ="Codeudor"
    CO_SINGER = "Avalista"
    SOLIDARY_DEBTOR = "Deudor solidario"
    CO_TENANT = "Coarrendatario"
    OTHER_GUARANTORS = "Otros Garantes"
    GUARANTOR = "Fiador"
    NOT_APPLICABLE = "No aplica"
    CO_HOLDER = "Cotitular"
    COMMUNAL = "Comunal (solo para cuentas de Microcrédito-MCR)"
    UNKNOWN = "Desconocido"