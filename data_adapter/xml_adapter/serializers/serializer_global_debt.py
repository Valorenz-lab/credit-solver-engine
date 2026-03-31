from typing import Optional

from data_adapter.xml_adapter.models.global_debt_models import (
    GlobalDebtEntity,
    GlobalDebtGuarantee,
    GlobalDebtRecord,
)
from data_adapter.xml_adapter.types import (
    SerializedGlobalDebt,
    SerializedGlobalDebtEntity,
    SerializedGlobalDebtGuarantee,
)


def serialize_global_debt_record(record: GlobalDebtRecord) -> SerializedGlobalDebt:
    return {
        "rating": record.rating.value if record.rating else None,
        "source": record.source,
        "outstanding_balance": record.outstanding_balance,
        "credit_type": record.credit_type.value if record.credit_type else None,
        "credit_type_label": record.credit_type.value if record.credit_type else None,
        "currency": record.currency.value if record.currency else None,
        "credit_count": record.credit_count,
        "report_date": record.report_date,
        "independent": record.independent,
        "entity": _serialize_entity(record.entity),
        "guarantee": _serialize_guarantee(record.guarantee),
    }


def _serialize_entity(e: GlobalDebtEntity) -> SerializedGlobalDebtEntity:
    return {
        "name": e.name,
        "nit": e.nit,
        "sector": e.sector.value if e.sector else None,
        "sector_label": e.sector.value if e.sector else None,
    }


def _serialize_guarantee(
    g: Optional[GlobalDebtGuarantee],
) -> Optional[SerializedGlobalDebtGuarantee]:
    if g is None:
        return None
    return {
        "guarantee_type": g.guarantee_type.value if g.guarantee_type else None,
        "guarantee_type_label": g.guarantee_type.value if g.guarantee_type else None,
        "value": g.value,
        "date": g.date,
    }
