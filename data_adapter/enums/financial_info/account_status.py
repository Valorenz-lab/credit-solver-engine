


from enum import StrEnum


class AccountStatus(StrEnum):
    ENTITY_NO_REPORT = "Entidad no reportó"
    ON_TIME = "Al día"
    OVERDUE_DEBT = "En Mora"
    FULL_PAYMENT = "Pago Total"
    JUDICIAL_PAYMENT = "Pago Judicial"
    DOUBTFUL_COLLECTION = "Dudoso Recaudo"
    WRITTEN_OFF = "Castigada"
    DATION_IN_PAYMENT = "Dación en Pago"
    VOLUNTARY_CANCELLED = "Cancelada Voluntariamente"
    CANCELLED_DUE_TO_MISMANAGEMENT = "Cancelada por mal manejo"
    CANCELLED_DUE_TO_STATUTE_OF_LIMITATIONS = "Cancelada por prescripción"
    CANCELLED_BY_INSTITUTION = "Cancelada por la entidad"
    CANCELLED_DUE_TO_RESTRUCTURING_REFINANCING = "Cancelada por reestructuración/refinanciación"
    UNKNOWN = "Desconocido"