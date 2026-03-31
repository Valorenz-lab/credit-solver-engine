from typing import Optional

from data_adapter.transformers.shared_transformers import transform_current_debt_status, transform_payment_behavior_char
from data_adapter.xml_adapter.models.aggregated_info_models import (
    AccountBehaviorVector,
    AccountTypeTotals,
    AggregatedBalances,
    AggregatedInfo,
    AggregatedPrincipals,
    AggregatedSummary,
    BalanceHistoryByType,
    BalanceHistoryQuarter,
    BehaviorMonthlyChar,
    CurrentDebtAccount,
    CurrentDebtBySector,
    CurrentDebtByType,
    CurrentDebtByUser,
    DebtEvolutionAnalysis,
    DebtEvolutionQuarter,
    GrandTotal,
    MicroCreditAggregatedInfo,
    MonthlyBalancesAndArrears,
    MonthlyBalance,
    MonthlyBehavior,
    GeneralProfile,
    PortfolioCompositionItem,
    PortfolioStateCount,
    QuarterlyDebtCartera,
    QuarterlyDebtSector,
    QuarterlyDebtSummary,
    SectorSeniority,
    SectorBalance,
    SectorBehaviorVector,
    SectorCreditCount,
    TrendDataPoint,
    TrendSeries,
    BalanceDelinquencyVector,
)
from data_adapter.xml_adapter.types import (
    SerializedAccountBehaviorVector,
    SerializedAccountTypeTotals,
    SerializedAggregatedBalances,
    SerializedAggregatedPrincipals,
    SerializedAggregatedSummary,
    SerializedAggregatedSummaryInner,
    SerializedBalanceHistoryByType,
    SerializedBalanceHistoryQuarter,
    SerializedBehaviorMonthlyChar,
    SerializedCurrentDebtAccount,
    SerializedCurrentDebtBySector,
    SerializedCurrentDebtByType,
    SerializedCurrentDebtByUser,
    SerializedDebtEvolutionAnalysis,
    SerializedDebtEvolutionQuarter,
    SerializedGrandTotal,
    SerializedMicroCreditAggregatedInfo,
    SerializedMonthlyBalance,
    SerializedMonthlyBehavior,
    SerializedMonthlyBalancesAndArrears,
    SerializedGeneralProfile,
    SerializedPortfolioCompositionItem,
    SerializedPortfolioStateCount,
    SerializedQuarterlyDebtCartera,
    SerializedQuarterlyDebtSector,
    SerializedQuarterlyDebtSummary,
    SerializedSectorSeniority,
    SerializedSectorBalance,
    SerializedSectorBehaviorVector,
    SerializedSectorCreditCount,
    SerializedTrendDataPoint,
    SerializedTrendSeries,
    SerializedBalanceDelinquencyVector,
)


def serialize_aggregated_info(info: AggregatedInfo) -> SerializedAggregatedSummary:
    return {
        "summary": _serialize_summary(info.summary),
        "account_totals": [_serialize_account_type_totals(t) for t in info.account_totals],
        "grand_totals": [_serialize_grand_total(g) for g in info.grand_totals],
        "portfolio_composition": [_serialize_composition_item(c) for c in info.portfolio_composition],
        "debt_evolution": [serialize_debt_evolution_quarter(q) for q in info.debt_evolution],
        "debt_evolution_analysis": (
            _serialize_debt_evolution_analysis(info.debt_evolution_analysis)
            if info.debt_evolution_analysis is not None
            else None
        ),
        "balance_history_by_type": [
            _serialize_balance_history_by_type(b) for b in info.balance_history_by_type
        ],
        "quarterly_debt_summary": [
            _serialize_quarterly_debt_summary(q) for q in info.quarterly_debt_summary
        ],
    }


