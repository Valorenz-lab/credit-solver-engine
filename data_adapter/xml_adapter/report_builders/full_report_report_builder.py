"""
Full report builder for Datacredito XML.
Pure orchestrator: delegates every node to its dedicated builder.
"""

import os
from xml.etree import ElementTree as ET

from data_adapter.xml_adapter.exceptions import XmlParseError
from data_adapter.xml_adapter.models.basic_data_models import BasicReport
from data_adapter.xml_adapter.models.full_report_models import FullReport
from data_adapter.xml_adapter.models.global_report_models import GlobalReport
from data_adapter.xml_adapter.report_builders.aggregated_info_builder import AggregatedInfoBuilder
from data_adapter.xml_adapter.report_builders.bank_account_report_builder import BankAccountReportBuilder
from data_adapter.xml_adapter.report_builders.basic_data_report_builder import BasicDataReportBuilder
from data_adapter.xml_adapter.report_builders.checking_account_report_builder import CheckingAccountReportBuilder
from data_adapter.xml_adapter.report_builders.credit_card_report_builder import CreditCardReportBuilder
from data_adapter.xml_adapter.report_builders.global_debt_builder import GlobalDebtBuilder
from data_adapter.xml_adapter.report_builders.global_report_report_builder import GlobalReportBuilder
from data_adapter.xml_adapter.report_builders.micro_credit_builder import MicroCreditBuilder
from data_adapter.xml_adapter.report_builders.query_builder import QueryBuilder
from data_adapter.xml_adapter.report_builders.score_alert_builder import AlertBuilder, ScoreBuilder
from data_adapter.xml_adapter.xml_extractors.xml_extractor import XmlExtractor


class FullReportBuilder:
    """Orchestrates all sub-builders to produce a FullReport from a single XML parse."""

    def parse(self, xml_input: str | bytes) -> FullReport:
        root = self._parse_xml(xml_input)
        return self._build(XmlExtractor(root))

    def parse_file(self, filepath: str) -> FullReport:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Not found: {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            return self.parse(f.read())

    def _parse_xml(self, xml_input: str | bytes) -> ET.Element:
        try:
            if isinstance(xml_input, str):
                xml_input = xml_input.encode("utf-8")
            return ET.fromstring(xml_input)
        except ET.ParseError as e:
            raise XmlParseError(f"Malformed XML: {e}") from e

    def _build(self, ex: XmlExtractor) -> FullReport:
        reports_node = ex.root if ex.root.tag == "Informes" else ex.find_node("Informes")
        if reports_node is None:
            raise ValueError("Main node 'Informes' not found.")

        report_node = ex.require_node("Informe", parent=reports_node)

        basic_data: BasicReport = BasicDataReportBuilder().build_from_node(ex, report_node)
        global_report: GlobalReport = GlobalReportBuilder().build_from_node(ex, report_node)

        return FullReport(
            basic_data=basic_data,
            portfolio_accounts=global_report.portfolio_account,
            bank_accounts=BankAccountReportBuilder().parse_accounts(ex, report_node),
            checking_accounts=CheckingAccountReportBuilder().parse_accounts(ex, report_node),
            credit_cards=CreditCardReportBuilder().parse_cards(ex, report_node),
            query_records=QueryBuilder(ex, report_node).build(),
            global_debt_records=GlobalDebtBuilder(ex, report_node).build(),
            aggregated_info=AggregatedInfoBuilder(ex, report_node).build(),
            micro_credit_info=MicroCreditBuilder(ex, report_node).build(),
            score_records=ScoreBuilder(ex, report_node).build(),
            alert_records=AlertBuilder(ex, report_node).build(),
        )
