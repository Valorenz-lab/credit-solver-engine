"""Builder for Consulta nodes → QueryRecord tuples."""

from xml.etree import ElementTree as ET

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
        return QueryRecord(
            date=self._ex.get_attr_required(node, "fecha"),
            account_type=self._ex.get_attr(node, "tipoCuenta"),
            entity=self._ex.get_attr_required(node, "entidad"),
            office=self._ex.get_attr(node, "oficina"),
            city=self._ex.get_attr(node, "ciudad"),
            reason=self._ex.get_attr(node, "razon"),
            count=self._ex.get_int(node, "cantidad"),
            subscriber_nit=self._ex.get_attr(node, "nitSuscriptor"),
            sector=self._ex.get_attr(node, "sector"),
        )
