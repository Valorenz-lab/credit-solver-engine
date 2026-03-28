from enum import StrEnum


class IdentificationStatus(StrEnum):
    VALID = "Vigente"
    SUSPENDED = "Suspendida"
    DECEASED = "Fallecido"
    CANCELED = "Cancelada"
    NOT_ISSUED = "No expedida"
    UNDEFINED = "Indefinido"
    IN_PROCESS = "En proceso"

