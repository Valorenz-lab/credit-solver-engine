from enum import StrEnum


class GuaranteeType(StrEnum):
    """Table 11 — Guarantee type (garantia field in CuentaCartera/Caracteristicas)."""
    NO_GUARANTEE = "Sin garantía"
    ADMISSIBLE = "Admisible"
    OTHER_SUITABLE = "Otras garantías idóneas"
    NOT_SUITABLE = "No idónea"
    REAL_ESTATE = "Bienes raíces comerciales y residenciales, fiducias hipotecarias"
    OTHER_COLLATERAL = "Otras prendas"
    REVENUE_PLEDGE = "Pignoración de rentas de entidades territoriales"
    SOVEREIGN_GUARANTEE = "Garantía soberana de la nación"
    TRUST_CONTRACT = "Contratos irrevocables de fiducia mercantil de garantía"
    FNG = "Garantías otorgadas por el Fondo Nacional de Garantías S.A."
    LETTER_OF_CREDIT = "Cartas de crédito"
    FAG = "FAG (Fondo Agropecuario de Garantías)"
    PERSONAL = "Personal"
    NON_REAL_ESTATE_LEASING = "Bienes dados en leasing diferente a inmobiliario"
    REAL_ESTATE_LEASING = "Bienes dados en leasing inmobiliario"
    SECURITIES_PLEDGE = "Prenda sobre títulos valores emitidos por instituciones financieras"
    CASH_DEPOSITS = "Depósitos de dinero en garantía colateral"
    CREDIT_INSURANCE = "Seguros de crédito"
    UNKNOWN = "Desconocido"
