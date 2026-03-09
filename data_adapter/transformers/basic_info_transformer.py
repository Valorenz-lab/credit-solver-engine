

from typing import Optional

from data_adapter.enums.basic_info_enums import ID_VALIDITY, Gender, TypesID


def transform_gender(value: Optional[str]) -> Gender:
    """Transform numeric codes to gender."""
    if value is None or not value or value.strip() == "":
        return Gender.UNKNOWN
    try:
        code = int(value)
    except ValueError:
        return Gender.UNKNOWN
    mapping = {4: Gender.FEMALE, 3: Gender.MALE}
    return mapping.get(code, Gender.UNKNOWN)


def transform_id_validity(value: str) -> ID_VALIDITY:
    """Transform numeric codes to ID validity status."""
    if not value or value.strip() == "":
        return ID_VALIDITY.UNDEFINED
    try:
        code = int(value)
    except ValueError:
        return ID_VALIDITY.UNDEFINED

    direct_map = {
        0:  ID_VALIDITY.VALID,
        12: ID_VALIDITY.SUSPENDED,
        21: ID_VALIDITY.DECEASED,
        29: ID_VALIDITY.CANCELED,
        99: ID_VALIDITY.IN_PROCESS,
    }
    
    if code in direct_map:
        return direct_map[code]

    if code < 30:
        return ID_VALIDITY.CANCELED
    elif 30 <= code < 60:
        return ID_VALIDITY.NOT_ISSUED
    elif 60 <= code < 99:
        return ID_VALIDITY.UNDEFINED  
    
    return ID_VALIDITY.UNDEFINED


def transform_id_type(value: str) -> TypesID:
    """Transform numeric codes to ID types."""
    if not value or value.strip() == "":
        return TypesID.UNDEFINED
    try:
        code = int(value)
    except ValueError:
        return TypesID.UNDEFINED

    mapping = {
        1: TypesID.CC,
        2: TypesID.NIT,
        3: TypesID.PJE,
        4: TypesID.CE,
        5: TypesID.PAS,
        6: TypesID.CD,
        7: TypesID.TI,
        8: TypesID.DNI,
        9: TypesID.PEP
    }
    return mapping.get(code, TypesID.UNDEFINED)
