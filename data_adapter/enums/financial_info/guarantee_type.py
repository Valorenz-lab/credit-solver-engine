from enum import StrEnum


class GuaranteeType(StrEnum):
    """Tabla 11 — Tipo de garantía en hábito de pago obligaciones vigentes."""
    SIN_GARANTIA = "Sin garantía"
    ADMISIBLE = "Admisible"
    OTRAS_IDONEAS = "Otras garantías idóneas"
    NO_IDONEA = "No idónea"
    BIENES_RAICES = "Bienes raíces comerciales y residenciales, fiducias hipotecarias"
    OTRAS_PRENDAS = "Otras prendas"
    PIGNORACION_RENTAS = "Pignoración de rentas de entidades territoriales"
    GARANTIA_SOBERANA = "Garantía soberana de la nación"
    CONTRATO_FIDUCIA = "Contratos irrevocables de fiducia mercantil de garantía"
    FNG = "Garantías otorgadas por el Fondo Nacional de Garantías S.A."
    CARTA_CREDITO = "Cartas de crédito"
    FAG = "FAG (Fondo Agropecuario de Garantías)"
    PERSONAL = "Personal"
    LEASING_NO_INMOBILIARIO = "Bienes dados en leasing diferente a inmobiliario"
    LEASING_INMOBILIARIO = "Bienes dados en leasing inmobiliario"
    PRENDA_TITULO = "Prenda sobre títulos valores emitidos por instituciones financieras"
    DEPOSITOS = "Depósitos de dinero en garantía colateral"
    SEGURO_CREDITO = "Seguros de crédito"
    UNKNOWN = "Desconocido"
