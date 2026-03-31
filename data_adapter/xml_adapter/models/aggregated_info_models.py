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
    score: Optional[float]
    rating: Optional[str]
    new_accounts: Optional[int]
    closed_accounts: Optional[int]
    total_open: Optional[int]
    total_closed: Optional[int]
    max_delinquency: Optional[str]
    max_delinquency_months: Optional[int]


@dataclass(frozen=True)
class DebtEvolutionAnalysis:
    """Percentage variation vs previous quarters. Reflects <AnalisisPromedio>."""

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


@dataclass(frozen=True)
class BalanceHistoryQuarter:
    """Quarterly balance snapshot for a specific account type. <HistoricoSaldos/TipoCuenta/Trimestre>."""

    date: str
    total_accounts: Optional[int]
    accounts_considered: Optional[int]
    balance: Optional[int]


@dataclass(frozen=True)
class BalanceHistoryByType:
    """Balance evolution per account type. <HistoricoSaldos/TipoCuenta>."""

    account_type: str
    quarters: tuple[BalanceHistoryQuarter, ...]


@dataclass(frozen=True)
class AggregatedInfo:
    summary: AggregatedSummary
    account_totals: tuple[AccountTypeTotals, ...]
    grand_totals: tuple[GrandTotal, ...]
    portfolio_composition: tuple[PortfolioCompositionItem, ...]
    debt_evolution: tuple[DebtEvolutionQuarter, ...]
    debt_evolution_analysis: Optional[DebtEvolutionAnalysis]
    balance_history_by_type: tuple[BalanceHistoryByType, ...]
    quarterly_debt_summary: tuple["QuarterlyDebtSummary", ...]


# ── ResumenEndeudamiento ──────────────────────────────────────────────────────


@dataclass(frozen=True)
class QuarterlyDebtCartera:
    """<Cartera> node within <ResumenEndeudamiento/Trimestre/Sector>."""

    portfolio_type: str  # tipo — "Comercial", "Hipotecario", "Consumo", etc.
    account_count: int  # numeroCuentas
    value: float  # valor


@dataclass(frozen=True)
class QuarterlyDebtSector:
    """<Sector> node within <ResumenEndeudamiento/Trimestre>."""

    sector_name: str  # sector — "Financiero", "Cooperativo", etc.
    sector_code: Optional[str]  # codigoSector
    admissible_guarantee: float
    other_guarantee: float
    portfolios: tuple[QuarterlyDebtCartera, ...]


@dataclass(frozen=True)
class QuarterlyDebtSummary:
    """<Trimestre> node within <ResumenEndeudamiento>."""

    date: str
    sectors: tuple[QuarterlyDebtSector, ...]


# ── SaldosYMoras ──────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class MonthlyBalancesAndArrears:
    """<SaldosYMoras> node within <VectorSaldosYMoras>."""

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


@dataclass(frozen=True)
class BalanceDelinquencyVector:
    """<VectorSaldosYMoras> within <InfoAgregadaMicrocredito/Resumen>."""

    has_financial: bool
    has_cooperative: bool
    has_real: bool
    has_telecom: bool
    monthly_data: tuple[MonthlyBalancesAndArrears, ...]


# ── GeneralProfile ─────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class SectorCreditCount:
    """A row in GeneralProfile (CreditosVigentes, CreditosCerrados, etc.)."""

    financial: int
    cooperative: int
    real: int
    telecom: int
    total_as_principal: int
    total_as_cosigner: int


@dataclass(frozen=True)
class SectorSeniority:
    """<AntiguedadDesde> node — oldest account date per sector."""

    financial: Optional[str]
    cooperative: Optional[str]
    real: Optional[str]
    telecom: Optional[str]


@dataclass(frozen=True)
class GeneralProfile:
    """<GeneralProfile> within <InfoAgregadaMicrocredito/Resumen>."""

    active_credits: SectorCreditCount
    closed_credits: SectorCreditCount
    restructured_credits: SectorCreditCount
    refinanced_credits: SectorCreditCount
    queries_last_6m: SectorCreditCount
    disputes: SectorCreditCount
    oldest_account: SectorSeniority


# ── EndeudamientoActual ───────────────────────────────────────────────────────


@dataclass(frozen=True)
class CurrentDebtAccount:
    """<Cuenta> within <EndeudamientoActual/Sector/TipoCuenta/Usuario>."""

    current_state: Optional[str]
    rating: Optional[str]
    initial_value: Optional[float]
    current_balance: Optional[float]
    past_due_balance: Optional[float]
    monthly_installment: Optional[float]
    has_negative_behavior: Optional[bool]
    total_portfolio_debt: Optional[float]


@dataclass(frozen=True)
class CurrentDebtByUser:
    """<Usuario> within <EndeudamientoActual/Sector/TipoCuenta>."""

    user_type: str  # tipoUsuario — "Principal", "Codeudor", etc.
    accounts: tuple[CurrentDebtAccount, ...]


@dataclass(frozen=True)
class CurrentDebtByType:
    """<TipoCuenta> within <EndeudamientoActual/Sector>."""

    account_type: str
    by_user: tuple[CurrentDebtByUser, ...]


@dataclass(frozen=True)
class CurrentDebtBySector:
    """<Sector> within <EndeudamientoActual>."""

    sector_code: str
    by_type: tuple[CurrentDebtByType, ...]


# ── AnalisisVectores ──────────────────────────────────────────────────────────


@dataclass(frozen=True)
class BehaviorMonthlyChar:
    """<CaracterFecha> node — monthly behavior for a specific account."""

    date: str
    behavior: Optional[str]  # saldoDeudaTotalMora — "N", "1-6", "C", etc.


@dataclass(frozen=True)
class AccountBehaviorVector:
    """<Cuenta> within <AnalisisVectores/Sector>."""

    entity: str
    account_number: str
    account_type: str
    state: Optional[str]
    contains_data: bool
    monthly_chars: tuple[BehaviorMonthlyChar, ...]
    max_delinquency_chars: tuple[BehaviorMonthlyChar, ...]


@dataclass(frozen=True)
class SectorBehaviorVector:
    """<Sector> within <AnalisisVectores>."""

    sector_name: str
    accounts: tuple[AccountBehaviorVector, ...]


# ── ImagenTendenciaEndeudamiento ─────────────────────────────────────────────


@dataclass(frozen=True)
class TrendDataPoint:
    value: float
    date: str


@dataclass(frozen=True)
class TrendSeries:
    """<Series> within <ImagenTendenciaEndeudamiento>."""

    series_name: str
    data_points: tuple[TrendDataPoint, ...]


# ── InfoAgregadaMicrocredito ──────────────────────────────────────────────────


@dataclass(frozen=True)
class MicroCreditAggregatedInfo:
    """
    <InfoAgregadaMicrocredito> — Sección paralela a InfoAgregada específica para microcrédito.
    Contains GeneralProfile, BalanceDelinquencyVector, EndeudamientoActual, AnalisisVectores.
    """

    general_profile: Optional[GeneralProfile]
    balance_delinquency_vector: Optional[BalanceDelinquencyVector]
    current_debt_by_sector: tuple[CurrentDebtBySector, ...]
    sector_behavior_vectors: tuple[SectorBehaviorVector, ...]
    trend_series: tuple[TrendSeries, ...]
    debt_evolution: tuple[DebtEvolutionQuarter, ...]
    debt_evolution_analysis: Optional[DebtEvolutionAnalysis]