def serialize_micro_credit_info(info: MicroCreditAggregatedInfo) -> SerializedMicroCreditAggregatedInfo:
    return {
        "general_profile": _serialize_general_profile(info.general_profile) if info.general_profile else None,
        "balance_delinquency_vector": _serialize_balance_delinquency_vector(info.balance_delinquency_vector) if info.balance_delinquency_vector else None,
        "current_debt_by_sector": [_serialize_current_debt_sector(s) for s in info.current_debt_by_sector],
        "sector_behavior_vectors": [_serialize_sector_behavior_vector(s) for s in info.sector_behavior_vectors],
        "trend_series": [_serialize_trend_series(t) for t in info.trend_series],
        "debt_evolution": [serialize_debt_evolution_quarter(q) for q in info.debt_evolution],
        "debt_evolution_analysis": (
            _serialize_debt_evolution_analysis(info.debt_evolution_analysis)
            if info.debt_evolution_analysis is not None
            else None
        ),
    }


def _serialize_summary(s: AggregatedSummary) -> SerializedAggregatedSummaryInner:
    return {
        "principals": _serialize_principals(s.principals),
        "balances": _serialize_balances(s.balances),
        "behavior_history": [_serialize_monthly_behavior(b) for b in s.behavior_history],
    }


def _serialize_principals(p: AggregatedPrincipals) -> SerializedAggregatedPrincipals:
    return {
        "active_credits": p.active_credits,
        "closed_credits": p.closed_credits,
        "current_negative": p.current_negative,
        "negative_last_12m": p.negative_last_12m,
        "open_savings_checking": p.open_savings_checking,
        "closed_savings_checking": p.closed_savings_checking,
        "queries_last_6m": p.queries_last_6m,
        "disputes_current": p.disputes_current,
        "oldest_account_date": p.oldest_account_date,
        "active_claims": p.active_claims,
    }


def _serialize_balances(b: AggregatedBalances) -> SerializedAggregatedBalances:
    return {
        "total_past_due": b.total_past_due,
        "past_due_30": b.past_due_30,
        "past_due_60": b.past_due_60,
        "past_due_90": b.past_due_90,
        "monthly_installment": b.monthly_installment,
        "highest_credit_balance": b.highest_credit_balance,
        "total_balance": b.total_balance,
        "by_sector": [_serialize_sector_balance(s) for s in b.by_sector],
        "monthly_history": [_serialize_monthly_balance(m) for m in b.monthly_history],
    }


def _serialize_sector_balance(s: SectorBalance) -> SerializedSectorBalance:
    return {
        "sector": s.sector,
        "balance": s.balance,
        "participation": s.participation,
    }


def _serialize_monthly_balance(m: MonthlyBalance) -> SerializedMonthlyBalance:
    return {
        "date": m.date,
        "total_past_due": m.total_past_due,
        "total_balance": m.total_balance,
    }


def _serialize_monthly_behavior(b: MonthlyBehavior) -> SerializedMonthlyBehavior:
    return {
        "date": b.date,
        "behavior": b.behavior,
        "count": b.count,
    }


def _serialize_account_type_totals(t: AccountTypeTotals) -> SerializedAccountTypeTotals:
    return {
        "account_type_code": t.account_type_code,
        "account_type_label": t.account_type_label,
        "debtor_quality": t.debtor_quality,
        "credit_limit": t.credit_limit,
        "balance": t.balance,
        "past_due": t.past_due,
        "installment": t.installment,
    }


def _serialize_grand_total(g: GrandTotal) -> SerializedGrandTotal:
    return {
        "debtor_quality": g.debtor_quality,
        "participation": g.participation,
        "credit_limit": g.credit_limit,
        "balance": g.balance,
        "past_due": g.past_due,
        "installment": g.installment,
    }


def _serialize_composition_item(c: PortfolioCompositionItem) -> SerializedPortfolioCompositionItem:
    return {
        "account_type": c.account_type,
        "debtor_quality": c.debtor_quality,
        "percentage": c.percentage,
        "count": c.count,
        "states": [_serialize_state_count(s) for s in c.states],
    }


def _serialize_state_count(s: PortfolioStateCount) -> SerializedPortfolioStateCount:
    return {
        "state_code": s.state_code,
        "count": s.count,
    }


