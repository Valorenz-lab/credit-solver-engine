from typing import Optional
from xml.etree import ElementTree as ET

from data_adapter.transformers.shared_transformers import (
    transform_credit_rating,
    transform_currency,
    transform_industry_sector,
    transform_ownership_situation,
    transform_savings_account_status,
)
from data_adapter.xml_adapter.models.bank_account_models import BankAccount, BankAccountState, BankAccountValue
from data_adapter.xml_adapter.xml_extractors.xml_extractor import XmlExtractor


class BankAccountReportBuilder:
    """Parses CuentaAhorro nodes into BankAccount dataclasses."""

    def parse_accounts(self, ex: XmlExtractor, report_node: ET.Element) -> tuple[BankAccount, ...]:
        nodes = report_node.findall(".//CuentaAhorro")
        return tuple(self._parse_account(ex, node) for node in nodes)

    def _parse_account(self, ex: XmlExtractor, node: ET.Element) -> BankAccount:
        characteristics_node = ex.find_node("Caracteristicas", parent=node)
        values_node = ex.find_node("Valores", parent=node)
        valor_node = ex.find_node("Valor", parent=values_node) if values_node is not None else None
        state_node = ex.find_node("Estado", parent=node)

        return BankAccount(
            lender=ex.get_attr_required(node, "entidad"),
            account_number=ex.get_attr_required(node, "numero"),
            account_class=ex.get_attr(characteristics_node, "clase"),
            opened_date=ex.get_attr(node, "fechaApertura"),
            rating=transform_credit_rating(ex.get_attr(node, "calificacion")),
            ownership_situation=transform_ownership_situation(ex.get_attr(node, "situacionTitular")),
            is_blocked=self._parse_blocked(ex, node),
            office=ex.get_attr(node, "oficina"),
            city=ex.get_attr(node, "ciudad"),
            dane_city_code=ex.get_attr(node, "codigoDaneCiudad"),
            sector=transform_industry_sector(ex.get_attr(node, "sector")),
            entity_id_type=ex.get_attr(node, "tipoIdentificacion"),
            entity_id=ex.get_attr(node, "identificacion"),
            value=self._parse_value(ex, valor_node),
            state=self._parse_state(ex, state_node),
        )

    def _parse_blocked(self, ex: XmlExtractor, node: ET.Element) -> bool:
        raw = ex.get_attr(node, "bloqueada")
        if raw is None:
            return False
        return raw.lower() in ("true", "1", "s", "si")

    def _parse_value(
        self,
        ex: XmlExtractor,
        node: Optional[ET.Element],
    ) -> Optional[BankAccountValue]:
        if node is None:
            return None
        return BankAccountValue(
            currency_code=transform_currency(ex.get_attr(node, "moneda")),
            date=ex.get_attr(node, "fecha"),
            rating=transform_credit_rating(ex.get_attr(node, "calificacion")),
        )

    def _parse_state(
        self,
        ex: XmlExtractor,
        node: Optional[ET.Element],
    ) -> Optional[BankAccountState]:
        if node is None:
            return None
        return BankAccountState(
            code=transform_savings_account_status(ex.get_attr(node, "codigo")),
            date=ex.get_attr(node, "fecha"),
        )
