from enum import StrEnum

class Gender(StrEnum):
    MALE = "Hombre"
    FEMALE = "Mujer"
    UNKNOWN = "Desconocido"

class TypesID(StrEnum):
    CC = "C.C - Cédula de Ciudadanía"
    NIT = "NIT - Número de identificación tributaria"
    PJE = "PJE - Persona jurídica del extranjero"
    CE = "C.E - Cédula de Extranjería"
    PAS = "PAS - Pasaporte"
    CD = "C.D - Carné Diplomático"
    TI = "T.I - Tarjeta de Identidad"
    DNI = "D.N.I - Documento Nacional de Identidad"
    PEP = "P.E.P - Permiso Especial de Permanencia"
    UNDEFINED = "Indefinido"

class ID_VALIDITY(StrEnum):
    VALID = "Vigente"
    SUSPENDED = "Suspendida"
    DECEASED = "Fallecido"
    CANCELED = "Cancelada"
    NOT_ISSUED = "No expedida"
    UNDEFINED = "Indefinido"
    IN_PROCESS = "En proceso"

