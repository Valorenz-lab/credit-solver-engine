from collections import Counter
from pathlib import Path

from django.conf import settings
from django.http import HttpRequest, JsonResponse

from data_adapter import debug_tracer
from data_adapter.debug_tracer import DebugTrace
from data_adapter.xml_adapter.extraction_validator import validate_extraction
from data_adapter.xml_adapter.report_builders.basic_data_report_builder import (
    BasicDataReportBuilder,
)
from data_adapter.xml_adapter.report_builders.full_report_report_builder import (
    FullReportBuilder,
)
from data_adapter.xml_adapter.report_builders.global_report_report_builder import (
    GlobalReportBuilder,
)
from data_adapter.xml_adapter.serializers.serializer_full_report import (
    serialize_full_report,
)
from data_adapter.xml_adapter.serializers.serializer_global_report import (
    serialize_global_report,
)
from data_adapter.xml_adapter.serializers.serializer_basic_report import (
    serialize_basic_report,
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def basic_report(request: HttpRequest, document_id: str) -> JsonResponse:
    xml_path = DATA_DIR / f"{document_id}.xml"

    if not xml_path.exists():
        return JsonResponse(
            {"error": f"No XML found for document_id '{document_id}'"}, status=404
        )

    parser_basic = BasicDataReportBuilder()
    inform1 = parser_basic.parse_file(str(xml_path))
    data = serialize_basic_report(inform1)

    parser_global = GlobalReportBuilder()
    inform2 = parser_global.parse_file(str(xml_path))
    data_global = serialize_global_report(inform2)

    return JsonResponse(
        {
            "basic_report": data,
            "global_report": data_global,
        }
    )


def full_report(request: HttpRequest, document_id: str) -> JsonResponse:
    xml_path = DATA_DIR / f"{document_id}.xml"

    if not xml_path.exists():
        return JsonResponse({"error": f"No XML found for '{document_id}'"}, status=404)

    builder = FullReportBuilder()
    report = builder.parse_file(str(xml_path))
    data = serialize_full_report(report)

    return JsonResponse(data)


def extraction_quality_report(request: HttpRequest, document_id: str) -> JsonResponse:
    xml_path = DATA_DIR / f"{document_id}.xml"

    if not xml_path.exists():
        return JsonResponse({"error": f"No XML found for '{document_id}'"}, status=404)

    result = validate_extraction(str(xml_path))
    result["document_id"] = document_id
    return JsonResponse(result)


def _serialize_trace(trace: DebugTrace, document_id: str) -> dict[str, object]:
    events = [
        {
            "transformer": e.transformer,
            "raw_value": e.raw_value,
            "xml_node": e.xml_node,
            "xml_attribute": e.xml_attribute,
            "record_type": e.record_type,
            "record_context": e.record_context,
        }
        for e in trace.events
    ]

    by_transformer: dict[str, int] = dict(
        Counter(e.transformer for e in trace.events)
    )
    by_raw_value: dict[str, int] = dict(
        Counter(e.raw_value if e.raw_value is not None else "null" for e in trace.events)
    )
    affected_records = len(
        {
            (e.record_type, tuple(sorted(e.record_context.items())))
            for e in trace.events
        }
    )

    return {
        "document_id": document_id,
        "unknown_events": events,
        "summary": {
            "total_unknown_events": len(events),
            "by_transformer": by_transformer,
            "by_raw_value": by_raw_value,
            "affected_records": affected_records,
        },
    }


def extraction_debug_report(request: HttpRequest, document_id: str) -> JsonResponse:
    if not getattr(settings, "EXTRACTION_DEBUG", False):
        return JsonResponse({"error": "Debug mode is disabled"}, status=403)

    xml_path = DATA_DIR / f"{document_id}.xml"
    if not xml_path.exists():
        return JsonResponse({"error": f"No XML found for '{document_id}'"}, status=404)

    trace = debug_tracer.start_trace()
    try:
        FullReportBuilder().parse_file(str(xml_path))
    finally:
        debug_tracer.end_trace()

    return JsonResponse(_serialize_trace(trace, document_id))
