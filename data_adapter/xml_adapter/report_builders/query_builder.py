"""Builder for Consulta nodes → QueryRecord tuples."""

from xml.etree import ElementTree as ET

from data_adapter.transformers.global_report_transformer import transform_account_type
from data_adapter.transformers.shared_transformers import (
    transform_industry_sector,
    transform_query_reason,
)
from data_adapter.xml_adapter.models.query_models import QueryRecord
from data_adapter.xml_adapter.xml_extractors.xml_extractor import XmlExtractor


class QueryBuilder:
    """Parses all <Consulta> nodes within an <Informe> node."""

    def __init__(self, ex: XmlExtractor, report_node: ET.Element) -> None:
        self._ex = ex
        self._report_node = report_node

    def build(self) -> tuple[QueryRecord, ...]:
        nodes = self._report_node.findall(".//Consulta")
        return tuple(self._parse_record(node) for node in nodes)

    def _parse_record(self, node: ET.Element) -> QueryRecord:
        date = self._ex.get_attr_required(node, "fecha")
        entity = self._ex.get_attr_required(node, "entidad")
        record_context: dict[str, str] = {"entity": entity, "date": date}
        return QueryRecord(
            date=date,
            account_type=transform_account_type(
                self._ex.get_attr(node, "tipoCuenta"),
                xml_node="Consulta",
                record_type="QueryRecord",
                record_context=record_context,
            ),
            entity=entity,
            office=self._ex.get_attr(node, "oficina"),
            city=self._ex.get_attr(node, "ciudad"),
            reason=transform_query_reason(
                self._ex.get_attr(node, "razon"),
                record_type="QueryRecord",
                record_context=record_context,
            ),
            count=self._ex.get_int(node, "cantidad"),
            subscriber_nit=self._ex.get_attr(node, "nitSuscriptor"),
            sector=transform_industry_sector(
                self._ex.get_attr(node, "sector"),
                xml_node="Consulta",
                record_type="QueryRecord",
                record_context=record_context,
            ),
        )
