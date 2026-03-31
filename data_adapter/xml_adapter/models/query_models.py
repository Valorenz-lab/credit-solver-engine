from dataclasses import dataclass
from typing import Optional

from data_adapter.enums.financial_info.account_type import AccountType
from data_adapter.enums.financial_info.industry_sector import IndustrySector
from data_adapter.enums.financial_info.query_reason import QueryReason


@dataclass(frozen=True)
class QueryRecord:
    date: str
    account_type: Optional[AccountType]
    entity: str
    office: Optional[str]
    city: Optional[str]
    reason: Optional[QueryReason]
    count: Optional[int]
    subscriber_nit: Optional[str]
    sector: Optional[IndustrySector]
