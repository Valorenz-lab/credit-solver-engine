"""
Parser of Datacredito XML (Experian).
Single responsibility: receive XML as string/bytes/Path and return dataclasses.
Does not transform codes — returns raw values from the XML.
"""

import os

from data_adapter.xml_adapter.exceptions import XmlParseError
from data_adapter.xml_adapter.models.global_report_models import AccountStatus, GlobalReport, PortfolioAccount, PortfolioCharacteristics, PortfolioValues
from data_adapter.xml_adapter.xml_extractors.xml_extractor import XmlExtractor
from xml.etree import ElementTree as ET


class GlobalReportBuilder:
    """
    Parses Datacredito XML using XmlExtractor for safe navigation.
    """

    def parse(self, xml_input: str | bytes) -> GlobalReport:
        root = self._parse_xml(xml_input)
        # We initialize the extractor with the root
        extractor = XmlExtractor(root)
        return self._build_report(extractor)


    def parse_file(self, filepath: str) -> GlobalReport:
        """For local development/testing only."""
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

    def _build_report(self, ex: XmlExtractor) -> GlobalReport:
        # We search for the main node
        reports_node = ex.root if ex.root.tag == "Informes" else ex.find_node("Informes")
        
        if reports_node is None:
            raise ValueError("The main node 'Informes' was not found.")

        report_node = ex.require_node("Informe", parent=reports_node)

        return GlobalReport(
            portfolio_account=self._parse_accounts_portfolio(ex, report_node),
        )

    def _parse_accounts_portfolio(self, ex: XmlExtractor, report_node: ET.Element) -> tuple[PortfolioAccount, ...]:
        nodos = report_node.findall(".//CuentaCartera")
        return tuple(self._parse_account_wallet(ex, n) for n in nodos)

    def _parse_account_wallet(self, ex: XmlExtractor, node: ET.Element) -> PortfolioAccount:
        return PortfolioAccount(
            lender=ex.get_attr_required(node, "entidad"),
            account_number=ex.get_attr_required(node, "numero"),
            opened_date=ex.get_attr(node, "fechaApertura"),
            maturity_date=ex.get_attr(node, "fechaVencimiento"),
            payment_history=ex.get_attr(node, "comportamiento"),
            credit_rating=ex.get_attr(node, "calificacion"),
            ownership_status=ex.get_attr(node, "situacionTitular"),
            is_blocked=ex.get_bool(node, "bloqueada"),
            city=ex.get_attr(node, "ciudad"),
            industry_sector=ex.get_attr(node, "sector"),
            default_probability=ex.get_float(node, "probabilidadIncumplimiento"),
            characteristics=self._parse_characteristics(ex, node),
            values=self._parse_value_portfolio(ex, node),
            account_status=self._parse_states(ex, node),
        )

    def _parse_characteristics(self, ex: XmlExtractor, parent: ET.Element) -> PortfolioCharacteristics:
        node = ex.find_node("Caracteristicas", parent=parent)
        # If the node does not exist, we return an object with Nones using the advantages of the extractor
        return PortfolioCharacteristics(
            account_type=ex.get_attr(node, "tipoCuenta"),
            obligation_type=ex.get_attr(node, "tipoObligacion"),
            contract_type=ex.get_attr(node, "tipoContrato"),
            contract_execution=ex.get_attr(node, "ejecucionContrato"),
            debtor_quality=ex.get_attr(node, "calidadDeudor"),
            guarantee=ex.get_attr(node, "garantia"),
        )

    def _parse_value_portfolio(self, ex: XmlExtractor, parent: ET.Element) -> PortfolioValues:
        # Safe browsing: Values ​​-> Value
        values_parent = ex.find_node("Valores", parent=parent)
        node = ex.find_node("Valor", parent=values_parent) if values_parent is not None else None
  
            
        return PortfolioValues(
            date=ex.get_attr(node, "fecha"),
            currency_code=ex.get_attr(node, "moneda"),
            credit_rating=ex.get_attr(node, "calificacion"),
            outstanding_balance=ex.get_float(node, "saldoActual"),
            past_due_amount=ex.get_float(node, "saldoMora"),
            available_limit=ex.get_float(node, "disponible"),
            installment_value=ex.get_float(node, "cuota"),
            missed_payments=ex.get_int(node, "cuotasMora"),
            total_installments=ex.get_int(node, "totalCuotas"),
            installments_paid=ex.get_int(node, "cuotasCanceladas"),
            principal_amount=ex.get_float(node, "valorInicial"),
            due_date=ex.get_attr(node, "fechaLimitePago"),
            payment_frequency=ex.get_attr(node, "periodicidad"),
            last_payment_date=ex.get_attr(node, "fechaPagoCuota"),
            days_past_due=ex.get_int(node, "diasMora")
        )

    def _parse_states(self, ex: XmlExtractor, parent: ET.Element) -> AccountStatus:
        states_node = ex.find_node("Estados", parent=parent)
        if states_node is None:
            return AccountStatus(None, None, None, None, None, None, None)

        ec = ex.find_node("EstadoCuenta", parent=states_node)
        eo = ex.find_node("EstadoOrigen", parent=states_node)
        ep = ex.find_node("EstadoPago", parent=states_node)

        return AccountStatus(
            account_statement_code=ex.get_attr(ec, "codigo"),
            account_statement_date=ex.get_attr(ec, "fecha"),
            origin_state_code=ex.get_attr(eo, "codigo"),
            origin_statement_date=ex.get_attr(eo, "fecha"),
            payment_status_code=ex.get_attr(ep, "codigo"),
            payment_status_months=ex.get_attr(ep, "meses"),
            payment_status_date=ex.get_attr(ep, "fecha"),
        )