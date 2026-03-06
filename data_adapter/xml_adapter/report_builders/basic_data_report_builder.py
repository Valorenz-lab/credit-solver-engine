"""
Data Credit XML Parser (Experian).

Single responsibility: receive XML as strings or bytes and return typed data classes. No knowledge of Django, DRF, or databases.
"""

import os
from xml.etree import ElementTree as ET

from data_adapter.xml_adapter.exceptions import XmlParseError
from data_adapter.xml_adapter.models import Age, BasicDataPerson, BasicReport, CustomerIdentification, CustomerIdentification, QueryMetadata
from data_adapter.xml_adapter.xml_extractors.xml_extractor import XmlExtractor


class BasicDataReportBuilder:
    """Parses the data credit XML."""

    def parse(self, xml_input: str | bytes) -> BasicReport:
        """Receives XML as a string or bytes, returns a BasicReport."""
        root = self._parse_xml(xml_input)
        extractor = XmlExtractor(root)
        return self._build_report(extractor)

    def parse_file(self, filepath: str) -> BasicReport:
        """For local development/testing only."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Not found: {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            return self.parse(f.read())

    # --- Parsing ---

    def _parse_xml(self, xml_input: str | bytes) -> ET.Element:
        try:
            if isinstance(xml_input, str):
                xml_input = xml_input.encode("utf-8")
            return ET.fromstring(xml_input)
        except ET.ParseError as e:
            raise XmlParseError(f"XML malformed: {e}") from e

    def _build_report(self, extractor: XmlExtractor) -> BasicReport:
        report_node = extractor.require_node("Informe")
        natural_node = extractor.require_node("NaturalNacional", report_node)
        
        meta = self._parse_metadata(extractor, report_node)
        person = self._parse_persona(extractor, natural_node)
        
        return BasicReport(metadata=meta, person=person)

    def _parse_metadata(self, extractor: XmlExtractor, node: ET.Element) -> QueryMetadata:
        return QueryMetadata(
            query_date=extractor.get_attr_required(node, "fechaConsulta"),
            answer=extractor.get_attr_required(node, "respuesta"),
            cod_security=extractor.get_attr_required(node, "codSeguridad"),
            type_id_entered=extractor.get_attr_required(node, "tipoIdDigitado"),
            id_typed=extractor.get_attr_required(node, "identificacionDigitada"),
            last_name_typed=extractor.get_attr_required(node, "apellidoDigitado")
        )

    def _parse_persona(self, extractor: XmlExtractor, node: ET.Element) -> BasicDataPerson:
        return BasicDataPerson(
            names=extractor.get_attr_required(node, "nombres"),
            first_name=extractor.get_attr_required(node, "primerApellido"),
            last_name=extractor.get_attr(node, "segundoApellido"),
            full_name=extractor.get_attr_required(node, "nombreCompleto"),
            gender=extractor.get_attr(node, "genero"),
            validated=extractor.get_bool(node, "validada"),
            rut=extractor.get_bool(node, "rut"),
            customer_identification=self._parse_identification(extractor, node),
            age=self._parse_edad(extractor, node),
        )

    def _parse_identification(self, extractor: XmlExtractor, parent: ET.Element) -> CustomerIdentification:
        node = extractor.require_node("Identificacion", parent)
        return CustomerIdentification(
            number=extractor.get_attr_required(node, "numero"),
            state=extractor.get_attr_required(node, "estado"),
            issue_date=extractor.get_date(node, "fechaExpedicion"),
            city=extractor.get_attr(node, "ciudad"),
            department=extractor.get_attr(node, "departamento"),
            gender=extractor.get_attr(node, "genero")
        )

    def _parse_edad(self, extractor: XmlExtractor, parent: ET.Element) -> Age:
        node = extractor.find_node("Edad", parent)
        if node is None:
            return Age(min=None, max=None)
        
        return Age(
            min=extractor.get_int(node, "min"),
            max=extractor.get_int(node, "max"),
        )