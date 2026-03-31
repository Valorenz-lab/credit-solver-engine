"""
Extraction quality validator.

Parses an XML file once and runs two categories of checks:
  1. node_count       — XML node count vs extracted tuple length (zero data loss)
  2. aggregate_check  — sums/counts from extracted models vs InfoAgregada summaries

No Django dependency: can be called from a view, a script, or a test.
"""

from typing import Optional
from xml.etree import ElementTree as ET

from data_adapter.xml_adapter.exceptions import XmlParseError
from data_adapter.xml_adapter.models.full_report_models import FullReport
from data_adapter.xml_adapter.report_builders.full_report_report_builder import (
    FullReportBuilder,
)
from data_adapter.xml_adapter.xml_extractors.xml_extractor import XmlExtractor

# Tolerance for floating-point balance comparisons (currency units).
# Datacredito XMLs occasionally have minor rounding differences between
# individual account fields and the aggregated summary totals.
_BALANCE_TOLERANCE: float = 1.0


def validate_extraction(xml_path: str) -> dict[str, object]:
    """Parse the XML at xml_path and return a quality report as a plain dict.

    Raises:
        FileNotFoundError: if the file does not exist.
        XmlParseError: if the XML is malformed.
    """
    try:
        with open(xml_path, "r", encoding="utf-8") as f:
            xml_text = f.read()
    except OSError as exc:
        raise FileNotFoundError(f"Cannot read file: {xml_path}") from exc

    try:
        root = ET.fromstring(xml_text.encode("utf-8"))
    except ET.ParseError as exc:
        raise XmlParseError(f"Malformed XML: {exc}") from exc

    ex = XmlExtractor(root)
    report = FullReportBuilder().build_from_extractor(ex)

    checks: list[dict[str, object]] = []
    checks.extend(_node_count_checks(root, report))
    checks.extend(_aggregate_cross_checks(report))

    passed = sum(1 for c in checks if c["status"] == "pass")
    failed = sum(1 for c in checks if c["status"] == "fail")
    skipped = sum(1 for c in checks if c["status"] == "skip")

    return {
        "status": "ok" if failed == 0 else "warnings",
        "summary": {
            "total": len(checks),
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
        },
        "checks": checks,
    }


# ── Internal helpers ──────────────────────────────────────────────────────────


def _make_check(
    name: str,
    category: str,
    xml_value: Optional[float],
    extracted_value: Optional[float],
    note: str,
    tolerance: Optional[float] = None,
) -> dict[str, object]:
    if xml_value is None or extracted_value is None:
        return {
            "name": name,
            "category": category,
            "status": "skip",
            "xml_value": xml_value,
            "extracted_value": extracted_value,
            "delta": None,
            "note": note,
        }

    delta = round(abs(xml_value - extracted_value), 2)

    if tolerance is not None:
        status = "pass" if delta <= tolerance else "fail"
    else:
        status = "pass" if xml_value == extracted_value else "fail"

    return {
        "name": name,
        "category": category,
        "status": status,
        "xml_value": xml_value,
        "extracted_value": extracted_value,
        "delta": delta,
        "note": note,
    }


def _node_count_checks(root: ET.Element, report: FullReport) -> list[dict[str, object]]:
    """Proposal 2: XML node count vs extracted tuple length."""
    node_map: list[tuple[str, int, str]] = [
        ("CuentaCartera", len(report.portfolio_accounts), "PortfolioAccount"),
        ("TarjetaCredito", len(report.credit_cards), "CreditCard"),
        ("CuentaAhorro", len(report.bank_accounts), "BankAccount"),
        ("CuentaCorriente", len(report.checking_accounts), "CheckingAccount"),
        ("Consulta", len(report.query_records), "QueryRecord"),
        ("EndeudamientoGlobal", len(report.global_debt_records), "GlobalDebtRecord"),
        ("Score", len(report.score_records), "ScoreRecord"),
        ("Alerta", len(report.alert_records), "AlertRecord"),
    ]

    return [
        _make_check(
            name=f"node_count:{xml_tag}",
            category="node_count",
            xml_value=float(len(root.findall(f".//{xml_tag}"))),
            extracted_value=float(extracted_count),
            note=f"<{xml_tag}> nodes in XML vs extracted {model_name} records",
        )
        for xml_tag, extracted_count, model_name in node_map
    ]


