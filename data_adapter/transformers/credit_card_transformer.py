from typing import Optional

from data_adapter.enums.financial_info.credit_card_class import CreditCardClass
from data_adapter.enums.financial_info.credit_card_franchise import CreditCardFranchise
from data_adapter.enums.financial_info.plastic_status import PlasticStatus


def transform_franchise(value: Optional[str]) -> CreditCardFranchise:
    if not value or value.strip() == "":
        return CreditCardFranchise.UNKNOWN
    mapping = {
        "1": CreditCardFranchise.AMERICAN_EXPRESS,
        "2": CreditCardFranchise.VISA,
        "3": CreditCardFranchise.MASTERCARD,
        "4": CreditCardFranchise.DINERS,
        "5": CreditCardFranchise.PRIVATE,
        "0": CreditCardFranchise.UNKNOWN,
    }
    return mapping.get(value.strip(), CreditCardFranchise.UNKNOWN)


def transform_credit_card_class(value: Optional[str]) -> CreditCardClass:
    if not value or value.strip() == "":
        return CreditCardClass.UNKNOWN
    mapping = {
        "1": CreditCardClass.CLASSIC,
        "2": CreditCardClass.GOLD,
        "3": CreditCardClass.PLATINUM,
        "4": CreditCardClass.OTHER,
        "0": CreditCardClass.UNKNOWN,
    }
    return mapping.get(value.strip(), CreditCardClass.UNKNOWN)


def transform_plastic_status(value: Optional[str]) -> PlasticStatus:
    if not value or value.strip() == "":
        return PlasticStatus.UNKNOWN
    mapping = {
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
    return mapping.get(value.strip(), PlasticStatus.UNKNOWN)
