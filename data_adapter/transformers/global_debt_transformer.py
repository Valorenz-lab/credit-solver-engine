from typing import Optional

from data_adapter.debug_tracer import record_unknown
from data_adapter.enums.financial_info.global_debt_credit_type import (
    GlobalDebtCreditType,
)


def transform_global_debt_credit_type(
    value: Optional[str],
    *,
    xml_node: str = "EndeudamientoGlobal",
    xml_attribute: str = "tipoCredito",
    record_type: str = "",
    record_context: Optional[dict[str, str]] = None,
) -> GlobalDebtCreditType:
    if not value or value.strip() == "":
        record_unknown(
            "transform_global_debt_credit_type",
            value,
            xml_node,
            xml_attribute,
            record_type,
            record_context or {},
        )
        return GlobalDebtCreditType.UNKNOWN
    mapping: dict[str, GlobalDebtCreditType] = {
        "CMR": GlobalDebtCreditType.COMMERCIAL,
        "HIP": GlobalDebtCreditType.MORTGAGE,
        "MIC": GlobalDebtCreditType.MICROCREDIT,
        "CNS": GlobalDebtCreditType.CONSUMER,
    }
    result = mapping.get(value.strip().upper())
    if result is None:
        record_unknown(
            "transform_global_debt_credit_type",
            value,
            xml_node,
            xml_attribute,
            record_type,
            record_context or {},
        )
        return GlobalDebtCreditType.UNKNOWN
    return result
