from data_adapter.xml_adapter.models.bank_account_models import (
    BankAccount,
    BankAccountState,
    BankAccountValue,
)
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
        "rating": account.rating.value if account.rating else None,
        "rating_label": account.rating.value if account.rating else None,
        "ownership_situation": (
            account.ownership_situation.value if account.ownership_situation else None
        ),
        "ownership_situation_label": (
            account.ownership_situation.value if account.ownership_situation else None
        ),
        "is_blocked": account.is_blocked,
        "office": account.office,
        "city": account.city,
        "dane_city_code": account.dane_city_code,
        "sector": account.sector.value if account.sector else None,
        "sector_label": account.sector.value if account.sector else None,
        "entity_id_type": account.entity_id_type,
        "entity_id": account.entity_id,
        "value": (
            _serialize_bank_account_value(account.value)
            if account.value is not None
            else None
        ),
        "state": (
            _serialize_bank_account_state(account.state)
            if account.state is not None
            else None
        ),
    }


def _serialize_bank_account_value(v: BankAccountValue) -> SerializedBankAccountValue:
    return {
        "currency_code": v.currency_code.value if v.currency_code else None,
        "currency_label": v.currency_code.value if v.currency_code else None,
        "date": v.date,
        "rating": v.rating.value if v.rating else None,
        "rating_label": v.rating.value if v.rating else None,
    }


def _serialize_bank_account_state(s: BankAccountState) -> SerializedBankAccountState:
    return {
        "code": s.code.value if s.code else None,
        "label": s.code.value if s.code else None,
        "date": s.date,
    }
