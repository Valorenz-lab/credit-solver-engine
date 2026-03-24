from data_adapter.transformers.global_debt_transformer import transform_global_debt_credit_type
from data_adapter.transformers.shared_transformers import transform_sector
from data_adapter.xml_adapter.models.global_debt_models import GlobalDebtEntity, GlobalDebtRecord
from data_adapter.xml_adapter.types import SerializedGlobalDebt, SerializedGlobalDebtEntity


def serialize_global_debt_record(record: GlobalDebtRecord) -> SerializedGlobalDebt:
    return {
        "rating": record.rating,
        "source": record.source,
        "outstanding_balance": record.outstanding_balance,
        "credit_type": record.credit_type,
        "credit_type_label": transform_global_debt_credit_type(record.credit_type).value,
        "currency": record.currency,
        "credit_count": record.credit_count,
        "report_date": record.report_date,
        "entity": _serialize_entity(record.entity),
    }


def _serialize_entity(e: GlobalDebtEntity) -> SerializedGlobalDebtEntity:
    return {
        "name": e.name,
        "nit": e.nit,
        "sector": e.sector,
        "sector_label": transform_sector(e.sector).value,
    }
