from typing import Optional, TypedDict


class SerializedQueryRecord(TypedDict):
    date: str
    account_type: Optional[str]
    entity: str
    office: Optional[str]
    city: Optional[str]
    reason: Optional[str]
    reason_label: Optional[str]
    count: Optional[int]
    subscriber_nit: Optional[str]
    sector: Optional[str]
    sector_label: Optional[str]


class SerializedGlobalDebtEntity(TypedDict):
    name: str
    nit: Optional[str]
    sector: Optional[str]
    sector_label: Optional[str]


class SerializedGlobalDebtGuarantee(TypedDict):
    guarantee_type: Optional[str]
    guarantee_type_label: Optional[str]
    value: Optional[float]
    date: Optional[str]


class SerializedGlobalDebt(TypedDict):
    rating: Optional[str]
    source: Optional[str]
    outstanding_balance: Optional[float]
    credit_type: Optional[str]
    credit_type_label: Optional[str]
    currency: Optional[str]
    credit_count: Optional[int]
    report_date: Optional[str]
    independent: Optional[str]
    entity: SerializedGlobalDebtEntity
    guarantee: Optional[SerializedGlobalDebtGuarantee]
