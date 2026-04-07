"""
Parser of Datacredito XML (Experian).
Single responsibility: receive XML as string/bytes/Path and return dataclasses.
"""

import os
from typing import Optional

from data_adapter.transformers.global_report_transformer import (
    transform_account_condition,
    transform_account_type,
    transform_contract_type,
    transform_debtor_role,
    transform_obligation_type,
    transform_payment_frequency,
)
from data_adapter.transformers.shared_transformers import (
    transform_credit_rating,
    transform_currency,
    transform_guarantee,
    transform_industry_sector,
    transform_origin_state,
    transform_ownership_situation,
    transform_payment_status,
)
from data_adapter.xml_adapter.exceptions import XmlParseError
from data_adapter.xml_adapter.models.global_report_models import (
    GlobalReport,
    PortfolioAccount,
    PortfolioCharacteristics,
    PortfolioStates,
    PortfolioValues,
)
from data_adapter.xml_adapter.xml_extractors.xml_extractor import XmlExtractor
from xml.etree import ElementTree as ET


class GlobalReportBuilder:
    """
    Parses Datacredito XML using XmlExtractor for safe navigation.
    """

    def parse(self, xml_input: str | bytes) -> GlobalReport:
        root = self._parse_xml(xml_input)
        extractor = XmlExtractor(root)
        return self._build_report(extractor)

    def build_from_node(
        self, ex: XmlExtractor, report_node: ET.Element
    ) -> GlobalReport:
        """Build a GlobalReport from an already-parsed extractor and Informe node.

        Use this when the caller already holds an XmlExtractor to avoid
        re-parsing the XML from scratch.
        """
        return GlobalReport(
            portfolio_account=self._parse_accounts_portfolio(ex, report_node),
        )

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
        reports_node = (
            ex.root if ex.root.tag == "Informes" else ex.find_node("Informes")
        )
        if reports_node is None:
            raise ValueError("The main node 'Informes' was not found.")
        report_node = ex.require_node("Informe", parent=reports_node)
        return self.build_from_node(ex, report_node)

    def _parse_accounts_portfolio(
        self, ex: XmlExtractor, report_node: ET.Element
    ) -> tuple[PortfolioAccount, ...]:
        nodos = report_node.findall(".//CuentaCartera")
        return tuple(self._parse_account_wallet(ex, n) for n in nodos)

    def _parse_account_wallet(
        self, ex: XmlExtractor, node: ET.Element
    ) -> PortfolioAccount:
        raw_hd = ex.get_attr(node, "calificacionHD")
        raw_blocked = ex.get_attr(node, "bloqueada")
        lender = ex.get_attr_required(node, "entidad")
        account_number = ex.get_attr_required(node, "numero")
        record_context: dict[str, str] = {
            "lender": lender,
            "account_number": account_number,
        }
        return PortfolioAccount(
            lender=lender,
            account_number=account_number,
            opened_date=ex.get_attr(node, "fechaApertura"),
            maturity_date=ex.get_attr(node, "fechaVencimiento"),
            payment_history=ex.get_attr(node, "comportamiento"),
            credit_rating=transform_credit_rating(ex.get_attr(node, "calificacion")),
            ownership_status=transform_ownership_situation(
                ex.get_attr(node, "situacionTitular"),
                xml_node="CuentaCartera",
                record_type="PortfolioAccount",
                record_context=record_context,
            ),
            is_blocked=raw_blocked is not None
            and raw_blocked.lower() in ("true", "1", "s", "si"),
            city=ex.get_attr(node, "ciudad"),
            dane_city_code=ex.get_attr(node, "codigoDaneCiudad"),
            industry_sector=transform_industry_sector(
                ex.get_attr(node, "sector"),
                xml_node="CuentaCartera",
                record_type="PortfolioAccount",
                record_context=record_context,
            ),
            default_probability=ex.get_float(node, "probabilidadIncumplimiento"),
            subscriber_code=ex.get_attr(node, "codSuscriptor"),
            entity_id_type=ex.get_attr(node, "tipoIdentificacion"),
            entity_id=ex.get_attr(node, "identificacion"),
            hd_rating=raw_hd is not None and raw_hd.lower() in ("true", "1"),
            characteristics=self._parse_characteristics(ex, node, record_context=record_context),
            values=self._parse_value_portfolio(ex, node, record_context=record_context),
            states=self._parse_states(ex, node, record_context=record_context),
        )

    def _parse_characteristics(
        self,
        ex: XmlExtractor,
        parent: ET.Element,
        record_context: Optional[dict[str, str]] = None,
    ) -> PortfolioCharacteristics:
        node = ex.find_node("Caracteristicas", parent=parent)
        return PortfolioCharacteristics(
            account_type=transform_account_type(
                ex.get_attr(node, "tipoCuenta"),
                xml_node="Caracteristicas",
                record_type="PortfolioAccount",
                record_context=record_context,
            ),
            obligation_type=transform_obligation_type(
                ex.get_attr(node, "tipoObligacion"),
                record_type="PortfolioAccount",
                record_context=record_context,
            ),
            contract_type=transform_contract_type(
                ex.get_attr(node, "tipoContrato"),
                record_type="PortfolioAccount",
                record_context=record_context,
            ),
            contract_execution=ex.get_attr(node, "ejecucionContrato"),
            debtor_quality=transform_debtor_role(
                ex.get_attr(node, "calidadDeudor"),
                record_type="PortfolioAccount",
                record_context=record_context,
            ),
            guarantee=transform_guarantee(
                ex.get_attr(node, "garantia"),
                xml_node="Caracteristicas",
                record_type="PortfolioAccount",
                record_context=record_context,
            ),
            permanence_months=ex.get_int(node, "mesesPermanencia"),
        )

    def _parse_value_portfolio(
        self,
        ex: XmlExtractor,
        parent: ET.Element,
        record_context: Optional[dict[str, str]] = None,
    ) -> PortfolioValues:
        # Safe browsing: Values ​​-> Value
        values_parent = ex.find_node("Valores", parent=parent)
        node = (
            ex.find_node("Valor", parent=values_parent)
            if values_parent is not None
            else None
        )

        return PortfolioValues(
            date=ex.get_attr(node, "fecha"),
            currency_code=transform_currency(ex.get_attr(node, "moneda")),
            credit_rating=transform_credit_rating(ex.get_attr(node, "calificacion")),
            outstanding_balance=ex.get_float(node, "saldoActual"),
            past_due_amount=ex.get_float(node, "saldoMora"),
            available_limit=ex.get_float(node, "disponible"),
            installment_value=ex.get_float(node, "cuota"),
            missed_payments=ex.get_int(node, "cuotasMora"),
            total_installments=ex.get_int(node, "totalCuotas"),
            installments_paid=ex.get_int(node, "cuotasCanceladas"),
            principal_amount=ex.get_float(node, "valorInicial"),
            due_date=ex.get_attr(node, "fechaLimitePago"),
            payment_frequency=transform_payment_frequency(
                ex.get_attr(node, "periodicidad"),
                record_type="PortfolioAccount",
                record_context=record_context,
            ),
            last_payment_date=ex.get_attr(node, "fechaPagoCuota"),
            days_past_due=ex.get_int(node, "diasMora"),
        )

    def _parse_states(
        self,
        ex: XmlExtractor,
        parent: ET.Element,
        record_context: Optional[dict[str, str]] = None,
    ) -> PortfolioStates:
        states_node = ex.find_node("Estados", parent=parent)
        if states_node is None:
            return PortfolioStates(None, None, None, None, None, None, None)

        ec = ex.find_node("EstadoCuenta", parent=states_node)
        eo = ex.find_node("EstadoOrigen", parent=states_node)
        ep = ex.find_node("EstadoPago", parent=states_node)

        return PortfolioStates(
            account_statement_code=transform_account_condition(
                ex.get_attr(ec, "codigo"),
                record_type="PortfolioAccount",
                record_context=record_context,
            ),
            account_statement_date=ex.get_attr(ec, "fecha"),
            origin_state_code=transform_origin_state(
                ex.get_attr(eo, "codigo"),
                record_type="PortfolioAccount",
                record_context=record_context,
            ),
            origin_statement_date=ex.get_attr(eo, "fecha"),
            payment_status_code=transform_payment_status(
                ex.get_attr(ep, "codigo"),
                record_type="PortfolioAccount",
                record_context=record_context,
            ),
            payment_status_months=ex.get_attr(ep, "meses"),
            payment_status_date=ex.get_attr(ep, "fecha"),
        )
