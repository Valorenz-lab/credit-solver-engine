from typing import Optional

from data_adapter.xml_adapter.models.score_alert_models import AlertRecord, AlertSource, ScoreReason, ScoreRecord
from data_adapter.xml_adapter.types import (
    SerializedAlertRecord,
    SerializedAlertSource,
    SerializedScoreReason,
    SerializedScoreRecord,
)


def serialize_score_record(record: ScoreRecord) -> SerializedScoreRecord:
    return {
        "score_type": record.score_type,
        "score_value": record.score_value,
        "classification": record.classification,
        "population_pct": record.population_pct,
        "date": record.date,
        "reasons": [_serialize_score_reason(r) for r in record.reasons],
    }


def _serialize_score_reason(reason: ScoreReason) -> SerializedScoreReason:
    return {"code": reason.code}


def serialize_alert_record(record: AlertRecord) -> SerializedAlertRecord:
    return {
        "placed_date": record.placed_date,
        "expiry_date": record.expiry_date,
        "cancelled_date": record.cancelled_date,
        "code": record.code,
        "text": record.text,
        "source": _serialize_alert_source(record.source) if record.source is not None else None,
    }


def _serialize_alert_source(source: AlertSource) -> SerializedAlertSource:
    return {
        "code": source.code,
        "name": source.name,
    }
