"""
Data classes that represent the information extracted from the Datacredito XML.

Each class maps to a node in the XML and is immutable by default.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import date


@dataclass(frozen=True)
class CustomerIdentification:
    number: str
    state: str
    issue_date: Optional[date]
    city: Optional[str]
    department: Optional[str]
    gender: Optional[str]


@dataclass(frozen=True)
class Age:
    min: Optional[int]
    max: Optional[int]


@dataclass(frozen=True)
class BasicDataPerson:
    # Data from the NaturalNational node
    names: str
    first_surname: str
    second_surname: Optional[str]
    full_name: str
    gender: Optional[str]
    validated: bool
    rut: bool

    # Sub-nodos
    customer_identification: CustomerIdentification
    age: Age


@dataclass(frozen=True)
class QueryMetadata:
    """Root node metadata <Reporte>"""

    query_date: str  # ISO string, ej: "2024-03-22T07:45:03"
    answer: str
    cod_security: str
    type_id_entered: str
    id_typed: str
    last_name_typed: str


@dataclass(frozen=True)
class BasicReport:
    """Complete result of the basic information parse."""

    metadata: QueryMetadata
    person: BasicDataPerson
