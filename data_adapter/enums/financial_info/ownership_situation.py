from enum import StrEnum


class OwnershipSituation(StrEnum):
    NORMAL = "Normal"
    CONCORDAT = "Concordato"
    FORCED_LIQUIDATION = "Liquidación forzosa"
    VOLUNTARY_LIQUIDATION = "Liquidación voluntaria"
    REORGANIZATION = "Reorganización"
    LAW_550 = "Ley 550"
    LAW_1116 = "Ley 1116"
    OTHER = "Otro"
    UNKNOWN = "Desconocido"
