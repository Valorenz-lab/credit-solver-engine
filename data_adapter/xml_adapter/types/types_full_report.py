from typing import Optional, TypedDict, Union

from data_adapter.xml_adapter.types.types_aggregated_info import (
    SerializedAggregatedSummary,
    SerializedDebtEvolutionQuarter,
)
from data_adapter.xml_adapter.types.types_bank_account import (
    SerializedBankAccount,
    SerializedCheckingAccount,
)
from data_adapter.xml_adapter.types.types_basic import SerializedReport
from data_adapter.xml_adapter.types.types_credit_card import SerializedCreditCard
from data_adapter.xml_adapter.types.types_global_debt import (
    SerializedGlobalDebt,
    SerializedQueryRecord,
)
from data_adapter.xml_adapter.types.types_micro_credit import (
    SerializedMicroCreditAggregatedInfo,
)
from data_adapter.xml_adapter.types.types_portfolio import SerializedPortfolioAccount
from data_adapter.xml_adapter.types.types_score_alert import (
    SerializedAlertRecord,
    SerializedScoreRecord,
)


class SerializedFullReport(TypedDict):
    basic_info: SerializedReport
    general_profile: Optional[SerializedAggregatedSummary]
    global_summary: list[SerializedPortfolioAccount]
    open_bank_accounts: list[SerializedBankAccount]
    closed_bank_accounts: list[SerializedBankAccount]
    checking_accounts: list[SerializedCheckingAccount]
    active_obligations: list[Union[SerializedPortfolioAccount, SerializedCreditCard]]
    payment_habits_open: dict[
        str, list[Union[SerializedPortfolioAccount, SerializedCreditCard]]
    ]
    payment_habits_closed: dict[
        str, list[Union[SerializedPortfolioAccount, SerializedCreditCard]]
    ]
    query_history: list[SerializedQueryRecord]
    global_debt_records: list[SerializedGlobalDebt]
    debt_evolution: list[SerializedDebtEvolutionQuarter]
    micro_credit_info: Optional[SerializedMicroCreditAggregatedInfo]
    score_records: list[SerializedScoreRecord]
    alert_records: list[SerializedAlertRecord]
