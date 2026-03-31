from dataclasses import dataclass
from typing import Optional

from data_adapter.enums.financial_info.credit_rating import CreditRating
from data_adapter.enums.financial_info.currency import Currency
from data_adapter.enums.financial_info.industry_sector import IndustrySector
from data_adapter.enums.financial_info.ownership_situation import OwnershipSituation
from data_adapter.enums.financial_info.savings_account_status import (
    SavingsAccountStatus,
)

_OPEN_BANK_ACCOUNT_STATUSES: frozenset[SavingsAccountStatus] = frozenset(
    {
        SavingsAccountStatus.ACTIVE,  # "01"
        SavingsAccountStatus.SEIZED,  # "06"
        SavingsAccountStatus.SEIZED_ACTIVE,  # "07"
    }
)


@dataclass(frozen=True)
class BankAccountValue:
    currency_code: Optional[Currency]
    date: Optional[str]
    rating: Optional[CreditRating]


@dataclass(frozen=True)
class BankAccountState:
    code: Optional[SavingsAccountStatus]
    date: Optional[str]


@dataclass(frozen=True)
class BankAccount:
    lender: str
    account_number: str
    account_class: Optional[str]
    opened_date: Optional[str]
    rating: Optional[CreditRating]
    ownership_situation: Optional[OwnershipSituation]
    is_blocked: bool
    office: Optional[str]
    city: Optional[str]
    dane_city_code: Optional[str]  # codigoDaneCiudad
    sector: Optional[IndustrySector]
    entity_id_type: Optional[str]  # tipoIdentificacion of the lending entity
    entity_id: Optional[str]  # identificacion (NIT) of the lending entity
    value: Optional[BankAccountValue]
    state: Optional[BankAccountState]

    @property
    def is_open(self) -> bool:
        """Return True if the account state code indicates an active savings account."""
        if self.state is None or self.state.code is None:
            return False
        return self.state.code in _OPEN_BANK_ACCOUNT_STATUSES
