from typing import Optional

from data_adapter.enums.financial_info.account_state_savings import AccountStateSavings
from data_adapter.enums.financial_info.credit_rating import CreditRating
from data_adapter.enums.financial_info.currency import Currency
from data_adapter.enums.financial_info.origin_state import OriginState
from data_adapter.enums.financial_info.ownership_situation import OwnershipSituation
from data_adapter.enums.financial_info.payment_method import PaymentMethod
from data_adapter.enums.financial_info.sector import Sector


def transform_sector(value: Optional[str]) -> Sector:
    if not value or value.strip() == "":
        return Sector.UNKNOWN
    mapping = {
        "1": Sector.FINANCIAL,
        "2": Sector.COOPERATIVE,
        "3": Sector.REAL,
        "4": Sector.TELECOM,
        "0": Sector.UNKNOWN,
    }
    return mapping.get(value.strip(), Sector.UNKNOWN)


def transform_credit_rating(value: Optional[str]) -> CreditRating:
    if not value or value.strip() == "":
        return CreditRating.UNKNOWN
    mapping = {
        "1": CreditRating.A,
        "2": CreditRating.B,
        "3": CreditRating.C,
        "4": CreditRating.D,
        "5": CreditRating.E,
        "6": CreditRating.AA,
        "7": CreditRating.BB,
        "8": CreditRating.CC,
        "9": CreditRating.K,
        "0": CreditRating.UNKNOWN,
    }
    return mapping.get(value.strip(), CreditRating.UNKNOWN)


def transform_account_state_savings(value: Optional[str]) -> AccountStateSavings:
    if not value or value.strip() == "":
        return AccountStateSavings.UNKNOWN
    mapping = {
        "01": AccountStateSavings.ACTIVE,
        "02": AccountStateSavings.CANCELLED_BAD_USE,
        "05": AccountStateSavings.PAID_OFF,
        "06": AccountStateSavings.SEIZED,
        "07": AccountStateSavings.SEIZED_ACTIVE,
        "09": AccountStateSavings.INACTIVE,
        "00": AccountStateSavings.UNKNOWN,
    }
    return mapping.get(value.strip(), AccountStateSavings.UNKNOWN)


def transform_ownership_situation(value: Optional[str]) -> OwnershipSituation:
    if not value or value.strip() == "":
        return OwnershipSituation.UNKNOWN
    mapping = {
        "0": OwnershipSituation.NORMAL,
        "1": OwnershipSituation.CONCORDATO,
        "2": OwnershipSituation.FORCED_LIQUIDATION,
        "3": OwnershipSituation.VOLUNTARY_LIQUIDATION,
        "4": OwnershipSituation.REORGANIZATION,
        "5": OwnershipSituation.LAW_550,
        "6": OwnershipSituation.LAW_1116,
        "7": OwnershipSituation.OTHER,
        "99": OwnershipSituation.UNKNOWN,
    }
    return mapping.get(value.strip(), OwnershipSituation.UNKNOWN)


def transform_origin_state(value: Optional[str]) -> OriginState:
    if not value or value.strip() == "":
        return OriginState.UNKNOWN
    mapping = {
        "0": OriginState.NORMAL,
        "1": OriginState.RESTRUCTURED,
        "2": OriginState.REFINANCED,
        "3": OriginState.TRANSFERRED,
        "4": OriginState.PURCHASED,
        "99": OriginState.UNKNOWN,
    }
    return mapping.get(value.strip(), OriginState.UNKNOWN)


def transform_payment_method(value: Optional[str]) -> PaymentMethod:
    if not value or value.strip() == "":
        return PaymentMethod.UNKNOWN
    mapping = {
        "0": PaymentMethod.CURRENT,
        "1": PaymentMethod.VOLUNTARY,
        "2": PaymentMethod.EXECUTIVE,
        "3": PaymentMethod.PAYMENT_ORDER,
        "4": PaymentMethod.RESTRUCTURING,
        "5": PaymentMethod.DACION,
        "6": PaymentMethod.CESSION,
        "7": PaymentMethod.DONATION,
        "99": PaymentMethod.UNKNOWN,
    }
    return mapping.get(value.strip(), PaymentMethod.UNKNOWN)


def transform_currency(value: Optional[str]) -> Currency:
    if not value or value.strip() == "":
        return Currency.UNKNOWN
    mapping = {
        "1": Currency.LEGAL,
        "2": Currency.FOREIGN,
        "0": Currency.UNKNOWN,
    }
    return mapping.get(value.strip(), Currency.UNKNOWN)
