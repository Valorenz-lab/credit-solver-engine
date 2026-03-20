# CLAUDE.md — Credit Solver Engine

## Propósito del proyecto

Motor de decisión crediticia (en fases muy tempranas). Por ahora el objetivo principal es **extraer y estructurar información de XMLs de Datacredito (Experian)**. No hay base de datos activa ni autenticación. Las vistas son básicas. La arquitectura puede mutar.

---

## Arquitectura actual

```
data_adapter/           ← App principal, única con lógica implementada
  enums/                ← Códigos de dominio (StrEnum con etiquetas en español)
    basic_info/         ← gender, id_validity, types_id
    financial_info/     ← account_status, account_type, debtor_quality, obligation_type, payment_frequency, card_holder
  transformers/         ← Código raw (str/int) → Enum
  xml_adapter/
    xml_extractors/     ← Navegación segura del XML (XmlExtractor)
    models/             ← Dataclasses inmutables que representan el XML
    report_builders/    ← Orquestación del parseo XML → modelos
    serializers/        ← Modelos → TypedDict (JSON-safe)
  views.py              ← Endpoints HTTP (mínimos)
  urls.py

engines/                ← Stub vacío (motor de decisión futuro)
tasks/                  ← Stub vacío
api/                    ← Stub vacío
```

**Flujo de datos:**
`XML file → ReportBuilder → Dataclass models → Serializers + Transformers → TypedDict → JsonResponse`

---

## Convenciones de desarrollo (mantener siempre)

### Tipado
- **Mypy en modo strict** (`mypy.ini`). Todo el código nuevo debe pasar mypy sin errores.
- Usar `Optional[T]` en lugar de `T | None` (consistencia con el código existente).
- Los TypedDict van en `xml_adapter/types.py`.
- Las funciones deben tener type hints completos (parámetros y retorno).

### Dataclasses
- Siempre `@dataclass(frozen=True)` — inmutabilidad es una regla del proyecto.
- Composición de dataclasses: los modelos complejos contienen sub-dataclasses.
- Van en `xml_adapter/models/`.

### Enums
- Heredar de `StrEnum`.
- Valores en `UPPER_CASE`.
- Los enums representan dominio de negocio con etiquetas legibles (pueden ser en español).
- Cada enum en su propio archivo bajo `enums/basic_info/` o `enums/financial_info/`.

### Transformers
- Función pura: `transform_X(value: Optional[str]) -> SomeEnum`.
- Nunca lanzar excepción en un transformer — devolver valor `UNKNOWN`/`UNDEFINED`/`NO_INFORMATION` como fallback.
- Van en `data_adapter/transformers/`.

### Serializers
- Función pura: `serialize_X(model: SomeDataclass) -> SomeTypedDict`.
- Aplican los transformers durante la serialización.
- Van en `xml_adapter/serializers/`.

### XmlExtractor
- Usar `find_node()` + `get_attr()` para campos opcionales (retorna None).
- Usar `require_node()` + `get_attr_required()` solo para campos obligatorios del XML.
- No usar `ElementTree` directamente en builders — siempre via `XmlExtractor`.

### Nombrado
| Elemento | Convención | Ejemplo |
|---|---|---|
| Clases | PascalCase | `PortfolioAccount`, `XmlExtractor` |
| Funciones / métodos | snake_case | `transform_gender()`, `parse_file()` |
| Métodos privados | `_snake_case` | `_parse_metadata()` |
| Constantes / Enum values | UPPER_CASE | `ON_TIME`, `MALE` |
| Archivos | snake_case | `global_report_builder.py` |

### Imports
- Absolutos desde la raíz del proyecto: `from data_adapter.enums.basic_info.gender import Gender`.
- Sin imports relativos.
- Sin imports no utilizados.

### Excepciones
- Usar la jerarquía de `xml_adapter/exceptions.py`:
  - `XmlParseError` — XML malformado
  - `XmlNodeNotFoundError` — nodo requerido ausente
  - `XmlInvalidValueError` — falla de conversión de tipo

---

## Estado actual de implementación

### Funcional
- Extracción de reporte básico (persona, metadata, identificación)
- Extracción de reporte global (cuentas de cartera con estructuras anidadas)
- Todos los enums (~70 valores en 6 grupos)
- Todos los transformers (gender, ID type, ID validity, características de cuenta, estado de cuenta)
- Serializers (TypedDict-based)
- Endpoint: `GET /api/data-adapter/basic-report/`

### Pendiente / Stubs vacíos
- `engines/` — motor de decisión (sin implementar)
- `tasks/` — tareas (sin implementar)
- `api/` — capa API genérica (sin implementar)
- Tests (archivos placeholder, sin cobertura real)
- Manejo de errores en views (actualmente los errores rompen con 500)

### Bugs conocidos
- `serializer_global_report.py` línea ~49: `"currency": v.credit_rating` debe ser `v.currency_code`
- `global_report_builder.py`: tiene imports no utilizados
- `views.py`: ruta del XML hardcodeada

---

## Datos de prueba

- Los XMLs de prueba van en `data/` (ignorado por `.gitignore`)
- El formato es XML de Datacredito/Experian
- Nodo raíz relevante: `Informes` → `CuentaCartera` (array de cuentas)

---

## Stack

- **Python 3.11** / **Django 6.0.2**
- **mypy** (strict) para type checking
- Sin base de datos activa (SQLite por defecto, sin modelos)
- Sin autenticación por ahora
