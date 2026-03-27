"""Builder for InfoAgregada node → AggregatedInfo.

Also exports parse_debt_evolution_quarters and parse_debt_evolution_analysis
as public module-level functions so MicroCreditBuilder can reuse them without
duplicating the logic (both InfoAgregada and InfoAgregadaMicrocredito share
the same <EvolucionDeuda> structure).
"""

from typing import Optional
from xml.etree import ElementTree as ET

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
    QuarterlyDebtCartera,
    QuarterlyDebtSector,
    QuarterlyDebtSummary,
    SectorBalance,
)
from data_adapter.xml_adapter.xml_extractors.xml_extractor import XmlExtractor


# ── Shared functions (also used by MicroCreditBuilder) ────────────────────────

def parse_debt_evolution_quarters(
    ex: XmlExtractor,
    evolution_node: Optional[ET.Element],
) -> tuple[DebtEvolutionQuarter, ...]:
    """Parse all <Trimestre> nodes inside an <EvolucionDeuda> node."""
    if evolution_node is None:
        return ()
    return tuple(_parse_quarter(ex, n) for n in evolution_node.findall("Trimestre"))


def parse_debt_evolution_analysis(
    ex: XmlExtractor,
    evolution_node: Optional[ET.Element],
) -> Optional[DebtEvolutionAnalysis]:
    """Parse <AnalisisPromedio> inside an <EvolucionDeuda> node."""
    if evolution_node is None:
        return None
    node = ex.find_node("AnalisisPromedio", parent=evolution_node)
    if node is None:
        return None
    return DebtEvolutionAnalysis(
        installment_pct=ex.get_float(node, "cuota"),
        total_credit_limit_pct=ex.get_float(node, "cupoTotal"),
        balance_pct=ex.get_float(node, "saldo"),
        usage_percentage_pct=ex.get_float(node, "porcentajeUso"),
        score=ex.get_float(node, "score"),
        rating=ex.get_attr(node, "calificacion"),
        new_accounts_pct=ex.get_float(node, "aperturaCuentas"),
        closed_accounts_pct=ex.get_float(node, "cierreCuentas"),
        total_open_pct=ex.get_float(node, "totalAbiertas"),
        total_closed_pct=ex.get_float(node, "totalCerradas"),
        max_delinquency=ex.get_attr(node, "moraMaxima"),
    )


def _parse_quarter(ex: XmlExtractor, node: ET.Element) -> DebtEvolutionQuarter:
    return DebtEvolutionQuarter(
        date=ex.get_attr_required(node, "fecha"),
        installment=ex.get_int(node, "cuota"),
        total_credit_limit=ex.get_int(node, "cupoTotal"),
        balance=ex.get_int(node, "saldo"),
        usage_percentage=ex.get_float(node, "porcentajeUso"),
        score=ex.get_float(node, "score"),
        rating=ex.get_attr(node, "calificacion"),
        new_accounts=ex.get_int(node, "aperturaCuentas"),
        closed_accounts=ex.get_int(node, "cierreCuentas"),
        total_open=ex.get_int(node, "totalAbiertas"),
        total_closed=ex.get_int(node, "totalCerradas"),
        max_delinquency=ex.get_attr(node, "moraMaxima"),
        max_delinquency_months=ex.get_int(node, "mesesMoraMaxima"),
    )


# ── AggregatedInfoBuilder ─────────────────────────────────────────────────────

