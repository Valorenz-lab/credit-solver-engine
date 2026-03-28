from typing import Optional, TypedDict


class SerializedBankAccountValue(TypedDict):
    currency_code: Optional[str]
    currency_label: Optional[str]
    date: Optional[str]
    rating: Optional[str]
    rating_label: Optional[str]


class SerializedBankAccountState(TypedDict):
    code: Optional[str]
    label: Optional[str]
    date: Optional[str]


class SerializedBankAccount(TypedDict):
    lender: str
    account_number: str
    account_class: Optional[str]
    opened_date: Optional[str]
    rating: Optional[str]
    rating_label: Optional[str]
    ownership_situation: Optional[str]
    ownership_situation_label: Optional[str]
    is_blocked: bool
    office: Optional[str]
    city: Optional[str]
    dane_city_code: Optional[str]
    sector: Optional[str]
    sector_label: Optional[str]
    entity_id_type: Optional[str]
    entity_id: Optional[str]
    value: Optional[SerializedBankAccountValue]
    state: Optional[SerializedBankAccountState]


class SerializedCheckingAccountOverdraft(TypedDict):
    value: Optional[float]
    days: Optional[int]
    date: Optional[str]


class SerializedCheckingAccount(TypedDict):
    lender: str
    account_number: str
    account_class: Optional[str]
    opened_date: Optional[str]
    ownership_situation: Optional[str]
    ownership_situation_label: Optional[str]
    is_blocked: bool
    office: Optional[str]
    city: Optional[str]
    dane_city_code: Optional[str]
    sector: Optional[str]
    sector_label: Optional[str]
    subscriber_code: Optional[str]
    entity_id_type: Optional[str]
    entity_id: Optional[str]
    value: Optional[SerializedBankAccountValue]
    state: Optional[SerializedBankAccountState]
    overdraft: Optional[SerializedCheckingAccountOverdraft]
