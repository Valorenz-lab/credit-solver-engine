from typing import Optional, TypedDict


class SerializedAggregatedPrincipals(TypedDict):
    active_credits: int
    closed_credits: int
    current_negative: int
    negative_last_12m: int
    open_savings_checking: int
    closed_savings_checking: int
    queries_last_6m: int
    disputes_current: int
    oldest_account_date: Optional[str]
    active_claims: int


class SerializedSectorBalance(TypedDict):
    sector: str
    balance: float
    participation: float


class SerializedMonthlyBalance(TypedDict):
    date: str
    total_past_due: float
    total_balance: float


class SerializedMonthlyBehavior(TypedDict):
    date: str
    behavior: str
    count: int


class SerializedAggregatedBalances(TypedDict):
    total_past_due: float
    past_due_30: float
    past_due_60: float
    past_due_90: float
    monthly_installment: float
    highest_credit_balance: float
    total_balance: float
    by_sector: list[SerializedSectorBalance]
    monthly_history: list[SerializedMonthlyBalance]


class SerializedAggregatedSummaryInner(TypedDict):
    principals: SerializedAggregatedPrincipals
    balances: SerializedAggregatedBalances
    behavior_history: list[SerializedMonthlyBehavior]


class SerializedAccountTypeTotals(TypedDict):
    account_type_code: str
    account_type_label: str
    debtor_quality: str
    credit_limit: float
    balance: float
    past_due: float
    installment: float


class SerializedGrandTotal(TypedDict):
    debtor_quality: str
    participation: float
    credit_limit: float
    balance: float
    past_due: float
    installment: float


class SerializedPortfolioStateCount(TypedDict):
    state_code: str
    count: int


class SerializedPortfolioCompositionItem(TypedDict):
    account_type: str
    debtor_quality: str
    percentage: float
    count: int
    states: list[SerializedPortfolioStateCount]


class SerializedDebtEvolutionQuarter(TypedDict):
    date: str
    installment: Optional[int]
    total_credit_limit: Optional[int]
    balance: Optional[int]
    usage_percentage: Optional[float]
    score: Optional[float]
    rating: Optional[str]
    new_accounts: Optional[int]
    closed_accounts: Optional[int]
    total_open: Optional[int]
    total_closed: Optional[int]
    max_delinquency: Optional[str]
    max_delinquency_months: Optional[int]


class SerializedDebtEvolutionAnalysis(TypedDict):
    installment_pct: Optional[float]
    total_credit_limit_pct: Optional[float]
    balance_pct: Optional[float]
    usage_percentage_pct: Optional[float]
    score: Optional[float]
    rating: Optional[str]
    new_accounts_pct: Optional[float]
    closed_accounts_pct: Optional[float]
    total_open_pct: Optional[float]
    total_closed_pct: Optional[float]
    max_delinquency: Optional[str]


class SerializedBalanceHistoryQuarter(TypedDict):
    date: str
    total_accounts: Optional[int]
    accounts_considered: Optional[int]
    balance: Optional[int]


class SerializedBalanceHistoryByType(TypedDict):
    account_type: str
    quarters: list[SerializedBalanceHistoryQuarter]


class SerializedQuarterlyDebtCartera(TypedDict):
    portfolio_type: str
    account_count: int
    value: float


class SerializedQuarterlyDebtSector(TypedDict):
    sector_name: str
    sector_code: Optional[str]
    admissible_guarantee: float
    other_guarantee: float
    portfolios: list[SerializedQuarterlyDebtCartera]


class SerializedQuarterlyDebtSummary(TypedDict):
    date: str
    sectors: list[SerializedQuarterlyDebtSector]


class SerializedAggregatedSummary(TypedDict):
    summary: SerializedAggregatedSummaryInner
    account_totals: list[SerializedAccountTypeTotals]
    grand_totals: list[SerializedGrandTotal]
    portfolio_composition: list[SerializedPortfolioCompositionItem]
    debt_evolution: list[SerializedDebtEvolutionQuarter]
    debt_evolution_analysis: Optional[SerializedDebtEvolutionAnalysis]
    balance_history_by_type: list[SerializedBalanceHistoryByType]
    quarterly_debt_summary: list[SerializedQuarterlyDebtSummary]
