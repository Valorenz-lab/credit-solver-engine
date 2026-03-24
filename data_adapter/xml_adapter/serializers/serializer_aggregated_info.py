from typing import Optional

from data_adapter.xml_adapter.models.aggregated_info_models import (
    AccountTypeTotals,
    AggregatedBalances,
    AggregatedInfo,
    AggregatedPrincipals,
    AggregatedSummary,
    BalanceHistoryByType,
    BalanceHistoryQuarter,
    DebtEvolutionAnalysis,
    DebtEvolutionQuarter,
    GrandTotal,
    MonthlyBalance,
    MonthlyBehavior,
    PortfolioCompositionItem,
    PortfolioStateCount,
    SectorBalance,
)
from data_adapter.xml_adapter.types import (
    SerializedAccountTypeTotals,
    SerializedAggregatedBalances,
    SerializedAggregatedPrincipals,
    SerializedAggregatedSummary,
    SerializedAggregatedSummaryInner,
    SerializedBalanceHistoryByType,
    SerializedBalanceHistoryQuarter,
    SerializedDebtEvolutionAnalysis,
    SerializedDebtEvolutionQuarter,
    SerializedGrandTotal,
    SerializedMonthlyBalance,
    SerializedMonthlyBehavior,
    SerializedPortfolioCompositionItem,
    SerializedPortfolioStateCount,
    SerializedSectorBalance,
)


def serialize_aggregated_info(info: AggregatedInfo) -> SerializedAggregatedSummary:
    return {
        "summary": _serialize_summary(info.summary),
        "account_totals": [_serialize_account_type_totals(t) for t in info.account_totals],
        "grand_totals": [_serialize_grand_total(g) for g in info.grand_totals],
        "portfolio_composition": [_serialize_composition_item(c) for c in info.portfolio_composition],
        "debt_evolution": [_serialize_debt_evolution_quarter(q) for q in info.debt_evolution],
        "debt_evolution_analysis": (
            _serialize_debt_evolution_analysis(info.debt_evolution_analysis)
            if info.debt_evolution_analysis is not None
            else None
        ),
        "balance_history_by_type": [
            _serialize_balance_history_by_type(b) for b in info.balance_history_by_type
        ],
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


def _serialize_debt_evolution_quarter(q: DebtEvolutionQuarter) -> SerializedDebtEvolutionQuarter:
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
