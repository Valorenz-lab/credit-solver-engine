

from typing import Optional

from data_adapter.enums.basic_info.gender import Gender
from data_adapter.enums.basic_info.identification_status import IdentificationStatus
from data_adapter.enums.basic_info.identification_document_type import IdentificationDocumentType



def transform_gender(value: Optional[str]) -> Gender:
    """Transform numeric codes to gender."""
    if value is None or not value or value.strip() == "":
        return Gender.UNKNOWN
    try:
        code = int(value)
    except ValueError:
        return Gender.UNKNOWN
    mapping = {3: Gender.FEMALE, 4: Gender.MALE}
    return mapping.get(code, Gender.UNKNOWN)


def transform_id_validity(value: Optional[str]) -> IdentificationStatus:
    """Transform numeric codes to ID validity status."""
    if not value or value.strip() == "":
        return IdentificationStatus.UNDEFINED
    try:
        code = int(value)
    except ValueError:
        return IdentificationStatus.UNDEFINED

    direct_map = {
        0:  IdentificationStatus.VALID,
        12: IdentificationStatus.SUSPENDED,
        21: IdentificationStatus.DECEASED,
        29: IdentificationStatus.CANCELED,
        99: IdentificationStatus.IN_PROCESS,
    }

    if code in direct_map:
        return direct_map[code]

    if code < 30:
        return IdentificationStatus.CANCELED
    elif 30 <= code < 60:
        return IdentificationStatus.NOT_ISSUED
    elif 60 <= code < 99:
        return IdentificationStatus.UNDEFINED

    return IdentificationStatus.UNDEFINED


def transform_id_type(value: Optional[str]) -> IdentificationDocumentType:
    """Transform numeric codes to ID types."""
    if not value or value.strip() == "":
        return IdentificationDocumentType.UNDEFINED
    try:
        code = int(value)
    except ValueError:
        return IdentificationDocumentType.UNDEFINED

    mapping = {
        1: IdentificationDocumentType.CC,
        2: IdentificationDocumentType.NIT,
        3: IdentificationDocumentType.PJE,
        4: IdentificationDocumentType.CE,
        5: IdentificationDocumentType.PAS,
        6: IdentificationDocumentType.CD,
        7: IdentificationDocumentType.TI,
        8: IdentificationDocumentType.DNI,
        9: IdentificationDocumentType.PEP
    }
    return mapping.get(code, IdentificationDocumentType.UNDEFINED)
