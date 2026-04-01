from typing import Optional

from data_adapter.debug_tracer import record_unknown
from data_adapter.enums.financial_info.credit_card_class import CreditCardClass
from data_adapter.enums.financial_info.credit_card_franchise import CreditCardFranchise
from data_adapter.enums.financial_info.plastic_status import PlasticStatus


def transform_franchise(
    value: Optional[str],
    *,
    xml_node: str = "Caracteristicas",
    xml_attribute: str = "franquicia",
    record_type: str = "",
    record_context: Optional[dict[str, str]] = None,
) -> CreditCardFranchise:
    if not value or value.strip() == "":
        record_unknown(
            "transform_franchise",
            value,
            xml_node,
            xml_attribute,
            record_type,
            record_context or {},
        )
        return CreditCardFranchise.UNKNOWN
    mapping: dict[str, CreditCardFranchise] = {
        "1": CreditCardFranchise.AMERICAN_EXPRESS,
        "2": CreditCardFranchise.VISA,
        "3": CreditCardFranchise.MASTERCARD,
        "4": CreditCardFranchise.DINERS,
        "5": CreditCardFranchise.PRIVATE,
        "0": CreditCardFranchise.UNKNOWN,
    }
    result = mapping.get(value.strip())
    if result is None:
        record_unknown(
            "transform_franchise",
            value,
            xml_node,
            xml_attribute,
            record_type,
            record_context or {},
        )
        return CreditCardFranchise.UNKNOWN
    return result


def transform_credit_card_class(
    value: Optional[str],
    *,
    xml_node: str = "Caracteristicas",
    xml_attribute: str = "clase",
    record_type: str = "",
    record_context: Optional[dict[str, str]] = None,
) -> CreditCardClass:
    if not value or value.strip() == "":
        record_unknown(
            "transform_credit_card_class",
            value,
            xml_node,
            xml_attribute,
            record_type,
            record_context or {},
        )
        return CreditCardClass.UNKNOWN
    mapping: dict[str, CreditCardClass] = {
        "1": CreditCardClass.CLASSIC,
        "2": CreditCardClass.GOLD,
        "3": CreditCardClass.PLATINUM,
        "4": CreditCardClass.OTHER,
        "0": CreditCardClass.UNKNOWN,
    }
    result = mapping.get(value.strip())
    if result is None:
        record_unknown(
            "transform_credit_card_class",
            value,
            xml_node,
            xml_attribute,
            record_type,
            record_context or {},
        )
        return CreditCardClass.UNKNOWN
    return result


def transform_plastic_status(
    value: Optional[str],
    *,
    xml_node: str = "EstadoPlastico",
    xml_attribute: str = "codigo",
    record_type: str = "",
    record_context: Optional[dict[str, str]] = None,
) -> PlasticStatus:
    if not value or value.strip() == "":
        record_unknown(
            "transform_plastic_status",
            value,
            xml_node,
            xml_attribute,
            record_type,
            record_context or {},
        )
        return PlasticStatus.UNKNOWN
    mapping: dict[str, PlasticStatus] = {
        "1": PlasticStatus.DELIVERED,
        "2": PlasticStatus.RENEWED,
        "3": PlasticStatus.NOT_RENEWED,
        "4": PlasticStatus.REISSUED,
        "5": PlasticStatus.STOLEN,
        "6": PlasticStatus.LOST,
        "7": PlasticStatus.NOT_DELIVERED,
        "8": PlasticStatus.RETURNED,
        "0": PlasticStatus.UNKNOWN,
    }
    result = mapping.get(value.strip())
    if result is None:
        record_unknown(
            "transform_plastic_status",
            value,
            xml_node,
            xml_attribute,
            record_type,
            record_context or {},
        )
        return PlasticStatus.UNKNOWN
    return result
