


from enum import StrEnum


class AccountCondition(StrEnum):
    """Tabla 4 — Estado actual de una obligación crediticia (EstadoCuenta.codigo).

    Códigos vigentes (abiertos): 01, 13-41, 45, 47
    Códigos cerrados: 02-12, 46, 49
    """
    # Vigente
    ON_TIME = "Al día"
    OVERDUE_DEBT = "En Mora"
    WRITTEN_OFF = "Castigada"
    DOUBTFUL_COLLECTION = "Dudoso Recaudo"
    # Cerrada
    CARD_NOT_DELIVERED = "Tarjeta no entregada"
    CANCELLED_DUE_TO_MISMANAGEMENT = "Cancelada por mal manejo"
    CARD_STOLEN = "Tarjeta robada"
    VOLUNTARY_CANCELLED = "Cancelada Voluntariamente"
    CANCELLED_BY_INSTITUTION = "Cancelada por la entidad"
    CARD_LOST = "Tarjeta extraviada"
    FULL_PAYMENT = "Pago Total"
    JUDICIAL_PAYMENT = "Cartera Recuperada"
    CARD_NOT_RENEWED = "Tarjeta no renovada"
    # Sin equivalente directo en Tabla 4 (compatibilidad)
    ENTITY_NO_REPORT = "Entidad no reportó"
    DATION_IN_PAYMENT = "Dación en Pago"
    CANCELLED_DUE_TO_STATUTE_OF_LIMITATIONS = "Cancelada por prescripción"
    CANCELLED_DUE_TO_RESTRUCTURING_REFINANCING = "Cancelada por reestructuración/refinanciación"
    UNKNOWN = "Desconocido"