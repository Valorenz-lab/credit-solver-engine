from typing import Optional
from xml.etree import ElementTree as ET

from data_adapter.xml_adapter.models.bank_account_models import BankAccountState, BankAccountValue
from data_adapter.xml_adapter.models.checking_account_models import (
    CheckingAccount,
    CheckingAccountOverdraft,
)
from data_adapter.xml_adapter.xml_extractors.xml_extractor import XmlExtractor


class CheckingAccountReportBuilder:
    """Parses CuentaCorriente nodes into CheckingAccount dataclasses."""

    def parse_accounts(self, ex: XmlExtractor, report_node: ET.Element) -> tuple[CheckingAccount, ...]:
        nodes = report_node.findall(".//CuentaCorriente")
        return tuple(self._parse_account(ex, node) for node in nodes)

    def _parse_account(self, ex: XmlExtractor, node: ET.Element) -> CheckingAccount:
        characteristics_node = ex.find_node("Caracteristicas", parent=node)
        values_node = ex.find_node("Valores", parent=node)
        valor_node = ex.find_node("Valor", parent=values_node) if values_node is not None else None
        state_node = ex.find_node("Estado", parent=node)
        overdraft_node = ex.find_node("Sobregiro", parent=node)

        raw_blocked = ex.get_attr(node, "bloqueada")
        is_blocked = raw_blocked is not None and raw_blocked.lower() in ("true", "1", "s", "si")

        return CheckingAccount(
            lender=ex.get_attr_required(node, "entidad"),
            account_number=ex.get_attr_required(node, "numero"),
            account_class=ex.get_attr(characteristics_node, "clase"),
            opened_date=ex.get_attr(node, "fechaApertura"),
            ownership_situation=ex.get_attr(node, "situacionTitular"),
            is_blocked=is_blocked,
            office=ex.get_attr(node, "oficina"),
            city=ex.get_attr(node, "ciudad"),
            dane_city_code=ex.get_attr(node, "codigoDaneCiudad"),
            sector=ex.get_attr(node, "sector"),
            subscriber_code=ex.get_attr(node, "codSuscriptor"),
            entity_id_type=ex.get_attr(node, "tipoIdentificacion"),
            entity_id=ex.get_attr(node, "identificacion"),
            value=self._parse_value(ex, valor_node),
            state=self._parse_state(ex, state_node),
            overdraft=self._parse_overdraft(ex, overdraft_node),
        )

    def _parse_value(
        self,
        ex: XmlExtractor,
        node: Optional[ET.Element],
    ) -> Optional[BankAccountValue]:
        if node is None:
            return None
        return BankAccountValue(
            currency_code=ex.get_attr(node, "moneda"),
            date=ex.get_attr(node, "fecha"),
            rating=ex.get_attr(node, "calificacion"),
        )

    def _parse_state(
        self,
        ex: XmlExtractor,
        node: Optional[ET.Element],
    ) -> Optional[BankAccountState]:
        if node is None:
            return None
        return BankAccountState(
            code=ex.get_attr(node, "codigo"),
            date=ex.get_attr(node, "fecha"),
        )

    def _parse_overdraft(
        self,
        ex: XmlExtractor,
        node: Optional[ET.Element],
    ) -> Optional[CheckingAccountOverdraft]:
        if node is None:
            return None
        return CheckingAccountOverdraft(
            value=ex.get_float(node, "valor"),
            days=ex.get_int(node, "dias"),
            date=ex.get_attr(node, "fecha"),
        )
