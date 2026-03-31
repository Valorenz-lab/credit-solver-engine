from dataclasses import dataclass
from typing import Optional

from data_adapter.enums.financial_info.industry_sector import IndustrySector
from data_adapter.enums.financial_info.ownership_situation import OwnershipSituation
from data_adapter.xml_adapter.models.bank_account_models import (
    BankAccountState,
    BankAccountValue,
)


@dataclass(frozen=True)
class CheckingAccountOverdraft:
    """<Sobregiro> node — overdraft status."""

    value: Optional[float]  # valor
    days: Optional[int]  # dias
    date: Optional[str]  # fecha


@dataclass(frozen=True)
class CheckingAccount:
    """Represents a checking account <CuentaCorriente>."""

    lender: str
    account_number: str
    account_class: Optional[str]
    opened_date: Optional[str]
    ownership_situation: Optional[OwnershipSituation]
    is_blocked: bool
    office: Optional[str]
    city: Optional[str]
    dane_city_code: Optional[str]
    sector: Optional[IndustrySector]
    subscriber_code: Optional[str]  # codSuscriptor
    entity_id_type: Optional[str]  # tipoIdentificacion of the lending entity
    entity_id: Optional[str]  # identificacion (NIT) of the lending entity
    value: Optional[BankAccountValue]
    state: Optional[BankAccountState]
    overdraft: Optional[CheckingAccountOverdraft]
