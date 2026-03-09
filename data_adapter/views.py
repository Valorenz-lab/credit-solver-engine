from django.http import HttpRequest, JsonResponse
from data_adapter.xml_adapter.report_builders.basic_data_report_builder import BasicDataReportBuilder
from data_adapter.xml_adapter.serializers.serializers_basic_report import serialize_basic_report
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

def basic_report(request: HttpRequest) -> JsonResponse:
    parser = BasicDataReportBuilder()
    inform = parser.parse_file(str(BASE_DIR / "data" / "73102905.xml"))
    data = serialize_basic_report(inform)
    return JsonResponse(data)

