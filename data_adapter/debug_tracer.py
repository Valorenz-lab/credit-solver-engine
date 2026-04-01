from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class UnknownEvent:
    transformer: str
    raw_value: Optional[str]
    xml_node: str
    xml_attribute: str
    record_type: str
    record_context: dict[str, str]


@dataclass
class DebugTrace:
    events: list[UnknownEvent] = field(default_factory=list)

    def record(self, event: UnknownEvent) -> None:
        self.events.append(event)


_active_trace: ContextVar[Optional[DebugTrace]] = ContextVar("debug_trace", default=None)


def start_trace() -> DebugTrace:
    trace = DebugTrace()
    _active_trace.set(trace)
    return trace


def end_trace() -> None:
    _active_trace.set(None)


def get_trace() -> Optional[DebugTrace]:
    return _active_trace.get()


def is_active() -> bool:
    return _active_trace.get() is not None


def record_unknown(
    transformer: str,
    raw_value: Optional[str],
    xml_node: str,
    xml_attribute: str,
    record_type: str,
    record_context: dict[str, str],
) -> None:
    trace = _active_trace.get()
    if trace is not None:
        trace.record(
            UnknownEvent(
                transformer=transformer,
                raw_value=raw_value,
                xml_node=xml_node,
                xml_attribute=xml_attribute,
                record_type=record_type,
                record_context=record_context,
            )
        )
