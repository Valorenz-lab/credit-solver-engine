from enum import StrEnum


class PaymentMethod(StrEnum):
    CURRENT = "Vigente"
    VOLUNTARY = "Pago Voluntario"
    EXECUTIVE = "Proceso ejecutivo"
    PAYMENT_ORDER = "Mandamiento de pago"
    RESTRUCTURING = "Reestructuración"
    DATION_IN_PAYMENT = "Dación en pago"
    CESSION = "Cesión"
    DONATION = "Donación"
    UNKNOWN = "Desconocido"
