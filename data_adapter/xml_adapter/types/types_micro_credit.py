from typing import Optional, TypedDict

from data_adapter.xml_adapter.types.types_aggregated_info import (
    SerializedDebtEvolutionAnalysis,
    SerializedDebtEvolutionQuarter,
)


class SerializedSectorCreditCount(TypedDict):
    financial: int
    cooperative: int
    real: int
    telecom: int
    total_as_principal: int
    total_as_cosigner: int


class SerializedSectorSeniority(TypedDict):
    financial: Optional[str]
    cooperative: Optional[str]
    real: Optional[str]
    telecom: Optional[str]


class SerializedGeneralProfile(TypedDict):
    active_credits: SerializedSectorCreditCount
    closed_credits: SerializedSectorCreditCount
    restructured_credits: SerializedSectorCreditCount
    refinanced_credits: SerializedSectorCreditCount
    queries_last_6m: SerializedSectorCreditCount
    disputes: SerializedSectorCreditCount
    oldest_account: SerializedSectorSeniority


class SerializedMonthlyBalancesAndArrears(TypedDict):
    date: str
    total_accounts_past_due: int
    past_due_balance: float
    total_balance: float
    max_delinquency_financial: Optional[str]
    max_delinquency_cooperative: Optional[str]
    max_delinquency_real: Optional[str]
    max_delinquency_telecom: Optional[str]
    max_delinquency_overall: Optional[str]
    accounts_past_due_30: Optional[int]
    accounts_past_due_60_plus: Optional[int]


class SerializedBalanceDelinquencyVector(TypedDict):
    has_financial: bool
    has_cooperative: bool
    has_real: bool
    has_telecom: bool
    monthly_data: list[SerializedMonthlyBalancesAndArrears]


class SerializedCurrentDebtAccount(TypedDict):
    current_state: Optional[str]
    current_state_label: Optional[str]
    rating: Optional[str]
    initial_value: Optional[float]
    current_balance: Optional[float]
    past_due_balance: Optional[float]
    monthly_installment: Optional[float]
    has_negative_behavior: Optional[bool]
    total_portfolio_debt: Optional[float]


class SerializedCurrentDebtByUser(TypedDict):
    user_type: str
    accounts: list[SerializedCurrentDebtAccount]


class SerializedCurrentDebtByType(TypedDict):
    account_type: str
    by_user: list[SerializedCurrentDebtByUser]


class SerializedCurrentDebtBySector(TypedDict):
    sector_code: str
    by_type: list[SerializedCurrentDebtByType]


class SerializedBehaviorMonthlyChar(TypedDict):
    date: str
    behavior: Optional[str]
    behavior_label: Optional[str]


class SerializedAccountBehaviorVector(TypedDict):
    entity: str
    account_number: str
    account_type: str
    state: Optional[str]
    contains_data: bool
    monthly_chars: list[SerializedBehaviorMonthlyChar]
    max_delinquency_chars: list[SerializedBehaviorMonthlyChar]


class SerializedSectorBehaviorVector(TypedDict):
    sector_name: str
    accounts: list[SerializedAccountBehaviorVector]


class SerializedTrendDataPoint(TypedDict):
    value: float
    date: str


class SerializedTrendSeries(TypedDict):
    series_name: str
    data_points: list[SerializedTrendDataPoint]


class SerializedMicroCreditAggregatedInfo(TypedDict):
    general_profile: Optional[SerializedGeneralProfile]
    balance_delinquency_vector: Optional[SerializedBalanceDelinquencyVector]
    current_debt_by_sector: list[SerializedCurrentDebtBySector]
    sector_behavior_vectors: list[SerializedSectorBehaviorVector]
    trend_series: list[SerializedTrendSeries]
    debt_evolution: list[SerializedDebtEvolutionQuarter]
    debt_evolution_analysis: Optional[SerializedDebtEvolutionAnalysis]
