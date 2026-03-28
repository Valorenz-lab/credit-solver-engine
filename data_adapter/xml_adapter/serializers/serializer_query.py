from data_adapter.transformers.shared_transformers import transform_query_reason, transform_industry_sector
from data_adapter.xml_adapter.models.query_models import QueryRecord
from data_adapter.xml_adapter.types import SerializedQueryRecord


def serialize_query_record(record: QueryRecord) -> SerializedQueryRecord:
    return {
        "date": record.date,
        "account_type": record.account_type,
        "entity": record.entity,
        "office": record.office,
        "city": record.city,
        "reason": record.reason,
        "reason_label": transform_query_reason(record.reason).value,
        "count": record.count,
        "subscriber_nit": record.subscriber_nit,
        "sector": record.sector,
        "sector_label": transform_industry_sector(record.sector).value,
    }
