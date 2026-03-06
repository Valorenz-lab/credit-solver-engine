"""
XML_adapter exceptions.

Allows upper layers (views, services) to catch parsing-specific errors without relying on lxml or xml.etree.
"""


class XmlAdapterError(Exception):
    """Base for all adapter errors."""
    pass


class XmlParseError(XmlAdapterError):
    """The XML is malformed or could not be parsed."""
    pass


class XmlNodeNotFoundError(XmlAdapterError):
    """An required node does not exist in the XML."""
    def __init__(self, node_name: str):
        self.node_name = node_name
        super().__init__(f"Required node not found in XML: <{node_name}>")


class XmlInvalidValueError(XmlAdapterError):
    """An XML value does not have the expected format."""
    def __init__(self, field_name: str, raw_value: str, reason: str = ""):
        self.field_name = field_name
        self.raw_value = raw_value
        super().__init__(
            f"Invalid value in field '{field_name}': '{raw_value}'"
            + (f" — {reason}" if reason else "")
        )