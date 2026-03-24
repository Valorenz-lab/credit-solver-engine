"""
Full report builder for Datacredito XML.
Orchestrates all sub-builders and parses remaining nodes inline.
"""

import os
from typing import Optional
from xml.etree import ElementTree as ET

from data_adapter.xml_adapter.exceptions import XmlParseError
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
from data_adapter.xml_adapter.models.basic_data_models import BasicReport
from data_adapter.xml_adapter.models.full_report_models import FullReport
from data_adapter.xml_adapter.models.global_debt_models import GlobalDebtEntity, GlobalDebtRecord
from data_adapter.xml_adapter.models.checking_account_models import CheckingAccount
from data_adapter.xml_adapter.models.global_report_models import PortfolioAccount
from data_adapter.xml_adapter.models.query_models import QueryRecord
from data_adapter.xml_adapter.report_builders.bank_account_builder import BankAccountBuilder
from data_adapter.xml_adapter.report_builders.basic_data_report_builder import BasicDataReportBuilder
from data_adapter.xml_adapter.report_builders.checking_account_builder import CheckingAccountBuilder
from data_adapter.xml_adapter.report_builders.credit_card_builder import CreditCardBuilder
from data_adapter.xml_adapter.report_builders.global_report_builder import GlobalReportBuilder
from data_adapter.xml_adapter.xml_extractors.xml_extractor import XmlExtractor