def _aggregate_cross_checks(report: FullReport) -> list[dict[str, object]]:
    """Proposal 1: cross-validate extracted data against InfoAgregada summaries."""
    if report.aggregated_info is None:
        return [
            _make_check(
                name="aggregate_cross_check:skipped",
                category="aggregate_check",
                xml_value=None,
                extracted_value=None,
                note="InfoAgregada not present in this XML — all aggregate checks skipped",
            )
        ]

    principals = report.aggregated_info.summary.principals
    balances = report.aggregated_info.summary.balances
    checks: list[dict[str, object]] = []

    # ── Count checks ─────────────────────────────────────────────────────────
    open_portfolio = sum(1 for a in report.portfolio_accounts if a.is_open)
    closed_portfolio = sum(1 for a in report.portfolio_accounts if not a.is_open)
    open_bank = sum(1 for a in report.bank_accounts if a.is_open)
    closed_bank = sum(1 for a in report.bank_accounts if not a.is_open)

    checks.append(
        _make_check(
            name="aggregate_check:active_credits",
            category="aggregate_check",
            xml_value=float(principals.active_credits),
            extracted_value=float(open_portfolio),
            note=(
                "AggregatedPrincipals.active_credits vs open PortfolioAccounts. "
                "May differ if the aggregate counts CreditCards as active credits."
            ),
        )
    )
    checks.append(
        _make_check(
            name="aggregate_check:closed_credits",
            category="aggregate_check",
            xml_value=float(principals.closed_credits),
            extracted_value=float(closed_portfolio),
            note="AggregatedPrincipals.closed_credits vs closed PortfolioAccounts.",
        )
    )
    checks.append(
        _make_check(
            name="aggregate_check:open_savings_checking",
            category="aggregate_check",
            xml_value=float(principals.open_savings_checking),
            extracted_value=float(open_bank),
            note="AggregatedPrincipals.open_savings_checking vs open BankAccounts.",
        )
    )
    checks.append(
        _make_check(
            name="aggregate_check:closed_savings_checking",
            category="aggregate_check",
            xml_value=float(principals.closed_savings_checking),
            extracted_value=float(closed_bank),
            note="AggregatedPrincipals.closed_savings_checking vs closed BankAccounts.",
        )
    )

    # ── Balance checks (with tolerance) ──────────────────────────────────────
    extracted_balance = round(
        sum(
            a.values.outstanding_balance
            for a in report.portfolio_accounts
            if a.values and a.values.outstanding_balance is not None
        ),
        2,
    )
    extracted_past_due = round(
        sum(
            a.values.past_due_amount
            for a in report.portfolio_accounts
            if a.values and a.values.past_due_amount is not None
        ),
        2,
    )

    # InfoAgregada stores monetary values in miles de pesos (thousands).
    # Individual PortfolioAccount.values fields are in pesos. Multiply by 1000 to align units.
    aggregate_balance_pesos = balances.total_balance * 1000
    aggregate_past_due_pesos = balances.total_past_due * 1000

    checks.append(
        _make_check(
            name="aggregate_check:total_balance",
            category="aggregate_check",
            xml_value=aggregate_balance_pesos,
            extracted_value=extracted_balance,
            tolerance=_BALANCE_TOLERANCE,
            note=(
                f"AggregatedBalances.total_balance (×1000, miles de pesos) vs "
                f"sum of PortfolioAccount.outstanding_balance in pesos "
                f"(tolerance ±{_BALANCE_TOLERANCE}). May differ if aggregate includes CreditCards."
            ),
        )
    )
    checks.append(
        _make_check(
            name="aggregate_check:total_past_due",
            category="aggregate_check",
            xml_value=aggregate_past_due_pesos,
            extracted_value=extracted_past_due,
            tolerance=_BALANCE_TOLERANCE,
            note=(
                f"AggregatedBalances.total_past_due (×1000, miles de pesos) vs "
                f"sum of PortfolioAccount.past_due_amount in pesos "
                f"(tolerance ±{_BALANCE_TOLERANCE})."
            ),
        )
    )

    return checks