def serialize_debt_evolution_quarter(q: DebtEvolutionQuarter) -> SerializedDebtEvolutionQuarter:
    return {
        "date": q.date,
        "installment": q.installment,
        "total_credit_limit": q.total_credit_limit,
        "balance": q.balance,
        "usage_percentage": q.usage_percentage,
        "score": q.score,
        "rating": q.rating,
        "new_accounts": q.new_accounts,
        "closed_accounts": q.closed_accounts,
        "total_open": q.total_open,
        "total_closed": q.total_closed,
        "max_delinquency": q.max_delinquency,
        "max_delinquency_months": q.max_delinquency_months,
    }


def _serialize_debt_evolution_analysis(a: DebtEvolutionAnalysis) -> SerializedDebtEvolutionAnalysis:
    return {
        "installment_pct": a.installment_pct,
        "total_credit_limit_pct": a.total_credit_limit_pct,
        "balance_pct": a.balance_pct,
        "usage_percentage_pct": a.usage_percentage_pct,
        "score": a.score,
        "rating": a.rating,
        "new_accounts_pct": a.new_accounts_pct,
        "closed_accounts_pct": a.closed_accounts_pct,
        "total_open_pct": a.total_open_pct,
        "total_closed_pct": a.total_closed_pct,
        "max_delinquency": a.max_delinquency,
    }


def _serialize_balance_history_quarter(q: BalanceHistoryQuarter) -> SerializedBalanceHistoryQuarter:
    return {
        "date": q.date,
        "total_accounts": q.total_accounts,
        "accounts_considered": q.accounts_considered,
        "balance": q.balance,
    }


def _serialize_balance_history_by_type(b: BalanceHistoryByType) -> SerializedBalanceHistoryByType:
    return {
        "account_type": b.account_type,
        "quarters": [_serialize_balance_history_quarter(q) for q in b.quarters],
    }


def _serialize_quarterly_debt_cartera(c: QuarterlyDebtCartera) -> SerializedQuarterlyDebtCartera:
    return {
        "portfolio_type": c.portfolio_type,
        "account_count": c.account_count,
        "value": c.value,
    }


def _serialize_quarterly_debt_sector(s: QuarterlyDebtSector) -> SerializedQuarterlyDebtSector:
    return {
        "sector_name": s.sector_name,
        "sector_code": s.sector_code,
        "admissible_guarantee": s.admissible_guarantee,
        "other_guarantee": s.other_guarantee,
        "portfolios": [_serialize_quarterly_debt_cartera(c) for c in s.portfolios],
    }


def _serialize_quarterly_debt_summary(q: QuarterlyDebtSummary) -> SerializedQuarterlyDebtSummary:
    return {
        "date": q.date,
        "sectors": [_serialize_quarterly_debt_sector(s) for s in q.sectors],
    }


# ── MicroCredit serializers ───────────────────────────────────────────────────

def _serialize_sector_credit_count(c: SectorCreditCount) -> SerializedSectorCreditCount:
    return {
        "financial": c.financial,
        "cooperative": c.cooperative,
        "real": c.real,
        "telecom": c.telecom,
        "total_as_principal": c.total_as_principal,
        "total_as_cosigner": c.total_as_cosigner,
    }


def _serialize_sector_seniority(a: SectorSeniority) -> SerializedSectorSeniority:
    return {
        "financial": a.financial,
        "cooperative": a.cooperative,
        "real": a.real,
        "telecom": a.telecom,
    }


def _serialize_general_profile(p: GeneralProfile) -> SerializedGeneralProfile:
    return {
        "active_credits": _serialize_sector_credit_count(p.active_credits),
        "closed_credits": _serialize_sector_credit_count(p.closed_credits),
        "restructured_credits": _serialize_sector_credit_count(p.restructured_credits),
        "refinanced_credits": _serialize_sector_credit_count(p.refinanced_credits),
        "queries_last_6m": _serialize_sector_credit_count(p.queries_last_6m),
        "disputes": _serialize_sector_credit_count(p.disputes),
        "oldest_account": _serialize_sector_seniority(p.oldest_account),
    }


