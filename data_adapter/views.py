from django.http import HttpRequest, JsonResponse
from data_adapter.xml_adapter.report_builders.basic_data_report_builder import BasicDataReportBuilder
from data_adapter.xml_adapter.report_builders.global_report_builder import GlobalReportBuilder

from pathlib import Path

from data_adapter.xml_adapter.serializers.serializer_global_report import serialize_global_report
from data_adapter.xml_adapter.serializers.serializers_basic_report import serialize_basic_report


BASE_DIR = Path(__file__).resolve().parent.parent

def basic_report(request: HttpRequest) -> JsonResponse:
    parser_basic = BasicDataReportBuilder()
    inform1 = parser_basic.parse_file(str(BASE_DIR / "data" / "39007435.xml"))
    data = serialize_basic_report(inform1)

    parser_global = GlobalReportBuilder()
    inform2 = parser_global.parse_file(str(BASE_DIR / "data" / "39007435.xml"))
    data_global = serialize_global_report(inform2)

    res = {
        "basic_report": data,
        "global_report": data_global,
    }
    return JsonResponse(res)

