from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class QueryRecord:
    date: str
    account_type: Optional[str]
    entity: str
    office: Optional[str]
    city: Optional[str]
    reason: Optional[str]
    count: Optional[int]
    subscriber_nit: Optional[str]
    sector: Optional[str]
