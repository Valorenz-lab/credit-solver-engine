from typing import Optional

from data_adapter.transformers.shared_transformers import (
    transform_account_state_savings,
    transform_credit_rating,
    transform_ownership_situation,
    transform_sector,
)
from data_adapter.xml_adapter.models.bank_account_models import BankAccount, BankAccountState, BankAccountValue
from data_adapter.xml_adapter.types import (
    SerializedBankAccount,
    SerializedBankAccountState,
    SerializedBankAccountValue,
)


def serialize_bank_account(account: BankAccount) -> SerializedBankAccount:
    return {
        "lender": account.lender,
        "account_number": account.account_number,
        "account_class": account.account_class,
        "opened_date": account.opened_date,
        "rating": account.rating,
        "rating_label": transform_credit_rating(account.rating).value,
        "ownership_situation": account.ownership_situation,
        "ownership_situation_label": transform_ownership_situation(account.ownership_situation).value,
        "is_blocked": account.is_blocked,
        "office": account.office,
        "city": account.city,
        "sector": account.sector,
        "sector_label": transform_sector(account.sector).value,
        "value": _serialize_bank_account_value(account.value) if account.value is not None else None,
        "state": _serialize_bank_account_state(account.state) if account.state is not None else None,
    }


def _serialize_bank_account_value(v: BankAccountValue) -> SerializedBankAccountValue:
    return {
        "currency_code": v.currency_code,
        "currency_label": None,
        "date": v.date,
        "rating": v.rating,
        "rating_label": transform_credit_rating(v.rating).value,
    }


def _serialize_bank_account_state(s: BankAccountState) -> SerializedBankAccountState:
    return {
        "code": s.code,
        "label": transform_account_state_savings(s.code).value,
        "date": s.date,
    }
