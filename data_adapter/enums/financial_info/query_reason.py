from enum import StrEnum


class QueryReason(StrEnum):
    """Tabla 23 — Razón de la consulta (Consulta/razon)."""
    RAZON_DESCONOCIDA = "Razón desconocida"
    SOLICITUD_PRODUCTO = "Solicitud de producto"
    REVISION_PORTAFOLIO_ENTIDAD = "Revisión del portafolio por parte de la entidad"
    REVISION_PORTAFOLIO_CIUDADANO = "Revisión del portafolio por parte del ciudadano"
    SOLICITUD_PRODUCTO_B = "Solicitud de producto"
    CONSULTA_INTERNET = "Consulta del ciudadano por Internet"
    CONSULTA_CAS_VIRTUAL = "Consulta del ciudadano por CAS Virtual"
    POR_DEFINIR_07 = "Por definir (07)"
    POR_DEFINIR_08 = "Por definir (08)"
    UNKNOWN = "Desconocido"