def _serialize_monthly_balances_and_arrears(m: MonthlyBalancesAndArrears) -> SerializedMonthlyBalancesAndArrears:
    return {
        "date": m.date,
        "total_accounts_past_due": m.total_accounts_past_due,
        "past_due_balance": m.past_due_balance,
        "total_balance": m.total_balance,
        "max_delinquency_financial": m.max_delinquency_financial,
        "max_delinquency_cooperative": m.max_delinquency_cooperative,
        "max_delinquency_real": m.max_delinquency_real,
        "max_delinquency_telecom": m.max_delinquency_telecom,
        "max_delinquency_overall": m.max_delinquency_overall,
        "accounts_past_due_30": m.accounts_past_due_30,
        "accounts_past_due_60_plus": m.accounts_past_due_60_plus,
    }


def _serialize_balance_delinquency_vector(v: BalanceDelinquencyVector) -> SerializedBalanceDelinquencyVector:
    return {
        "has_financial": v.has_financial,
        "has_cooperative": v.has_cooperative,
        "has_real": v.has_real,
        "has_telecom": v.has_telecom,
        "monthly_data": [_serialize_monthly_balances_and_arrears(m) for m in v.monthly_data],
    }


def _serialize_current_debt_account(a: CurrentDebtAccount) -> SerializedCurrentDebtAccount:
    return {
        "current_state": a.current_state,
        "current_state_label": transform_current_debt_status(a.current_state).value,
        "rating": a.rating,
        "initial_value": a.initial_value,
        "current_balance": a.current_balance,
        "past_due_balance": a.past_due_balance,
        "monthly_installment": a.monthly_installment,
        "has_negative_behavior": a.has_negative_behavior,
        "total_portfolio_debt": a.total_portfolio_debt,
    }


def _serialize_current_debt_user(u: CurrentDebtByUser) -> SerializedCurrentDebtByUser:
    return {
        "user_type": u.user_type,
        "accounts": [_serialize_current_debt_account(a) for a in u.accounts],
    }


def _serialize_current_debt_type(t: CurrentDebtByType) -> SerializedCurrentDebtByType:
    return {
        "account_type": t.account_type,
        "by_user": [_serialize_current_debt_user(u) for u in t.by_user],
    }


def _serialize_current_debt_sector(s: CurrentDebtBySector) -> SerializedCurrentDebtBySector:
    return {
        "sector_code": s.sector_code,
        "by_type": [_serialize_current_debt_type(t) for t in s.by_type],
    }


def _serialize_behavior_monthly_char(c: BehaviorMonthlyChar) -> SerializedBehaviorMonthlyChar:
    behavior_label: Optional[str] = None
    if c.behavior is not None:
        if len(c.behavior) == 1:
            behavior_label = transform_payment_behavior_char(c.behavior).value
        else:
            # Multi-character values (e.g. "1-6") represent ranges not covered by the
            # single-character transformer; emit the raw value to avoid silent data loss.
            behavior_label = c.behavior
    return {
        "date": c.date,
        "behavior": c.behavior,
        "behavior_label": behavior_label,
    }


def _serialize_account_behavior_vector(a: AccountBehaviorVector) -> SerializedAccountBehaviorVector:
    return {
        "entity": a.entity,
        "account_number": a.account_number,
        "account_type": a.account_type,
        "state": a.state,
        "contains_data": a.contains_data,
        "monthly_chars": [_serialize_behavior_monthly_char(c) for c in a.monthly_chars],
        "max_delinquency_chars": [_serialize_behavior_monthly_char(c) for c in a.max_delinquency_chars],
    }


def _serialize_sector_behavior_vector(s: SectorBehaviorVector) -> SerializedSectorBehaviorVector:
    return {
        "sector_name": s.sector_name,
        "accounts": [_serialize_account_behavior_vector(a) for a in s.accounts],
    }


def _serialize_trend_data_point(p: TrendDataPoint) -> SerializedTrendDataPoint:
    return {
        "value": p.value,
        "date": p.date,
    }


def _serialize_trend_series(t: TrendSeries) -> SerializedTrendSeries:
    return {
        "series_name": t.series_name,
        "data_points": [_serialize_trend_data_point(p) for p in t.data_points],
    }
