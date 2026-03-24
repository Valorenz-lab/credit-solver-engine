"""
Serializes a FullReport into SerializedFullReport (JSON-safe TypedDict).
"""

from typing import Any, Optional

from data_adapter.xml_adapter.models.bank_account_models import BankAccount
from data_adapter.xml_adapter.models.credit_card_models import CreditCard
from data_adapter.xml_adapter.models.full_report_models import FullReport
from data_adapter.xml_adapter.models.global_report_models import PortfolioAccount
from data_adapter.xml_adapter.serializers.serializer_aggregated_info import (
    _serialize_debt_evolution_quarter,
    serialize_aggregated_info,
)
from data_adapter.xml_adapter.serializers.serializer_bank_account import serialize_bank_account
from data_adapter.xml_adapter.serializers.serializer_credit_card import serialize_credit_card
from data_adapter.xml_adapter.serializers.serializer_global_debt import serialize_global_debt_record
from data_adapter.xml_adapter.serializers.serializer_global_report import _serialize_account
from data_adapter.xml_adapter.serializers.serializer_query import serialize_query_record
from data_adapter.xml_adapter.serializers.serializers_basic_report import serialize_basic_report
from data_adapter.xml_adapter.types import (
    SerializedAggregatedSummary,
    SerializedDebtEvolutionQuarter,
    SerializedFullReport,
    SerializedPortfolioAccount,
)

# Account state codes that indicate an open/active portfolio account (Tabla 4 vigente codes)
_OPEN_ACCOUNT_CODES = frozenset({
    "01", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23",
    "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35",
    "36", "37", "38", "39", "40", "41", "45", "47",
})


def serialize_full_report(report: FullReport) -> SerializedFullReport:
    basic_info = serialize_basic_report(report.basic_data)

    general_profile: Optional[SerializedAggregatedSummary] = (
        serialize_aggregated_info(report.aggregated_info)
        if report.aggregated_info is not None
        else None
    )

    # Global summary: all portfolio accounts (open CuentaCartera)
    open_portfolio = [
        acc for acc in report.portfolio_accounts
        if _is_portfolio_account_open(acc)
    ]
    global_summary: list[SerializedPortfolioAccount] = [
        _serialize_account(acc) for acc in open_portfolio
    ]

    # Bank accounts split by open/closed
    open_bank_accounts = [
        serialize_bank_account(acc)
        for acc in report.bank_accounts
        if _is_bank_account_open(acc)
    ]
    closed_bank_accounts = [
        serialize_bank_account(acc)
        for acc in report.bank_accounts
        if not _is_bank_account_open(acc)
    ]

    # Active obligations: open portfolio accounts + open credit cards
    active_portfolio = [_serialize_account(acc) for acc in report.portfolio_accounts if _is_portfolio_account_open(acc)]
    active_cards = [serialize_credit_card(c) for c in report.credit_cards if _is_credit_card_open(c)]
    active_obligations: list[dict[str, Any]] = [*active_portfolio, *active_cards]  # type: ignore[list-item]

    # Payment habits grouped by sector
    payment_habits_open = _group_by_sector_open(report)
    payment_habits_closed = _group_by_sector_closed(report)

    query_history = [serialize_query_record(q) for q in report.query_records]
    global_debt_records = [serialize_global_debt_record(g) for g in report.global_debt_records]

    debt_evolution: list[SerializedDebtEvolutionQuarter] = (
        [_serialize_debt_evolution_quarter(q) for q in report.aggregated_info.debt_evolution]
        if report.aggregated_info is not None
        else []
    )

    return {
        "basic_info": basic_info,
        "general_profile": general_profile,
        "global_summary": global_summary,
        "open_bank_accounts": open_bank_accounts,
        "closed_bank_accounts": closed_bank_accounts,
        "active_obligations": active_obligations,
        "payment_habits_open": payment_habits_open,
        "payment_habits_closed": payment_habits_closed,
        "query_history": query_history,
        "global_debt_records": global_debt_records,
        "debt_evolution": debt_evolution,
    }


def _is_portfolio_account_open(account: PortfolioAccount) -> bool:
    code = account.account_status.account_statement_code
    if code is None:
        return False
    return code in _OPEN_ACCOUNT_CODES


def _is_bank_account_open(account: BankAccount) -> bool:
    if account.state is None:
        return False
    code = account.state.code
    if code is None:
        return False
    # Savings account active codes: "01", "06", "07"
    return code in ("01", "06", "07")


def _is_credit_card_open(card: CreditCard) -> bool:
    code = card.states.account_state_code
    if code is None:
        return False
    return code in _OPEN_ACCOUNT_CODES


def _group_by_sector_open(report: FullReport) -> dict[str, Any]:
    result: dict[str, Any] = {}

    for acc in report.portfolio_accounts:
        if not _is_portfolio_account_open(acc):
            continue
        sector = acc.industry_sector or "unknown"
        if sector not in result:
            result[sector] = []
        result[sector].append(_serialize_account(acc))

    for card in report.credit_cards:
        if not _is_credit_card_open(card):
            continue
        sector = card.sector or "unknown"
        if sector not in result:
            result[sector] = []
        result[sector].append(serialize_credit_card(card))

    return result


def _group_by_sector_closed(report: FullReport) -> dict[str, Any]:
    result: dict[str, Any] = {}

    for acc in report.portfolio_accounts:
        if _is_portfolio_account_open(acc):
            continue
        sector = acc.industry_sector or "unknown"
        if sector not in result:
            result[sector] = []
        result[sector].append(_serialize_account(acc))

    for card in report.credit_cards:
        if _is_credit_card_open(card):
            continue
        sector = card.sector or "unknown"
        if sector not in result:
            result[sector] = []
        result[sector].append(serialize_credit_card(card))

    return result
