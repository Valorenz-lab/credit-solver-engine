from typing import Optional

from data_adapter.enums.financial_info.credit_card_class import CreditCardClass
from data_adapter.enums.financial_info.credit_card_franchise import CreditCardFranchise
from data_adapter.enums.financial_info.plastic_state import PlasticState


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


def transform_plastic_state(value: Optional[str]) -> PlasticState:
    if not value or value.strip() == "":
        return PlasticState.UNKNOWN
    mapping = {
        "1": PlasticState.DELIVERED,
        "2": PlasticState.RENEWED,
        "3": PlasticState.NOT_RENEWED,
        "4": PlasticState.REISSUED,
        "5": PlasticState.STOLEN,
        "6": PlasticState.LOST,
        "7": PlasticState.NOT_DELIVERED,
        "8": PlasticState.RETURNED,
        "0": PlasticState.UNKNOWN,
    }
    return mapping.get(value.strip(), PlasticState.UNKNOWN)
