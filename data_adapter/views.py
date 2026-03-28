from pathlib import Path

from django.http import HttpRequest, JsonResponse

from data_adapter.xml_adapter.report_builders.basic_data_report_builder import BasicDataReportBuilder
from data_adapter.xml_adapter.report_builders.full_report_report_builder import FullReportBuilder
from data_adapter.xml_adapter.report_builders.global_report_report_builder import GlobalReportBuilder
from data_adapter.xml_adapter.serializers.serializer_full_report import serialize_full_report
from data_adapter.xml_adapter.serializers.serializer_global_report import serialize_global_report
from data_adapter.xml_adapter.serializers.serializer_basic_report import serialize_basic_report


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def basic_report(request: HttpRequest, document_id: str) -> JsonResponse:
    xml_path = DATA_DIR / f"{document_id}.xml"

    if not xml_path.exists():
        return JsonResponse({"error": f"No XML found for document_id '{document_id}'"}, status=404)

    parser_basic = BasicDataReportBuilder()
    inform1 = parser_basic.parse_file(str(xml_path))
    data = serialize_basic_report(inform1)

    parser_global = GlobalReportBuilder()
    inform2 = parser_global.parse_file(str(xml_path))
    data_global = serialize_global_report(inform2)

    return JsonResponse({
        "basic_report": data,
        "global_report": data_global,
    })


def full_report(request: HttpRequest, document_id: str) -> JsonResponse:
    xml_path = DATA_DIR / f"{document_id}.xml"

    if not xml_path.exists():
        return JsonResponse({"error": f"No XML found for '{document_id}'"}, status=404)

    builder = FullReportBuilder()
    report = builder.parse_file(str(xml_path))
    data = serialize_full_report(report)

    return JsonResponse(data)

