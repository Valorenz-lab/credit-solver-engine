"""Builder for EndeudamientoGlobal nodes → GlobalDebtRecord tuples."""

from typing import Optional
from xml.etree import ElementTree as ET

from data_adapter.transformers.global_debt_transformer import (
    transform_global_debt_credit_type,
    transform_global_debt_guarantee,
)
from data_adapter.transformers.shared_transformers import (
    transform_credit_rating,
    transform_currency,
    transform_industry_sector,
)
from data_adapter.xml_adapter.models.global_debt_models import (
    GlobalDebtEntity,
    GlobalDebtGuarantee,
    GlobalDebtRecord,
)
from data_adapter.xml_adapter.xml_extractors.xml_extractor import XmlExtractor


class GlobalDebtBuilder:
    """Parses all <EndeudamientoGlobal> nodes within an <Informe> node."""

    def __init__(self, ex: XmlExtractor, report_node: ET.Element) -> None:
        self._ex = ex
        self._report_node = report_node

    def build(self) -> tuple[GlobalDebtRecord, ...]:
        nodes = self._report_node.findall(".//EndeudamientoGlobal")
        return tuple(self._parse_record(node) for node in nodes)

    def _parse_record(self, node: ET.Element) -> GlobalDebtRecord:
        entity_node = self._ex.find_node("Entidad", parent=node)
        entity_name = self._ex.get_attr(entity_node, "nombre") or ""
        source = self._ex.get_attr(node, "fuente")
        record_context: dict[str, str] = {
            "entity": entity_name,
            "source": source or "",
        }
        entity = GlobalDebtEntity(
            name=entity_name,
            nit=self._ex.get_attr(entity_node, "nit"),
            sector=transform_industry_sector(
                self._ex.get_attr(entity_node, "sector"),
                xml_node="Entidad",
                record_type="GlobalDebtRecord",
                record_context=record_context,
            ),
        )
        return GlobalDebtRecord(
            rating=transform_credit_rating(self._ex.get_attr(node, "calificacion")),
            source=source,
            outstanding_balance=self._ex.get_float(node, "saldoPendiente"),
            credit_type=transform_global_debt_credit_type(
                self._ex.get_attr(node, "tipoCredito"),
                record_type="GlobalDebtRecord",
                record_context=record_context,
            ),
            currency=transform_currency(self._ex.get_attr(node, "moneda")),
            credit_count=self._ex.get_int(node, "numeroCreditos"),
            report_date=self._ex.get_attr(node, "fechaReporte"),
            independent=self._ex.get_attr(node, "independiente"),
            entity=entity,
            guarantee=self._parse_guarantee(node, record_context=record_context),
        )

    def _parse_guarantee(
        self,
        node: ET.Element,
        record_context: Optional[dict[str, str]] = None,
    ) -> Optional[GlobalDebtGuarantee]:
        guarantee_node = self._ex.find_node("Garantia", parent=node)
        if guarantee_node is None:
            return None
        return GlobalDebtGuarantee(
            guarantee_type=transform_global_debt_guarantee(
                self._ex.get_attr(guarantee_node, "tipo"),
                record_type="GlobalDebtRecord",
                record_context=record_context,
            ),
            value=self._ex.get_float(guarantee_node, "valor"),
            date=self._ex.get_attr(guarantee_node, "fecha"),
        )
