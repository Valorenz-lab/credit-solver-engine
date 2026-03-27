"""
Serializes a FullReport into SerializedFullReport (JSON-safe TypedDict).
"""

from typing import Optional, Union

from data_adapter.xml_adapter.models.full_report_models import FullReport
from data_adapter.xml_adapter.serializers.serializer_aggregated_info import (
    serialize_debt_evolution_quarter,
    serialize_aggregated_info,
    serialize_micro_credit_info,
)
from data_adapter.xml_adapter.serializers.serializer_bank_account import serialize_bank_account
from data_adapter.xml_adapter.serializers.serializer_checking_account import serialize_checking_account
from data_adapter.xml_adapter.serializers.serializer_credit_card import serialize_credit_card
from data_adapter.xml_adapter.serializers.serializer_global_debt import serialize_global_debt_record
from data_adapter.xml_adapter.serializers.serializer_global_report import _serialize_account
from data_adapter.xml_adapter.serializers.serializer_query import serialize_query_record
from data_adapter.xml_adapter.serializers.serializer_score_alert import serialize_alert_record, serialize_score_record
from data_adapter.xml_adapter.serializers.serializers_basic_report import serialize_basic_report
from data_adapter.xml_adapter.types import (
    SerializedAggregatedSummary,
    SerializedCreditCard,
    SerializedDebtEvolutionQuarter,
    SerializedFullReport,
    SerializedMicroCreditAggregatedInfo,
    SerializedPortfolioAccount,
)


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
        if acc.is_open
    ]
    global_summary: list[SerializedPortfolioAccount] = [
        _serialize_account(acc) for acc in open_portfolio
    ]

    # Bank accounts split by open/closed
    open_bank_accounts = [
        serialize_bank_account(acc)
        for acc in report.bank_accounts
        if acc.is_open
    ]
    closed_bank_accounts = [
        serialize_bank_account(acc)
        for acc in report.bank_accounts
        if not acc.is_open
    ]

    checking_accounts = [serialize_checking_account(acc) for acc in report.checking_accounts]

    # Active obligations: open portfolio accounts + open credit cards
    active_portfolio = [_serialize_account(acc) for acc in report.portfolio_accounts if acc.is_open]
    active_cards = [serialize_credit_card(c) for c in report.credit_cards if c.is_open]
    active_obligations: list[Union[SerializedPortfolioAccount, SerializedCreditCard]] = [*active_portfolio, *active_cards]

    # Payment habits grouped by sector
    payment_habits_open = _group_by_sector_open(report)
    payment_habits_closed = _group_by_sector_closed(report)

    query_history = [serialize_query_record(q) for q in report.query_records]
    global_debt_records = [serialize_global_debt_record(g) for g in report.global_debt_records]

    debt_evolution: list[SerializedDebtEvolutionQuarter] = (
        [serialize_debt_evolution_quarter(q) for q in report.aggregated_info.debt_evolution]
        if report.aggregated_info is not None
        else []
    )

    micro_credit: Optional[SerializedMicroCreditAggregatedInfo] = (
        serialize_micro_credit_info(report.micro_credit_info)
        if report.micro_credit_info is not None
        else None
    )

    score_records = [serialize_score_record(s) for s in report.score_records]
    alert_records = [serialize_alert_record(a) for a in report.alert_records]

    return {
        "basic_info": basic_info,
        "general_profile": general_profile,
        "global_summary": global_summary,
        "open_bank_accounts": open_bank_accounts,
        "closed_bank_accounts": closed_bank_accounts,
        "checking_accounts": checking_accounts,
        "active_obligations": active_obligations,
        "payment_habits_open": payment_habits_open,
        "payment_habits_closed": payment_habits_closed,
        "query_history": query_history,
        "global_debt_records": global_debt_records,
        "debt_evolution": debt_evolution,
        "micro_credit_info": micro_credit,
        "score_records": score_records,
        "alert_records": alert_records,
    }


def _group_by_sector_open(
    report: FullReport,
) -> dict[str, list[Union[SerializedPortfolioAccount, SerializedCreditCard]]]:
    result: dict[str, list[Union[SerializedPortfolioAccount, SerializedCreditCard]]] = {}

    for acc in report.portfolio_accounts:
        if not acc.is_open:
            continue
        sector = acc.industry_sector or "unknown"
        if sector not in result:
            result[sector] = []
        result[sector].append(_serialize_account(acc))

    for card in report.credit_cards:
        if not card.is_open:
            continue
        sector = card.sector or "unknown"
        if sector not in result:
            result[sector] = []
        result[sector].append(serialize_credit_card(card))

    return result


def _group_by_sector_closed(
    report: FullReport,
) -> dict[str, list[Union[SerializedPortfolioAccount, SerializedCreditCard]]]:
    result: dict[str, list[Union[SerializedPortfolioAccount, SerializedCreditCard]]] = {}

    for acc in report.portfolio_accounts:
        if acc.is_open:
            continue
        sector = acc.industry_sector or "unknown"
        if sector not in result:
            result[sector] = []
        result[sector].append(_serialize_account(acc))

    for card in report.credit_cards:
        if card.is_open:
            continue
        sector = card.sector or "unknown"
        if sector not in result:
            result[sector] = []
        result[sector].append(serialize_credit_card(card))

    return result
