from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AggregatedPrincipals:
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


@dataclass(frozen=True)
class SectorBalance:
    sector: str
    balance: float
    participation: float


@dataclass(frozen=True)
class MonthlyBalance:
    date: str
    total_past_due: float
    total_balance: float


@dataclass(frozen=True)
class MonthlyBehavior:
    date: str
    behavior: str
    count: int


@dataclass(frozen=True)
class AggregatedBalances:
    total_past_due: float
    past_due_30: float
    past_due_60: float
    past_due_90: float
    monthly_installment: float
    highest_credit_balance: float
    total_balance: float
    by_sector: tuple[SectorBalance, ...]
    monthly_history: tuple[MonthlyBalance, ...]


@dataclass(frozen=True)
class AggregatedSummary:
    principals: AggregatedPrincipals
    balances: AggregatedBalances
    behavior_history: tuple[MonthlyBehavior, ...]


@dataclass(frozen=True)
class AccountTypeTotals:
    account_type_code: str
    account_type_label: str
    debtor_quality: str
    credit_limit: float
    balance: float
    past_due: float
    installment: float


@dataclass(frozen=True)
class GrandTotal:
    debtor_quality: str
    participation: float
    credit_limit: float
    balance: float
    past_due: float
    installment: float


@dataclass(frozen=True)
class PortfolioStateCount:
    state_code: str
    count: int


@dataclass(frozen=True)
class PortfolioCompositionItem:
    account_type: str
    debtor_quality: str
    percentage: float
    count: int
    states: tuple[PortfolioStateCount, ...]


@dataclass(frozen=True)
class DebtEvolutionQuarter:
    date: str
    installment: Optional[int]
    total_credit_limit: Optional[int]
    balance: Optional[int]
    usage_percentage: Optional[float]
    rating: Optional[str]
    new_accounts: Optional[int]
    closed_accounts: Optional[int]
    total_open: Optional[int]
    total_closed: Optional[int]
    max_delinquency: Optional[str]
    max_delinquency_months: Optional[int]


@dataclass(frozen=True)
class AggregatedInfo:
    summary: AggregatedSummary
    account_totals: tuple[AccountTypeTotals, ...]
    grand_totals: tuple[GrandTotal, ...]
    portfolio_composition: tuple[PortfolioCompositionItem, ...]
    debt_evolution: tuple[DebtEvolutionQuarter, ...]
