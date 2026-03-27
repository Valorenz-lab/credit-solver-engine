

from data_adapter.transformers.shared_transformers import (
    transform_account_state_savings,
    transform_credit_rating,
    transform_ownership_situation,
    transform_sector,
)
from data_adapter.xml_adapter.models.bank_account_models import BankAccountState, BankAccountValue
from data_adapter.xml_adapter.models.checking_account_models import (
    CheckingAccount,
    CheckingAccountOverdraft,
)
from data_adapter.xml_adapter.types import (
    SerializedBankAccountState,
    SerializedBankAccountValue,
    SerializedCheckingAccount,
    SerializedCheckingAccountOverdraft,
)


def serialize_checking_account(account: CheckingAccount) -> SerializedCheckingAccount:
    return {
        "lender": account.lender,
        "account_number": account.account_number,
        "account_class": account.account_class,
        "opened_date": account.opened_date,
        "ownership_situation": account.ownership_situation,
        "ownership_situation_label": transform_ownership_situation(account.ownership_situation).value,
        "is_blocked": account.is_blocked,
        "office": account.office,
        "city": account.city,
        "dane_city_code": account.dane_city_code,
        "sector": account.sector,
        "sector_label": transform_sector(account.sector).value,
        "subscriber_code": account.subscriber_code,
        "entity_id_type": account.entity_id_type,
        "entity_id": account.entity_id,
        "value": _serialize_value(account.value) if account.value is not None else None,
        "state": _serialize_state(account.state) if account.state is not None else None,
        "overdraft": _serialize_overdraft(account.overdraft) if account.overdraft is not None else None,
    }


def _serialize_value(v: BankAccountValue) -> SerializedBankAccountValue:
    return {
        "currency_code": v.currency_code,
        "currency_label": None,
        "date": v.date,
        "rating": v.rating,
        "rating_label": transform_credit_rating(v.rating).value,
    }


def _serialize_state(s: BankAccountState) -> SerializedBankAccountState:
    return {
        "code": s.code,
        "label": transform_account_state_savings(s.code).value,
        "date": s.date,
    }


def _serialize_overdraft(o: CheckingAccountOverdraft) -> SerializedCheckingAccountOverdraft:
    return {
        "value": o.value,
        "days": o.days,
        "date": o.date,
    }
