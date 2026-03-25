from enum import StrEnum


class CurrentDebtState(StrEnum):
    """
    Estado actual de una obligación en <EndeudamientoActual/Cuenta>.
    Texto libre generado por Datacredito — se mapean los valores observados en los XMLs.
    """
    AL_DIA = "Al día"
    MORA_30 = "En mora 30 días"
    MORA_60 = "En mora 60 días"
    MORA_90 = "En mora 90 días"
    MORA_120 = "En mora 120 días o más"
    CASTIGADA = "Cartera castigada"
    DUDOSO_RECAUDO = "Dudoso recaudo"
    UNKNOWN = "Desconocido"
