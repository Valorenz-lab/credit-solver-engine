import json
from collections import Counter
from pathlib import Path

from django.core.management.base import BaseCommand

from data_adapter import debug_tracer
from data_adapter.xml_adapter.extraction_validator import validate_extraction
from data_adapter.xml_adapter.report_builders.full_report_report_builder import (
    FullReportBuilder,
)

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"
OUTPUT_DIR = DATA_DIR / "Evaluaiones"


def _run_validate(xml_path: Path, document_id: str) -> dict[str, object]:
    result: dict[str, object] = validate_extraction(str(xml_path))
    result["document_id"] = document_id
    return result


def _run_debug(xml_path: Path, document_id: str) -> dict[str, object]:
    trace = debug_tracer.start_trace()
    try:
        FullReportBuilder().parse_file(str(xml_path))
    finally:
        debug_tracer.end_trace()

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

    by_transformer: dict[str, int] = dict(Counter(e.transformer for e in trace.events))
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


class Command(BaseCommand):
    help = "Run validate + debug audit on all XMLs in data/ and save results to data/Evaluaiones/"

    def handle(self, *args: object, **options: object) -> None:
        OUTPUT_DIR.mkdir(exist_ok=True)

        xml_files = sorted(DATA_DIR.glob("*.xml"))
        if not xml_files:
            self.stderr.write("No XML files found in data/")
            return

        self.stdout.write(f"Found {len(xml_files)} XML files. Running audit...\n")

        total_pass = 0
        total_warn = 0
        total_error = 0
        total_debug_events = 0

        for xml_path in xml_files:
            document_id = xml_path.stem
            prefix = f"  [{document_id}]"

            try:
                validate_result = _run_validate(xml_path, document_id)
                debug_result = _run_debug(xml_path, document_id)
            except Exception as exc:
                self.stderr.write(f"{prefix} ERROR: {exc}")
                total_error += 1
                continue

            status = validate_result.get("status", "unknown")
            summary = validate_result.get("summary", {})
            failed = summary.get("failed", 0) if isinstance(summary, dict) else 0
            unknown_events = debug_result.get("summary", {})
            n_events = unknown_events.get("total_unknown_events", 0) if isinstance(unknown_events, dict) else 0

            # Save validate JSON always
            validate_out = OUTPUT_DIR / f"{document_id} - validate.json"
            validate_out.write_text(json.dumps(validate_result, ensure_ascii=False, indent=None))

            # Save debug JSON only when there are unknown events
            if n_events > 0:
                debug_out = OUTPUT_DIR / f"{document_id}-debug.json"
                debug_out.write_text(json.dumps(debug_result, ensure_ascii=False, indent=None))

            # Console summary line
            status_icon = "✅" if status == "ok" else "⚠️ "
            debug_icon = f"  🔴 {n_events} unknown events" if n_events > 0 else ""
            self.stdout.write(
                f"{prefix} {status_icon} {status}  checks_failed={failed}{debug_icon}"
            )

            if status == "ok":
                total_pass += 1
            else:
                total_warn += 1
            total_debug_events += n_events

        self.stdout.write("\n--- SUMMARY ---")
        self.stdout.write(f"  ok:       {total_pass}")
        self.stdout.write(f"  warnings: {total_warn}")
        self.stdout.write(f"  errors:   {total_error}")
        self.stdout.write(f"  total unknown enum events: {total_debug_events}")
        self.stdout.write(f"\nResults saved to: {OUTPUT_DIR}")
