"""Builders for Score and Alerta nodes."""

from typing import Optional
from xml.etree import ElementTree as ET

from data_adapter.xml_adapter.models.score_alert_models import (
    AlertRecord,
    AlertSource,
    ScoreReason,
    ScoreRecord,
)
from data_adapter.xml_adapter.xml_extractors.xml_extractor import XmlExtractor


class ScoreBuilder:
    """Parses all <Score> nodes within an <Informe> node."""

    def __init__(self, ex: XmlExtractor, report_node: ET.Element) -> None:
        self._ex = ex
        self._report_node = report_node

    def build(self) -> tuple[ScoreRecord, ...]:
        return tuple(self._parse_record(n) for n in self._report_node.findall("Score"))

    def _parse_record(self, node: ET.Element) -> ScoreRecord:
        reasons = tuple(
            ScoreReason(code=self._ex.get_attr_required(r, "codigo"))
            for r in node.findall("Razon")
        )
        return ScoreRecord(
            score_type=self._ex.get_attr_required(node, "tipo"),
            score_value=self._ex.get_float(node, "puntaje") or 0.0,
            classification=self._ex.get_attr(node, "clasificacion"),
            population_pct=self._ex.get_int(node, "poblacion"),
            date=self._ex.get_attr_required(node, "fecha"),
            reasons=reasons,
        )


class AlertBuilder:
    """Parses all <Alerta> nodes within an <Informe> node."""

    def __init__(self, ex: XmlExtractor, report_node: ET.Element) -> None:
        self._ex = ex
        self._report_node = report_node

    def build(self) -> tuple[AlertRecord, ...]:
        return tuple(self._parse_record(n) for n in self._report_node.findall("Alerta"))

    def _parse_record(self, node: ET.Element) -> AlertRecord:
        source: Optional[AlertSource] = None
        source_node = self._ex.find_node("Fuente", parent=node)
        if source_node is not None:
            source = AlertSource(
                code=self._ex.get_attr_required(source_node, "codigo"),
                name=self._ex.get_attr(source_node, "nombre"),
            )
        return AlertRecord(
            placed_date=self._ex.get_attr_required(node, "colocacion"),
            expiry_date=self._ex.get_attr_required(node, "vencimiento"),
            cancelled_date=self._ex.get_attr(node, "modificacion"),
            code=self._ex.get_attr_required(node, "codigo"),
            text=self._ex.get_attr(node, "texto"),
            source=source,
        )
