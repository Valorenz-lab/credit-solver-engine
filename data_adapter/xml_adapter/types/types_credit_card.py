from typing import Optional, TypedDict


class SerializedCreditCardCharacteristics(TypedDict):
    franchise: Optional[str]
    franchise_label: Optional[str]
    card_class: Optional[str]
    card_class_label: Optional[str]
    brand: Optional[str]
    is_covered: bool
    covered_code: Optional[str]
    guarantee: Optional[str]
    guarantee_label: Optional[str]


class SerializedCreditCardValues(TypedDict):
    currency_code: Optional[str]
    currency_label: Optional[str]
    date: Optional[str]
    rating: Optional[str]
    rating_label: Optional[str]
    outstanding_balance: Optional[float]
    past_due_amount: Optional[float]
    available_limit: Optional[float]
    installment_value: Optional[float]
    missed_payments: Optional[int]
    days_past_due: Optional[int]
    last_payment_date: Optional[str]
    due_date: Optional[str]
    total_credit_limit: Optional[float]


class SerializedCreditCardStates(TypedDict):
    plastic_state_code: Optional[str]
    plastic_state_label: Optional[str]
    plastic_state_date: Optional[str]
    account_state_code: Optional[str]
    account_state_date: Optional[str]
    origin_state_code: Optional[str]
    origin_state_label: Optional[str]
    origin_state_date: Optional[str]
    payment_status_code: Optional[str]
    payment_status_label: Optional[str]
    payment_status_months: Optional[str]
    payment_status_date: Optional[str]


class SerializedCreditCard(TypedDict):
    lender: str
    account_number: str
    opened_date: Optional[str]
    maturity_date: Optional[str]
    payment_history: Optional[str]
    payment_history_parsed: Optional[list[str]]
    payment_method: Optional[str]
    payment_method_label: Optional[str]
    default_probability: Optional[float]
    credit_rating: Optional[str]
    credit_rating_label: Optional[str]
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
    hd_rating: Optional[bool]
    characteristics: SerializedCreditCardCharacteristics
    values: Optional[SerializedCreditCardValues]
    states: SerializedCreditCardStates
