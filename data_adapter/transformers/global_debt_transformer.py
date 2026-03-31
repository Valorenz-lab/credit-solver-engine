from typing import Optional

from data_adapter.enums.financial_info.global_debt_credit_type import (
    GlobalDebtCreditType,
)


def transform_global_debt_credit_type(value: Optional[str]) -> GlobalDebtCreditType:
    if not value or value.strip() == "":
        return GlobalDebtCreditType.UNKNOWN
    mapping = {
        "CMR": GlobalDebtCreditType.COMMERCIAL,
        "HIP": GlobalDebtCreditType.MORTGAGE,
        "MIC": GlobalDebtCreditType.MICROCREDIT,
        "CNS": GlobalDebtCreditType.CONSUMER,
    }
    return mapping.get(value.strip().upper(), GlobalDebtCreditType.UNKNOWN)
