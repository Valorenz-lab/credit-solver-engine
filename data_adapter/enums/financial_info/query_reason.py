from enum import StrEnum


class QueryReason(StrEnum):
    """Table 23 — Query reason (razon field in Consulta)."""

    UNKNOWN_REASON = "Razón desconocida"
    PRODUCT_REQUEST_01 = "Solicitud de producto (01)"
    ENTITY_PORTFOLIO_REVIEW = "Revisión del portafolio por parte de la entidad"
    CITIZEN_PORTFOLIO_REVIEW = "Revisión del portafolio por parte del ciudadano"
    PRODUCT_REQUEST_04 = "Solicitud de producto (04)"
    CITIZEN_INTERNET_QUERY = "Consulta del ciudadano por Internet"
    CITIZEN_CAS_QUERY = "Consulta del ciudadano por CAS Virtual"
    UNDEFINED_07 = "Por definir (07)"
    UNDEFINED_08 = "Por definir (08)"
    UNKNOWN = "Desconocido"
