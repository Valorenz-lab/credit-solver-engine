from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class BankAccountValue:
    currency_code: Optional[str]
    date: Optional[str]
    rating: Optional[str]


@dataclass(frozen=True)
class BankAccountState:
    code: Optional[str]
    date: Optional[str]


@dataclass(frozen=True)
class BankAccount:
    lender: str
    account_number: str
    account_class: Optional[str]
    opened_date: Optional[str]
    rating: Optional[str]
    ownership_situation: Optional[str]
    is_blocked: bool
    office: Optional[str]
    city: Optional[str]
    sector: Optional[str]
    value: Optional[BankAccountValue]
    state: Optional[BankAccountState]
