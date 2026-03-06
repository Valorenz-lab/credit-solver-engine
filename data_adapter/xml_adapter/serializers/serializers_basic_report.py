"""
Converts data classes from InformeBasico to serializable dicts (JSON-safe).

If you use DRF, you can replace this with a DRF Serializer.
"""


from data_adapter.xml_adapter.models import Age, BasicDataPerson, BasicReport, CustomerIdentification, QueryMetadata
from data_adapter.xml_adapter.types import SerializedAge, SerializedCustomerIdentification, SerializedMetadata, SerializedPerson, SerializedReport


def serialize_basic_report(report: BasicReport) -> SerializedReport:
    meta = _serialize_metadata(report.metadata)
    persona = _serialize_persona(report.person)
    return {
        "metadata": meta,
        "persona": persona,
    }


def _serialize_metadata(m: QueryMetadata) -> SerializedMetadata:
    return {
        "query_date": m.query_date,
        "answer": m.answer,
        "cod_security": m.cod_security,
        "type_id_entered": m.type_id_entered,
        "id_typed": m.id_typed,
        "last_name_typed": m.last_name_typed,
    }


def _serialize_persona(p: BasicDataPerson) -> SerializedPerson:
    return {
       "names": p.names,
        "first_name": p.first_name,
        "last_name": p.last_name,
        "full_name": p.full_name,
        "gender": p.gender,
        "validated": p.validated,
        "rut": p.rut,
        "customer_identification": _serialize_identification(p.customer_identification),
        "age": _serialize_age(p.age)
    }


def _serialize_identification(i: CustomerIdentification ) -> SerializedCustomerIdentification:
    issue_date = i.issue_date.isoformat() if i.issue_date else None
    return {
        "number": i.number,
        "state": i.state,
        "issue_date": issue_date,
        "city": i.city,
        "department": i.department,
        "gender": i.gender
    }


def _serialize_age(e: Age) -> SerializedAge:
    return {"min": e.min, "max": e.max}