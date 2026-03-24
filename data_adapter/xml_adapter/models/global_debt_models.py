from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class GlobalDebtEntity:
    name: str
    nit: Optional[str]
    sector: Optional[str]


@dataclass(frozen=True)
class GlobalDebtRecord:
    rating: Optional[str]
    source: Optional[str]
    outstanding_balance: Optional[float]
    credit_type: Optional[str]
    currency: Optional[str]
    credit_count: Optional[int]
    report_date: Optional[str]
    entity: GlobalDebtEntity
