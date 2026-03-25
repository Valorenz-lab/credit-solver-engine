from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class GlobalDebtEntity:
    name: str
    nit: Optional[str]
    sector: Optional[str]


@dataclass(frozen=True)
class GlobalDebtGuarantee:
    """<Garantia> node inside <EndeudamientoGlobal>. See Table 49."""
    guarantee_type: Optional[str]   # tipo — código de garantía (Table 49)
    value: Optional[float]          # valor
    date: Optional[str]             # fecha


@dataclass(frozen=True)
class GlobalDebtRecord:
    rating: Optional[str]
    source: Optional[str]
    outstanding_balance: Optional[float]
    credit_type: Optional[str]
    currency: Optional[str]
    credit_count: Optional[int]
    report_date: Optional[str]
    independent: Optional[str]      # "N"=PN, "J"=PJ, vacío=no aplica
    entity: GlobalDebtEntity
    guarantee: Optional[GlobalDebtGuarantee]
