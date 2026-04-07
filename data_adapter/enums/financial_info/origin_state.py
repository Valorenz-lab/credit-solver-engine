from enum import StrEnum


class OriginState(StrEnum):
    """Tabla 44 — Estado de la obligación al momento de originarse (EstadoOrigen.codigo).
    Se aplica cuando la cuenta no está bloqueada (ver sección 7.1.1 del Manual Insumos XML v1.6.4).

    ADVERTENCIA — VALORES INFERIDOS:
    Los códigos EO=5 y EO=6 fueron observados en XMLs reales pero la Tabla 44
    oficial (Manual HDC 1.6.4) no está disponible. Sus etiquetas y nombres son inferidos
    del contexto observado en los datos (ver ANALISIS_EXTRACCION.md).
    PUEDEN SER INCORRECTOS. Actualizar en cuanto se obtenga el documento de tablas
    de referencia de Datacredito (paquete de integración HDC 1.6.4).
    """

    NORMAL = "Normal"
    RESTRUCTURED = "Reestructurado"
    REFINANCED = "Refinanciado"
    TRANSFERRED = "Trasladado"
    PURCHASED = "Comprado"
    UNKNOWN = "Desconocido"

    # =====================================================================
    # VALORES INFERIDOS — PENDIENTES DE VERIFICACIÓN CON TABLA 44 (HDC 1.6.4)
    # Fuente de inferencia: ANALISIS_EXTRACCION.md — patrones en 25 XMLs reales.
    # PUEDEN SER INCORRECTOS. Actualizar al obtener la Tabla 44 oficial.
    # =====================================================================

    # EO=5: BANCO BOGOTA VIVIENDA — cuenta CAV (crédito de vivienda), EC=05
    #       (voluntariamente cancelada), EP=47 (dudoso recaudo), mora $3.57M sobre $46.78M.
    # Inferencia: régimen especial de origen, posiblemente hipotecario o con subsidio.
    # Riesgo bajo-medio: EstadoOrigen es contextual, no determina el estado actual.
    SPECIAL_REGIME = "Régimen especial de origen"

    # EO=6: GASCARIBE — cuenta de servicio público (gas natural domiciliario), EC=01 (al día).
    # Inferencia: origen como contrato de servicio público domiciliario.
    PUBLIC_SERVICE = "Servicio público"
