from dataclasses import dataclass
from typing import Optional

# Savings account state codes that represent an open/active account.
# Source: Datacredito — CuentaAhorro active codes (distinct from portfolio codes).
_OPEN_BANK_ACCOUNT_CODES: frozenset[str] = frozenset({"01", "06", "07"})


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
    dane_city_code: Optional[str]        # codigoDaneCiudad
    sector: Optional[str]
    entity_id_type: Optional[str]        # tipoIdentificacion of the lending entity
    entity_id: Optional[str]             # identificacion (NIT) of the lending entity
    value: Optional[BankAccountValue]
    state: Optional[BankAccountState]

    @property
    def is_open(self) -> bool:
        """Return True if the account state code indicates an active savings account."""
        if self.state is None or self.state.code is None:
            return False
        return self.state.code in _OPEN_BANK_ACCOUNT_CODES
