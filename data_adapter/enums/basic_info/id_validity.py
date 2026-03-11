from enum import StrEnum


class ID_VALIDITY(StrEnum):
    VALID = "Vigente"
    SUSPENDED = "Suspendida"
    DECEASED = "Fallecido"
    CANCELED = "Cancelada"
    NOT_ISSUED = "No expedida"
    UNDEFINED = "Indefinido"
    IN_PROCESS = "En proceso"

