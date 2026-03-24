from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CreditCardCharacteristics:
    franchise: Optional[str]
    card_class: Optional[str]
    brand: Optional[str]
    is_covered: bool
    covered_code: Optional[str]
    guarantee: Optional[str]


@dataclass(frozen=True)
class CreditCardValues:
    currency_code: Optional[str]
    date: Optional[str]
    rating: Optional[str]
    outstanding_balance: Optional[float]
    past_due_amount: Optional[float]
    available_limit: Optional[float]
    installment_value: Optional[float]
    missed_payments: Optional[int]
    days_past_due: Optional[int]
    last_payment_date: Optional[str]
    due_date: Optional[str]
    total_credit_limit: Optional[float]


@dataclass(frozen=True)
class CreditCardStates:
    plastic_state_code: Optional[str]
    plastic_state_date: Optional[str]
    account_state_code: Optional[str]
    account_state_date: Optional[str]
    origin_state_code: Optional[str]
    origin_state_date: Optional[str]
    payment_status_code: Optional[str]
    payment_status_months: Optional[str]
    payment_status_date: Optional[str]


@dataclass(frozen=True)
class CreditCard:
    lender: str
    account_number: str
    opened_date: Optional[str]
    maturity_date: Optional[str]
    payment_history: Optional[str]
    payment_method: Optional[str]
    default_probability: Optional[float]
    credit_rating: Optional[str]
    ownership_situation: Optional[str]
    is_blocked: bool
    office: Optional[str]
    city: Optional[str]
    sector: Optional[str]
    characteristics: CreditCardCharacteristics
    values: Optional[CreditCardValues]
    states: CreditCardStates
