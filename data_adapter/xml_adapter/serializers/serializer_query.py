from data_adapter.xml_adapter.models.query_models import QueryRecord
from data_adapter.xml_adapter.types import SerializedQueryRecord


def serialize_query_record(record: QueryRecord) -> SerializedQueryRecord:
    return {
        "date": record.date,
        "account_type": record.account_type.value if record.account_type else None,
        "entity": record.entity,
        "office": record.office,
        "city": record.city,
        "reason": record.reason.value if record.reason else None,
        "reason_label": record.reason.value if record.reason else None,
        "count": record.count,
        "subscriber_nit": record.subscriber_nit,
        "sector": record.sector.value if record.sector else None,
        "sector_label": record.sector.value if record.sector else None,
    }
