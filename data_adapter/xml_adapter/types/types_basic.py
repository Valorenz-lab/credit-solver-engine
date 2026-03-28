from typing import Optional, TypedDict


class SerializedMetadata(TypedDict):
    query_date: str
    answer: str
    cod_security: str
    type_id_entered: str
    id_typed: str
    last_name_typed: str


class SerializedCustomerIdentification(TypedDict):
    number: str
    state: str
    issue_date: Optional[str]
    city: Optional[str]
    department: Optional[str]
    gender: Optional[str]


class SerializedAge(TypedDict):
    min: Optional[int]
    max: Optional[int]


class SerializedPerson(TypedDict):
    names: str
    first_name: str
    last_name: Optional[str]
    full_name: str
    gender: Optional[str]
    validated: bool
    rut: bool
    customer_identification: SerializedCustomerIdentification
    age: SerializedAge


class SerializedReport(TypedDict):
    metadata: SerializedMetadata
    persona: SerializedPerson