class AggregatedInfoBuilder:
    """Parses <InfoAgregada> within an <Informe> node."""

    def __init__(self, ex: XmlExtractor, report_node: ET.Element) -> None:
        self._ex = ex
        self._report_node = report_node

    def build(self) -> Optional[AggregatedInfo]:
        info_node = self._ex.find_node("InfoAgregada", parent=self._report_node)
        if info_node is None:
            return None

        resumen_node = self._ex.find_node("Resumen", parent=info_node)
        totales_node = self._ex.find_node("Totales", parent=info_node)
        composition_node = self._ex.find_node("ComposicionPortafolio", parent=info_node)
        evolution_node = self._ex.find_node("EvolucionDeuda", parent=info_node)
        quarterly_debt_node = self._ex.find_node("ResumenEndeudamiento", parent=info_node)

        return AggregatedInfo(
            summary=self._parse_summary(resumen_node),
            account_totals=self._parse_account_type_totals(totales_node),
            grand_totals=self._parse_grand_totals(totales_node),
            portfolio_composition=self._parse_portfolio_composition(composition_node),
            debt_evolution=parse_debt_evolution_quarters(self._ex, evolution_node),
            debt_evolution_analysis=parse_debt_evolution_analysis(self._ex, evolution_node),
            balance_history_by_type=self._parse_balance_history_by_type(info_node),
            quarterly_debt_summary=self._parse_quarterly_debt_summary(quarterly_debt_node),
        )

    # ── Resumen ───────────────────────────────────────────────────────────────

    def _parse_summary(self, resumen_node: Optional[ET.Element]) -> AggregatedSummary:
        return AggregatedSummary(
            principals=self._parse_principals(resumen_node),
            balances=self._parse_balances(resumen_node),
            behavior_history=self._parse_behavior_history(resumen_node),
        )

    def _parse_principals(self, resumen_node: Optional[ET.Element]) -> AggregatedPrincipals:
        node: Optional[ET.Element] = None
        if resumen_node is not None:
            node = self._ex.find_node("Principales", parent=resumen_node)
        return AggregatedPrincipals(
            active_credits=self._ex.get_int(node, "creditoVigentes") or 0,
            closed_credits=self._ex.get_int(node, "creditosCerrados") or 0,
            current_negative=self._ex.get_int(node, "creditosActualesNegativos") or 0,
            negative_last_12m=self._ex.get_int(node, "histNegUlt12Meses") or 0,
            open_savings_checking=self._ex.get_int(node, "cuentasAbiertasAHOCCB") or 0,
            closed_savings_checking=self._ex.get_int(node, "cuentasCerradasAHOCCB") or 0,
            queries_last_6m=self._ex.get_int(node, "consultadasUlt6meses") or 0,
            disputes_current=self._ex.get_int(node, "desacuerdosALaFecha") or 0,
            oldest_account_date=self._ex.get_attr(node, "antiguedadDesde"),
            active_claims=self._ex.get_int(node, "reclamosVigentes") or 0,
        )

    def _parse_balances(self, resumen_node: Optional[ET.Element]) -> AggregatedBalances:
        saldos_node: Optional[ET.Element] = None
        if resumen_node is not None:
            saldos_node = self._ex.find_node("Saldos", parent=resumen_node)

        sector_nodes: list[ET.Element] = []
        month_nodes: list[ET.Element] = []
        if saldos_node is not None:
            sector_nodes = saldos_node.findall("Sector")
            month_nodes = saldos_node.findall("Mes")

        by_sector = tuple(
            SectorBalance(
                sector=self._ex.get_attr(s, "sector") or "",
                balance=self._ex.get_float(s, "saldo") or 0.0,
                participation=self._ex.get_float(s, "participacion") or 0.0,
            )
            for s in sector_nodes
        )
        monthly_history = tuple(
            MonthlyBalance(
                date=self._ex.get_attr(m, "fecha") or "",
                total_past_due=self._ex.get_float(m, "saldoTotalMora") or 0.0,
                total_balance=self._ex.get_float(m, "saldoTotal") or 0.0,
            )
            for m in month_nodes
        )
        return AggregatedBalances(
            total_past_due=self._ex.get_float(saldos_node, "saldoTotalEnMora") or 0.0,
            past_due_30=self._ex.get_float(saldos_node, "saldoM30") or 0.0,
            past_due_60=self._ex.get_float(saldos_node, "saldoM60") or 0.0,
            past_due_90=self._ex.get_float(saldos_node, "saldoM90") or 0.0,
            monthly_installment=self._ex.get_float(saldos_node, "cuotaMensual") or 0.0,
            highest_credit_balance=self._ex.get_float(saldos_node, "saldoCreditoMasAlto") or 0.0,
            total_balance=self._ex.get_float(saldos_node, "saldoTotal") or 0.0,
            by_sector=by_sector,
            monthly_history=monthly_history,
        )

    def _parse_behavior_history(
        self, resumen_node: Optional[ET.Element]
    ) -> tuple[MonthlyBehavior, ...]:
        if resumen_node is None:
            return ()
        comportamiento_node = self._ex.find_node("Comportamiento", parent=resumen_node)
        if comportamiento_node is None:
            return ()
        return tuple(
            MonthlyBehavior(
                date=self._ex.get_attr(m, "fecha") or "",
                behavior=self._ex.get_attr(m, "comportamiento") or "",
                count=self._ex.get_int(m, "cantidad") or 0,
            )
            for m in comportamiento_node.findall("Mes")
        )

    # ── Totales ───────────────────────────────────────────────────────────────

    def _parse_account_type_totals(
        self, totales_node: Optional[ET.Element]
    ) -> tuple[AccountTypeTotals, ...]:
        if totales_node is None:
            return ()
        return tuple(
            AccountTypeTotals(
                account_type_code=self._ex.get_attr(n, "codigoTipo") or "",
                account_type_label=self._ex.get_attr(n, "tipo") or "",
                debtor_quality=self._ex.get_attr(n, "calidadDeudor") or "",
                credit_limit=self._ex.get_float(n, "cupo") or 0.0,
                balance=self._ex.get_float(n, "saldo") or 0.0,
                past_due=self._ex.get_float(n, "saldoMora") or 0.0,
                installment=self._ex.get_float(n, "cuota") or 0.0,
            )
            for n in totales_node.findall("TipoCuenta")
        )

    def _parse_grand_totals(
        self, totales_node: Optional[ET.Element]
    ) -> tuple[GrandTotal, ...]:
        if totales_node is None:
            return ()
        return tuple(
            GrandTotal(
                debtor_quality=self._ex.get_attr(n, "calidadDeudor") or "",
                participation=self._ex.get_float(n, "participacion") or 0.0,
                credit_limit=self._ex.get_float(n, "cupo") or 0.0,
                balance=self._ex.get_float(n, "saldo") or 0.0,
                past_due=self._ex.get_float(n, "saldoMora") or 0.0,
                installment=self._ex.get_float(n, "cuota") or 0.0,
            )
            for n in totales_node.findall("Total")
        )

    # ── ComposicionPortafolio ─────────────────────────────────────────────────

    def _parse_portfolio_composition(
        self, composition_node: Optional[ET.Element]
    ) -> tuple[PortfolioCompositionItem, ...]:
        if composition_node is None:
            return ()
        return tuple(
            self._parse_composition_item(n)
            for n in composition_node.findall("TipoCuenta")
        )

    def _parse_composition_item(self, node: ET.Element) -> PortfolioCompositionItem:
        states = tuple(
            PortfolioStateCount(
                state_code=self._ex.get_attr(s, "codigo") or "",
                count=self._ex.get_int(s, "cantidad") or 0,
            )
            for s in node.findall("Estado")
        )
        return PortfolioCompositionItem(
            account_type=self._ex.get_attr(node, "tipo") or "",
            debtor_quality=self._ex.get_attr(node, "calidadDeudor") or "",
            percentage=self._ex.get_float(node, "porcentaje") or 0.0,
            count=self._ex.get_int(node, "cantidad") or 0,
            states=states,
        )

    # ── HistoricoSaldos ───────────────────────────────────────────────────────

    def _parse_balance_history_by_type(
        self, info_node: ET.Element
    ) -> tuple[BalanceHistoryByType, ...]:
        historico_node = self._ex.find_node("HistoricoSaldos", parent=info_node)
        if historico_node is None:
            return ()
        return tuple(
            self._parse_balance_history_type(n)
            for n in historico_node.findall("TipoCuenta")
        )

    def _parse_balance_history_type(self, node: ET.Element) -> BalanceHistoryByType:
        quarters = tuple(
            BalanceHistoryQuarter(
                date=self._ex.get_attr_required(q, "fecha"),
                total_accounts=self._ex.get_int(q, "totalCuentas"),
                accounts_considered=self._ex.get_int(q, "cuentasConsideradas"),
                balance=self._ex.get_int(q, "saldo"),
            )
            for q in node.findall("Trimestre")
        )
        return BalanceHistoryByType(
            account_type=self._ex.get_attr(node, "tipo") or "",
            quarters=quarters,
        )

    # ── ResumenEndeudamiento ──────────────────────────────────────────────────

    def _parse_quarterly_debt_summary(
        self, node: Optional[ET.Element]
    ) -> tuple[QuarterlyDebtSummary, ...]:
        if node is None:
            return ()
        return tuple(
            self._parse_quarterly_debt_quarter(t) for t in node.findall("Trimestre")
        )

    def _parse_quarterly_debt_quarter(self, node: ET.Element) -> QuarterlyDebtSummary:
        sectors = tuple(
            self._parse_quarterly_debt_sector(s) for s in node.findall("Sector")
        )
        return QuarterlyDebtSummary(
            date=self._ex.get_attr_required(node, "fecha"),
            sectors=sectors,
        )

    def _parse_quarterly_debt_sector(self, node: ET.Element) -> QuarterlyDebtSector:
        portfolios = tuple(
            QuarterlyDebtCartera(
                portfolio_type=self._ex.get_attr(c, "tipo") or "",
                account_count=self._ex.get_int(c, "numeroCuentas") or 0,
                value=self._ex.get_float(c, "valor") or 0.0,
            )
            for c in node.findall("Cartera")
        )
        return QuarterlyDebtSector(
            sector_name=self._ex.get_attr(node, "sector") or "",
            sector_code=self._ex.get_attr(node, "codigoSector"),
            admissible_guarantee=self._ex.get_float(node, "garantiaAdmisible") or 0.0,
            other_guarantee=self._ex.get_float(node, "garantiaOtro") or 0.0,
            portfolios=portfolios,
        )
