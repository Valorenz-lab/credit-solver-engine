# Debug de Transformaciones — Plan de Implementación

**Fecha:** 2026-03-31
**Contexto:** Pipeline XML → Builder → Transformer → Enum → Serializer
**Problema inmediato:** `AccountCondition.UNKNOWN` en `is_open`, pero el patrón es general.

---

## 1. Definición del problema

Los transformers del proyecto son funciones puras con firma:

```python
def transform_X(value: Optional[str]) -> SomeEnum:
    ...
    return SomeEnum.UNKNOWN  # fallback silencioso
```

Esto es correcto por diseño: un transformer nunca debe lanzar excepción. Pero introduce un problema de **observabilidad**: cuando retorna `UNKNOWN`, la información de qué valor llegó desde el XML se pierde permanentemente. El modelo extrae `AccountCondition.UNKNOWN` y no hay forma de saber si el XML enviaba `"99"`, `"AB"`, o un nodo ausente.

El problema tiene tres dimensiones:

| Dimensión | Descripción |
|---|---|
| **¿Qué valor raw llegó?** | El string exacto desde `get_attr()` antes de transformar |
| **¿Desde qué nodo XML?** | `CuentaCartera`, `EstadoCuenta.codigo`, etc. |
| **¿Para qué registro?** | La cuenta número X de la entidad Y |

Sin las tres se puede saber *que algo falló* pero no *dónde ni por qué*.

---

## 2. Restricciones de diseño

Cualquier solución debe respetar:

1. **Los transformers siguen siendo funciones puras** — no reciben ni retornan contexto de debug.
2. **Los dataclasses siguen siendo `frozen=True`** — no se añaden campos de debug al modelo.
3. **El `FullReport` no se contamina** — el reporte de producción no cambia.
4. **Cero overhead en producción** — si el flag está apagado, no hay costo.
5. **Seguro en concurrencia** — Django puede atender múltiples requests simultáneos.

---

## 3. Arquitectura: DebugTracer

### 3.1 Componente central

Un módulo `data_adapter/debug_tracer.py` con un **ContextVar** de Python (seguro para concurrencia y async):

```python
# data_adapter/debug_tracer.py
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class UnknownEvent:
    transformer: str        # "transform_account_condition"
    raw_value: Optional[str]  # "99" — el valor exacto del XML
    xml_node: str           # "EstadoCuenta"
    xml_attribute: str      # "codigo"
    record_type: str        # "PortfolioAccount"
    record_context: dict[str, str]  # {"lender": "Banco X", "account": "0012345"}

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
        trace.record(UnknownEvent(
            transformer=transformer,
            raw_value=raw_value,
            xml_node=xml_node,
            xml_attribute=xml_attribute,
            record_type=record_type,
            record_context=record_context,
        ))
```

### 3.2 Por qué ContextVar y no threading.local

`ContextVar` (Python 3.7+) es el mecanismo correcto para Django porque:
- Es seguro en multi-thread (cada request tiene su propio contexto).
- Es compatible con async si en el futuro se migra a ASGI.
- Se resetea automáticamente al inicio de cada request si se gestiona correctamente.

---

## 4. Puntos de integración

### 4.1 Django settings

```python
# settings.py
EXTRACTION_DEBUG: bool = False  # activar solo en desarrollo/staging
```

El flag se lee una sola vez al inicio del request. No hay evaluación condicional dentro de los transformers.

### 4.2 Transformers — mínima invasión

El transformer solo añade **una línea** en el retorno `UNKNOWN`:

```python
# Antes:
def transform_account_condition(value: Optional[str]) -> AccountCondition:
    ...
    return mapping.get(value.strip(), AccountCondition.UNKNOWN)

# Después:
from data_adapter.debug_tracer import record_unknown

def transform_account_condition(
    value: Optional[str],
    *,
    xml_node: str = "EstadoCuenta",
    xml_attribute: str = "codigo",
    record_type: str = "",
    record_context: dict[str, str] | None = None,
) -> AccountCondition:
    ...
    result = mapping.get(value.strip(), AccountCondition.UNKNOWN)
    if result is AccountCondition.UNKNOWN:
        record_unknown("transform_account_condition", value, xml_node, xml_attribute,
                       record_type, record_context or {})
    return result
```

> **Nota:** Los parámetros extra son keyword-only con defaults → la firma pública no cambia para los llamadores existentes.

### 4.3 Builders — push de contexto

El builder envuelve el parseo de cada cuenta con el contexto del registro:

```python
# global_report_report_builder.py
def _parse_account_wallet(self, ex: XmlExtractor, node: ET.Element) -> PortfolioAccount:
    ctx = {
        "lender": node.get("entidad", "?"),
        "account_number": node.get("numero", "?"),
    }
    return PortfolioAccount(
        ...
        states=self._parse_states(ex, node, record_context=ctx),
    )

def _parse_states(self, ex, parent, record_context=None):
    ec = ex.find_node("EstadoCuenta", parent=states_node)
    return PortfolioStates(
        account_statement_code=transform_account_condition(
            ex.get_attr(ec, "codigo"),
            record_type="PortfolioAccount",
            record_context=record_context or {},
        ),
        ...
    )
```

El contexto fluye desde el builder → `_parse_states` → transformer → `DebugTracer`. **No toca el dataclass.**

### 4.4 Vista debug

```python
# views.py
from django.conf import settings
from data_adapter import debug_tracer

def extraction_debug_report(request: HttpRequest, document_id: str) -> JsonResponse:
    if not getattr(settings, "EXTRACTION_DEBUG", False):
        return JsonResponse({"error": "Debug mode is disabled"}, status=403)

    xml_path = DATA_DIR / f"{document_id}.xml"
    if not xml_path.exists():
        return JsonResponse({"error": "Not found"}, status=404)

    trace = debug_tracer.start_trace()
    try:
        report = FullReportBuilder().parse_file(str(xml_path))
    finally:
        debug_tracer.end_trace()

    return JsonResponse(_serialize_trace(trace, report))
```

La vista es independiente de `full_report` — no devuelve el reporte completo, devuelve **solo el trace de debug**.

---

## 5. Formato de salida del debug report

```json
{
  "document_id": "12345678",
  "unknown_events": [
    {
      "transformer": "transform_account_condition",
      "raw_value": "60",
      "xml_node": "EstadoCuenta",
      "xml_attribute": "codigo",
      "record_type": "PortfolioAccount",
      "record_context": {
        "lender": "BANCOLOMBIA",
        "account_number": "000123456789"
      }
    }
  ],
  "summary": {
    "total_unknown_events": 6,
    "by_transformer": {
      "transform_account_condition": 4,
      "transform_industry_sector": 2
    },
    "by_raw_value": {
      "60": 3,
      "null": 2,
      "ZZ": 1
    },
    "affected_records": 5
  }
}
```

`"null"` en `by_raw_value` significa que el atributo XML estaba ausente (nodo sin `codigo`).

---

## 6. Plan de implementación por fases

### Fase 1 — Infraestructura (sin tocar transformers)
1. Crear `data_adapter/debug_tracer.py` con `ContextVar`, `DebugTrace`, `UnknownEvent`.
2. Añadir `EXTRACTION_DEBUG = False` a `settings.py`.
3. Crear la vista `extraction_debug_report` (devuelve 403 si debug está apagado).
4. Registrar URL `debug/<document_id>/`.

### Fase 2 — Instrumentar el transformer prioritario
5. Añadir parámetros keyword-only a `transform_account_condition`.
6. Añadir `record_unknown(...)` en el retorno `UNKNOWN`.
7. Actualizar `_parse_states` en `GlobalReportBuilder` para pasar contexto.
8. Verificar que mypy sigue en 0 errores.

### Fase 3 — Expandir a otros transformers críticos
9. Instrumentar `transform_industry_sector`, `transform_ownership_situation`, etc.
10. Cada transformer nuevo: misma firma keyword-only, misma línea de registro.

### Fase 4 — Enriquecer el reporte de debug
11. Añadir al output el valor del campo en el modelo resultante (no solo el raw).
12. Añadir navegación inversa: "este UNKNOWN es el account_statement_code de esta cuenta".

---

## 7. Generalización — patrón aplicable a cualquier proyecto

Este patrón resuelve el problema de **observabilidad en pipelines de transformación de datos** donde:
- Las funciones de transformación son puras (sin efectos laterales).
- El fallo es silencioso por diseño (fallback en lugar de excepción).
- Se necesita correlacionar el fallo con el registro de origen.

El patrón se puede abstraer como:

```
ContextVar (scope de request)
  ← activado por la capa de vista/orquestación
  ← leído por los transformers (zero-cost si está apagado)
  → produce un DebugTrace estructurado
  → expuesto por una vista/endpoint separado
```

Es análogo al **distributed tracing** (OpenTelemetry, Jaeger) pero a escala de pipeline in-process. Las diferencias son: no hay red, el span es el registro individual (una cuenta), y el "error" es retornar UNKNOWN en lugar de lanzar excepción.

---

## 8. Lo que este sistema NO hace

- No reemplaza logs de aplicación (usar `logging` de Python para errores de sistema).
- No persiste los traces (son efímeros por request).
- No trackea valores correctos — solo los que caen en UNKNOWN.
- No modifica el comportamiento del pipeline de producción.
