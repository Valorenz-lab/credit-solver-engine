from datetime import date
from typing import Optional, TypeVar, overload
from xml.etree import ElementTree as ET
import logging

from data_adapter.xml_adapter.exceptions import XmlInvalidValueError, XmlNodeNotFoundError

logger = logging.getLogger(__name__)

T = TypeVar('T')

class XmlExtractor:
    """Navigate XML safely and tolerantly."""
    
    def __init__(self, root: ET.Element):
        self.root = root
    
    def find_node(self, path: str, parent: Optional[ET.Element] = None) -> Optional[ET.Element]:
        """Search for a node. If it doesn't exist, log and continue."""
        base = parent if parent is not None else self.root
        node = base.find(path)
        if node is None:
            parent_str = ET.tostring(base, encoding='unicode').strip()[:200] 
            logger.warning(f"Node not found {path}.\n Parent: {parent_str}...")

        return node
    
    def require_node(self, path: str, parent: Optional[ET.Element] = None) -> ET.Element:
        """Find a node or raise XmlNodeNotFoundError."""
        node = self.find_node(path, parent)
        if node is None:
            raise XmlNodeNotFoundError(f"Node not found: path:{path}\nparent:{str(parent)}")
        return node
    
    @overload
    def get_attr(self, node: Optional[ET.Element], attr: str) -> str | None: ...
    
    @overload
    def get_attr(self, node: Optional[ET.Element], attr: str, default: T) -> str | T: ...
    
    def get_attr(self, node: Optional[ET.Element], attr: str, default: T | None = None) -> str | T | None:
        """Extract an attribute safely."""
        if node is None:
            return default
        value = node.get(attr)
        if value is None:
            logger.debug(f"Attribute '{attr}' missing in node '{node.tag}'")
            return default
        return value.strip()
    
    def get_attr_required(self, node: ET.Element, attr: str) -> str:
        """Extract required attribute or raise."""
        value = self.get_attr(node, attr)
        if value is None:
            raise XmlNodeNotFoundError(f"{node.tag}@{attr}")
        return value
    
    def get_bool(self, node: ET.Element, attr: str) -> bool:
        """Parse bool attribute."""
        raw = self.get_attr_required(node, attr).lower()
        if raw in ("true", "1"):
            return True
        if raw in ("false", "0"):
            return False
        raise XmlInvalidValueError(attr, raw, "true/false expected")
    
    def get_int(self, node: Optional[ET.Element], attr: str) -> Optional[int]:
        raw = self.get_attr(node, attr)
        if raw is None: return None
        try:
            return int(float(raw))
        except ValueError:
            raise XmlInvalidValueError(attr, raw, "integer expected")
    
    def get_float(self, node: Optional[ET.Element], attr: str) -> Optional[float]:
        raw = self.get_attr(node, attr)
        if raw is None: return None
        try:
            return float(raw)
        except ValueError:
            raise XmlInvalidValueError(attr, raw, "float expected")

    def get_date(self, node: Optional[ET.Element], attr: str) -> Optional[date]:
        """Parse date attribute (optional)."""
        raw = self.get_attr(node, attr)
        if not raw:
            return None
        try:
            return date.fromisoformat(raw)
        except ValueError:
            raise XmlInvalidValueError(attr, raw, "expected format: YYYY-MM-DD")