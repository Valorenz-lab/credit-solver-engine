from data_adapter.xml_adapter.models.bank_account_models import (
    BankAccountState,
    BankAccountValue,
)
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
        "subscriber_code": account.subscriber_code,
        "entity_id_type": account.entity_id_type,
        "entity_id": account.entity_id,
        "value": _serialize_value(account.value) if account.value is not None else None,
        "state": _serialize_state(account.state) if account.state is not None else None,
        "overdraft": (
            _serialize_overdraft(account.overdraft)
            if account.overdraft is not None
            else None
        ),
    }


def _serialize_value(v: BankAccountValue) -> SerializedBankAccountValue:
    return {
        "currency_code": v.currency_code.value if v.currency_code else None,
        "currency_label": v.currency_code.value if v.currency_code else None,
        "date": v.date,
        "rating": v.rating.value if v.rating else None,
        "rating_label": v.rating.value if v.rating else None,
    }


def _serialize_state(s: BankAccountState) -> SerializedBankAccountState:
    return {
        "code": s.code.value if s.code else None,
        "label": s.code.value if s.code else None,
        "date": s.date,
    }


def _serialize_overdraft(
    o: CheckingAccountOverdraft,
) -> SerializedCheckingAccountOverdraft:
    return {
        "value": o.value,
        "days": o.days,
        "date": o.date,
    }
