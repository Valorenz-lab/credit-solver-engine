from typing import Optional, TypedDict


class SerializedScoreReason(TypedDict):
    code: str


class SerializedScoreRecord(TypedDict):
    score_type: str
    score_value: float
    classification: Optional[str]
    population_pct: Optional[int]
    date: str
    reasons: list[SerializedScoreReason]


class SerializedAlertSource(TypedDict):
    code: str
    name: Optional[str]


class SerializedAlertRecord(TypedDict):
    placed_date: str
    expiry_date: str
    cancelled_date: Optional[str]
    code: str
    text: Optional[str]
    source: Optional[SerializedAlertSource]
