from dataclasses import dataclass
from typing import Optional

from data_adapter.enums.financial_info.credit_rating import CreditRating
from data_adapter.enums.financial_info.currency import Currency
from data_adapter.enums.financial_info.global_debt_credit_type import (
    GlobalDebtCreditType,
)
from data_adapter.enums.financial_info.guarantee_type import GuaranteeType
from data_adapter.enums.financial_info.industry_sector import IndustrySector


@dataclass(frozen=True)
class GlobalDebtEntity:
    name: str
    nit: Optional[str]
    sector: Optional[IndustrySector]


@dataclass(frozen=True)
class GlobalDebtGuarantee:
    """<Garantia> node inside <EndeudamientoGlobal>. See Table 49."""

    guarantee_type: Optional[GuaranteeType]  # tipo — código de garantía (Table 49)
    value: Optional[float]  # valor
    date: Optional[str]  # fecha


@dataclass(frozen=True)
class GlobalDebtRecord:
    rating: Optional[CreditRating]
    source: Optional[str]
    outstanding_balance: Optional[float]
    credit_type: Optional[GlobalDebtCreditType]
    currency: Optional[Currency]
    credit_count: Optional[int]
    report_date: Optional[str]
    independent: Optional[str]  # "N"=PN, "J"=PJ, vacío=no aplica
    entity: GlobalDebtEntity
    guarantee: Optional[GlobalDebtGuarantee]
