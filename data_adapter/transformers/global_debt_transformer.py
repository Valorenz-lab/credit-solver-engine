from typing import Optional

from data_adapter.debug_tracer import record_unknown
from data_adapter.enums.financial_info.global_debt_credit_type import (
    GlobalDebtCreditType,
)
from data_adapter.enums.financial_info.guarantee_type import GuaranteeType


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


def transform_global_debt_guarantee(
    value: Optional[str],
    *,
    xml_node: str = "Garantia",
    xml_attribute: str = "tipo",
    record_type: str = "",
    record_context: Optional[dict[str, str]] = None,
) -> GuaranteeType:
    """Transform EndeudamientoGlobal/Garantia.tipo (Tabla 49) to GuaranteeType.

    Tabla 49 uses numeric codes 0-16, distinct from Tabla 11 (alphanumeric)
    used by CuentaCartera/TarjetaCredito. Both tables are mapped to the
    shared GuaranteeType enum since the underlying guarantee concepts overlap.
    """
    if not value or value.strip() == "":
        record_unknown(
            "transform_global_debt_guarantee",
            value,
            xml_node,
            xml_attribute,
            record_type,
            record_context or {},
        )
        return GuaranteeType.UNKNOWN
    mapping: dict[str, GuaranteeType] = {
        "0":  GuaranteeType.NO_GUARANTEE,
        "1":  GuaranteeType.NOT_SUITABLE,
        "2":  GuaranteeType.REAL_ESTATE,
        "3":  GuaranteeType.OTHER_COLLATERAL,
        "4":  GuaranteeType.REVENUE_PLEDGE,
        "5":  GuaranteeType.SOVEREIGN_GUARANTEE,
        "6":  GuaranteeType.TRUST_CONTRACT,
        "7":  GuaranteeType.FNG,
        "8":  GuaranteeType.LETTER_OF_CREDIT,
        "9":  GuaranteeType.OTHER_SUITABLE,
        "10": GuaranteeType.FAG,
        "11": GuaranteeType.PERSONAL,
        "12": GuaranteeType.NON_REAL_ESTATE_LEASING,
        "13": GuaranteeType.REAL_ESTATE_LEASING,
        "14": GuaranteeType.SECURITIES_PLEDGE,
        "15": GuaranteeType.CASH_DEPOSITS,
        "16": GuaranteeType.CREDIT_INSURANCE,
    }
    result = mapping.get(value.strip())
    if result is None:
        record_unknown(
            "transform_global_debt_guarantee",
            value,
            xml_node,
            xml_attribute,
            record_type,
            record_context or {},
        )
        return GuaranteeType.UNKNOWN
    return result
