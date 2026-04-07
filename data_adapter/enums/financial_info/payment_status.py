from enum import StrEnum


class PaymentStatus(StrEnum):
    """Tabla 4 — Estado acumulado de pago (EstadoPago.codigo). Códigos de dos dígitos observados en XMLs reales de Datacredito.

    ADVERTENCIA — VALORES INFERIDOS:
    Los códigos EP=14, 17, 19, 37 y 41 fueron observados en XMLs reales pero la Tabla 4
    oficial (Manual HDC 1.6.4) no está disponible. Sus etiquetas y nombres son inferidos
    de los patrones observados en los datos (ver ANALISIS_EXTRACCION.md).
    PUEDEN SER INCORRECTOS. Actualizar en cuanto se obtenga el documento de tablas
    de referencia de Datacredito (paquete de integración HDC 1.6.4).
    """

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

    # =====================================================================
    # VALORES INFERIDOS — PENDIENTES DE VERIFICACIÓN CON TABLA 4 (HDC 1.6.4)
    # Fuente de inferencia: ANALISIS_EXTRACCION.md — patrones en 25 XMLs reales.
    # PUEDEN SER INCORRECTOS. Actualizar al obtener la Tabla 4 oficial.
    # =====================================================================

    # EP=14: CLARO SERV MOV — PortfolioAccount, EC=01 (al día), sin saldo ni mora.
    # Inferencia: variante de estado "al día" para cuentas telecom sin saldo activo.
    CURRENT_NO_BALANCE = "Al día sin saldo"

    # EP=17: CLARO TEC MOV — PortfolioAccount, EC=02 (cerrada), mora $129k.
    # Inferencia: cuenta cerrada con mora pendiente en sector telecom.
    CLOSED_IN_ARREARS = "Cerrada en mora"

    # EP=19: CREDIEXPRESS POPAYAN — PortfolioAccount, EC=02, saldo=mora (100% en mora).
    # Inferencia: estado de cobro externo en microfinanzas. Riesgo medio.
    EXTERNAL_COLLECTION = "Cobro externo"

    # EP=37: BBVA COLOMBIA — CreditCard, EC=02, mora > saldo (mora excede capital original).
    # Inferencia: estado de cobro avanzado en tarjeta bancaria. Riesgo medio.
    SEVERE_COLLECTION = "Cobro severo"

    # EP=41: ORI BANCOLOMBI PAUTO REINTEGR / CRJA S.A / COOBOLARQUI LIBRANZA
    #        PortfolioAccount, EC=02, saldo=mora (100% en mora) en banca, consumo y libranza.
    # Inferencia: cobro judicial o cartera cedida. Riesgo ALTO — afecta libranza.
    JUDICIAL_COLLECTION = "Cobro judicial"