class FullReportBuilder:
    """Orchestrates all sub-builders to produce a FullReport."""

    def parse(self, xml_input: str | bytes) -> FullReport:
        root = self._parse_xml(xml_input)
        extractor = XmlExtractor(root)
        return self._build_full_report(extractor, xml_input)

    def parse_file(self, filepath: str) -> FullReport:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Not found: {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return self.parse(content)

    def _parse_xml(self, xml_input: str | bytes) -> ET.Element:
        try:
            if isinstance(xml_input, str):
                xml_input = xml_input.encode("utf-8")
            return ET.fromstring(xml_input)
        except ET.ParseError as e:
            raise XmlParseError(f"Malformed XML: {e}") from e

    def _build_full_report(self, ex: XmlExtractor, xml_input: str | bytes) -> FullReport:
        basic_builder = BasicDataReportBuilder()
        basic_data: BasicReport = basic_builder.parse(xml_input)

        global_builder = GlobalReportBuilder()
        global_report = global_builder.parse(xml_input)

        reports_node = ex.root if ex.root.tag == "Informes" else ex.find_node("Informes")
        if reports_node is None:
            raise ValueError("Main node 'Informes' not found.")

        report_node = ex.require_node("Informe", parent=reports_node)

        bank_builder = BankAccountBuilder()
        bank_accounts = bank_builder.parse_accounts(ex, report_node)

        checking_builder = CheckingAccountBuilder()
        checking_accounts = checking_builder.parse_accounts(ex, report_node)

        card_builder = CreditCardBuilder()
        credit_cards = card_builder.parse_cards(ex, report_node)

        query_records = self._parse_query_records(ex, report_node)
        global_debt_records = self._parse_global_debt_records(ex, report_node)
        aggregated_info = self._parse_aggregated_info(ex, report_node)

        return FullReport(
            basic_data=basic_data,
            portfolio_accounts=global_report.portfolio_account,
            bank_accounts=bank_accounts,
            checking_accounts=checking_accounts,
            credit_cards=credit_cards,
            query_records=query_records,
            global_debt_records=global_debt_records,
            aggregated_info=aggregated_info,
        )

    def _parse_query_records(
        self,
        ex: XmlExtractor,
        report_node: ET.Element,
    ) -> tuple[QueryRecord, ...]:
        nodes = report_node.findall(".//Consulta")
        return tuple(self._parse_query_record(ex, node) for node in nodes)

    def _parse_query_record(self, ex: XmlExtractor, node: ET.Element) -> QueryRecord:
        return QueryRecord(
            date=ex.get_attr_required(node, "fecha"),
            account_type=ex.get_attr(node, "tipoCuenta"),
            entity=ex.get_attr_required(node, "entidad"),
            office=ex.get_attr(node, "oficina"),
            city=ex.get_attr(node, "ciudad"),
            reason=ex.get_attr(node, "razon"),
            count=ex.get_int(node, "cantidad"),
            subscriber_nit=ex.get_attr(node, "nitSuscriptor"),
            sector=ex.get_attr(node, "sector"),
        )

    def _parse_global_debt_records(
        self,
        ex: XmlExtractor,
        report_node: ET.Element,
    ) -> tuple[GlobalDebtRecord, ...]:
        nodes = report_node.findall(".//EndeudamientoGlobal")
        return tuple(self._parse_global_debt_record(ex, node) for node in nodes)

    def _parse_global_debt_record(self, ex: XmlExtractor, node: ET.Element) -> GlobalDebtRecord:
        entity_node = ex.find_node("Entidad", parent=node)
        entity_name = ex.get_attr(entity_node, "nombre") or ""
        entity = GlobalDebtEntity(
            name=entity_name,
            nit=ex.get_attr(entity_node, "nit"),
            sector=ex.get_attr(entity_node, "sector"),
        )
        return GlobalDebtRecord(
            rating=ex.get_attr(node, "calificacion"),
            source=ex.get_attr(node, "fuente"),
            outstanding_balance=ex.get_float(node, "saldoPendiente"),
            credit_type=ex.get_attr(node, "tipoCredito"),
            currency=ex.get_attr(node, "moneda"),
            credit_count=ex.get_int(node, "numeroCreditos"),
            report_date=ex.get_attr(node, "fechaReporte"),
            entity=entity,
        )

    def _parse_aggregated_info(
        self,
        ex: XmlExtractor,
        report_node: ET.Element,
    ) -> Optional[AggregatedInfo]:
        info_node = ex.find_node("InfoAgregada", parent=report_node)
        if info_node is None:
            return None

        resumen_node = ex.find_node("Resumen", parent=info_node)
        totales_node = ex.find_node("Totales", parent=info_node)
        composition_node = ex.find_node("ComposicionPortafolio", parent=info_node)
        evolution_node = ex.find_node("EvolucionDeuda", parent=info_node)

        summary = self._parse_aggregated_summary(ex, resumen_node)
        account_totals = self._parse_account_type_totals(ex, totales_node)
        grand_totals = self._parse_grand_totals(ex, totales_node)
        portfolio_composition = self._parse_portfolio_composition(ex, composition_node)
        debt_evolution = self._parse_debt_evolution(ex, evolution_node)
        debt_evolution_analysis = self._parse_debt_evolution_analysis(ex, evolution_node)
        balance_history_by_type = self._parse_balance_history_by_type(ex, info_node)

        return AggregatedInfo(
            summary=summary,
            account_totals=account_totals,
            grand_totals=grand_totals,
            portfolio_composition=portfolio_composition,
            debt_evolution=debt_evolution,
            debt_evolution_analysis=debt_evolution_analysis,
            balance_history_by_type=balance_history_by_type,
        )

    def _parse_aggregated_summary(
        self,
        ex: XmlExtractor,
        resumen_node: Optional[ET.Element],
    ) -> AggregatedSummary:
        principals = self._parse_principals(ex, resumen_node)
        balances = self._parse_balances(ex, resumen_node)
        behavior_history = self._parse_behavior_history(ex, resumen_node)
        return AggregatedSummary(
            principals=principals,
            balances=balances,
            behavior_history=behavior_history,
        )

    def _parse_principals(
        self,
        ex: XmlExtractor,
        resumen_node: Optional[ET.Element],
    ) -> AggregatedPrincipals:
        node: Optional[ET.Element] = None
        if resumen_node is not None:
            node = ex.find_node("Principales", parent=resumen_node)
        return AggregatedPrincipals(
            active_credits=ex.get_int(node, "creditoVigentes") or 0,
            closed_credits=ex.get_int(node, "creditosCerrados") or 0,
            current_negative=ex.get_int(node, "creditosActualesNegativos") or 0,
            negative_last_12m=ex.get_int(node, "histNegUlt12Meses") or 0,
            open_savings_checking=ex.get_int(node, "cuentasAbiertasAHOCCB") or 0,
            closed_savings_checking=ex.get_int(node, "cuentasCerradasAHOCCB") or 0,
            queries_last_6m=ex.get_int(node, "consultadasUlt6meses") or 0,
            disputes_current=ex.get_int(node, "desacuerdosALaFecha") or 0,
            oldest_account_date=ex.get_attr(node, "antiguedadDesde"),
            active_claims=ex.get_int(node, "reclamosVigentes") or 0,
        )

    def _parse_balances(
        self,
        ex: XmlExtractor,
        resumen_node: Optional[ET.Element],
    ) -> AggregatedBalances:
        saldos_node: Optional[ET.Element] = None
        if resumen_node is not None:
            saldos_node = ex.find_node("Saldos", parent=resumen_node)

        sector_nodes: list[ET.Element] = []
        month_nodes: list[ET.Element] = []
        if saldos_node is not None:
            sector_nodes = saldos_node.findall("Sector")
            month_nodes = saldos_node.findall("Mes")

        by_sector = tuple(
            SectorBalance(
                sector=ex.get_attr(s, "sector") or "",
                balance=ex.get_float(s, "saldo") or 0.0,
                participation=ex.get_float(s, "participacion") or 0.0,
            )
            for s in sector_nodes
        )
        monthly_history = tuple(
            MonthlyBalance(
                date=ex.get_attr(m, "fecha") or "",
                total_past_due=ex.get_float(m, "saldoTotalMora") or 0.0,
                total_balance=ex.get_float(m, "saldoTotal") or 0.0,
            )
            for m in month_nodes
        )

        return AggregatedBalances(
            total_past_due=ex.get_float(saldos_node, "saldoTotalEnMora") or 0.0,
            past_due_30=ex.get_float(saldos_node, "saldoM30") or 0.0,
            past_due_60=ex.get_float(saldos_node, "saldoM60") or 0.0,
            past_due_90=ex.get_float(saldos_node, "saldoM90") or 0.0,
            monthly_installment=ex.get_float(saldos_node, "cuotaMensual") or 0.0,
            highest_credit_balance=ex.get_float(saldos_node, "saldoCreditoMasAlto") or 0.0,
            total_balance=ex.get_float(saldos_node, "saldoTotal") or 0.0,
            by_sector=by_sector,
            monthly_history=monthly_history,
        )

    def _parse_behavior_history(
        self,
        ex: XmlExtractor,
        resumen_node: Optional[ET.Element],
    ) -> tuple[MonthlyBehavior, ...]:
        if resumen_node is None:
            return ()
        comportamiento_node = ex.find_node("Comportamiento", parent=resumen_node)
        if comportamiento_node is None:
            return ()
        nodes = comportamiento_node.findall("Mes")
        return tuple(
            MonthlyBehavior(
                date=ex.get_attr(m, "fecha") or "",
                behavior=ex.get_attr(m, "comportamiento") or "",
                count=ex.get_int(m, "cantidad") or 0,
            )
            for m in nodes
        )

    def _parse_account_type_totals(
        self,
        ex: XmlExtractor,
        totales_node: Optional[ET.Element],
    ) -> tuple[AccountTypeTotals, ...]:
        if totales_node is None:
            return ()
        nodes = totales_node.findall("TipoCuenta")
        return tuple(
            AccountTypeTotals(
                account_type_code=ex.get_attr(n, "codigoTipo") or "",
                account_type_label=ex.get_attr(n, "tipo") or "",
                debtor_quality=ex.get_attr(n, "calidadDeudor") or "",
                credit_limit=ex.get_float(n, "cupo") or 0.0,
                balance=ex.get_float(n, "saldo") or 0.0,
                past_due=ex.get_float(n, "saldoMora") or 0.0,
                installment=ex.get_float(n, "cuota") or 0.0,
            )
            for n in nodes
        )

    def _parse_grand_totals(
        self,
        ex: XmlExtractor,
        totales_node: Optional[ET.Element],
    ) -> tuple[GrandTotal, ...]:
        if totales_node is None:
            return ()
        nodes = totales_node.findall("Total")
        return tuple(
            GrandTotal(
                debtor_quality=ex.get_attr(n, "calidadDeudor") or "",
                participation=ex.get_float(n, "participacion") or 0.0,
                credit_limit=ex.get_float(n, "cupo") or 0.0,
                balance=ex.get_float(n, "saldo") or 0.0,
                past_due=ex.get_float(n, "saldoMora") or 0.0,
                installment=ex.get_float(n, "cuota") or 0.0,
            )
            for n in nodes
        )

    def _parse_portfolio_composition(
        self,
        ex: XmlExtractor,
        composition_node: Optional[ET.Element],
    ) -> tuple[PortfolioCompositionItem, ...]:
        if composition_node is None:
            return ()
        nodes = composition_node.findall("TipoCuenta")
        return tuple(self._parse_composition_item(ex, n) for n in nodes)

    def _parse_composition_item(
        self,
        ex: XmlExtractor,
        node: ET.Element,
    ) -> PortfolioCompositionItem:
        state_nodes = node.findall("Estado")
        states = tuple(
            PortfolioStateCount(
                state_code=ex.get_attr(s, "codigo") or "",
                count=ex.get_int(s, "cantidad") or 0,
            )
            for s in state_nodes
        )
        return PortfolioCompositionItem(
            account_type=ex.get_attr(node, "tipo") or "",
            debtor_quality=ex.get_attr(node, "calidadDeudor") or "",
            percentage=ex.get_float(node, "porcentaje") or 0.0,
            count=ex.get_int(node, "cantidad") or 0,
            states=states,
        )

    def _parse_debt_evolution(
        self,
        ex: XmlExtractor,
        evolution_node: Optional[ET.Element],
    ) -> tuple[DebtEvolutionQuarter, ...]:
        if evolution_node is None:
            return ()
        nodes = evolution_node.findall("Trimestre")
        return tuple(self._parse_quarter(ex, n) for n in nodes)

    def _parse_quarter(self, ex: XmlExtractor, node: ET.Element) -> DebtEvolutionQuarter:
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

    def _parse_debt_evolution_analysis(
        self,
        ex: XmlExtractor,
        evolution_node: Optional[ET.Element],
    ) -> Optional[DebtEvolutionAnalysis]:
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

    def _parse_balance_history_by_type(
        self,
        ex: XmlExtractor,
        info_node: ET.Element,
    ) -> tuple[BalanceHistoryByType, ...]:
        historico_node = ex.find_node("HistoricoSaldos", parent=info_node)
        if historico_node is None:
            return ()
        type_nodes = historico_node.findall("TipoCuenta")
        return tuple(self._parse_balance_history_type(ex, n) for n in type_nodes)

    def _parse_balance_history_type(
        self,
        ex: XmlExtractor,
        node: ET.Element,
    ) -> BalanceHistoryByType:
        quarter_nodes = node.findall("Trimestre")
        quarters = tuple(
            BalanceHistoryQuarter(
                date=ex.get_attr_required(q, "fecha"),
                total_accounts=ex.get_int(q, "totalCuentas"),
                accounts_considered=ex.get_int(q, "cuentasConsideradas"),
                balance=ex.get_int(q, "saldo"),
            )
            for q in quarter_nodes
        )
        return BalanceHistoryByType(
            account_type=ex.get_attr(node, "tipo") or "",
            quarters=quarters,
        )
