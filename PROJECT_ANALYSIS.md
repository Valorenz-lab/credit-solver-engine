# Análisis del proyecto — data_adapter

**Fecha:** 2026-03-31
**Alcance:** `data_adapter/` completo, validado contra `CLAUDE.md`

---

## Calificación general

| Dimensión | Nota | Justificación |
|---|---|---|
| **Arquitectura** | 8 / 10 | Separación en capas clara y coherente. El flujo XML→Builder→Model→Serializer→TypedDict está bien diseñado y es consistente. Algunos acoplamientos puntuales (función privada importada entre módulos, doble parseo en view). |
| **Buenas prácticas** | 6.5 / 10 | Tipado mypy-strict cumplido en su mayoría, dataclasses inmutables, transformers puros. Se penaliza por bugs de serialización que pueden crashear en producción, nomenclatura inconsistente y ausencia de manejo de errores en views. |
| **Sobre-ingeniería** | 7.5 / 10 | En general la complejidad es justificada por el dominio (XML de Datacredito es genuinamente complejo). El único caso dudoso es el doble par `_code`/`_label` con valores idénticos en todos los serializers, que expande la API sin aportar información. |
| **Adherencia a CLAUDE.md** | 7 / 10 | Se respetan enums, dataclasses, transformers puros, imports absolutos y XmlExtractor. Fallan: un builder usa `get_bool` donde debería usar el patrón defensivo; cuatro campos en serializers emiten objetos enum en lugar de `.value`; nomenclatura inconsistente entre modelos. |

---

## Bugs críticos (pueden causar crash en producción)

### BUG-01 — `GlobalReportBuilder` usa `get_bool` en campo opcional
**Severidad: ALTA**
**Archivo:** `xml_adapter/report_builders/global_report_report_builder.py`

`_parse_account_wallet` llama `ex.get_bool(node, "bloqueada")`. El método `get_bool` llama internamente `get_attr_required`, que lanza `XmlNodeNotFoundError` si el atributo no existe en el XML. Todos los demás builders usan un patrón defensivo:
```python
raw = ex.get_attr(node, "bloqueada")
return raw is not None and raw.lower() in ("true", "1", "s", "si")
```

**Corrección:** Reemplazar la llamada a `get_bool` por el patrón defensivo, igual que en `BankAccountReportBuilder`, `CheckingAccountReportBuilder` y `CreditCardReportBuilder`.

---

### BUG-02 — Serializer emite objetos enum en lugar de strings
**Severidad: ALTA**
**Archivos:** `serializer_global_report.py` (líneas ~49, ~53, ~73, ~79)

Cuatro campos emiten el objeto enum directamente, no su `.value`:

| Campo | Tipo en TypedDict | Tipo que emite hoy |
|---|---|---|
| `obligation_type` | `Optional[ObligationType]` | `ObligationType` objeto |
| `debtor_quality` | `Optional[DebtorRole]` | `DebtorRole` objeto |
| `payment_frequency` | `Optional[PaymentFrequency]` | `PaymentFrequency` objeto |
| `account_statement_code` | `Optional[AccountCondition]` | `AccountCondition` objeto |

Como son `StrEnum`, `JsonResponse` los serializa correctamente hoy (Python 3.11 serializa `StrEnum` como string). Sin embargo, el patrón es inconsistente con el resto del sistema, viola la convención del proyecto y es frágil ante cambios de versión.

**Corrección:** Los primeros tres TypedDicts deberían cambiar su tipo a `Optional[str]` y los serializers deberían emitir `.value if x else None`. `account_statement_code` puede mantenerse como `Optional[AccountCondition]` si se quiere el enum en el TypedDict (es el único campo en todo el sistema que lo hace), o también pasarse a `Optional[str]`.

---

### BUG-03 — `views.py` sin manejo de excepciones
**Severidad: ALTA**
**Archivo:** `data_adapter/views.py`

Cualquier XML malformado, nodo requerido ausente o valor de tipo incorrecto llanza `XmlParseError`, `XmlNodeNotFoundError` o `XmlInvalidValueError`, que Django convierte en HTTP 500 sin cuerpo informativo.

**Corrección:**
```python
try:
    report = FullReportBuilder().parse_file(xml_path)
except XmlNodeNotFoundError as e:
    return JsonResponse({"error": str(e)}, status=422)
except XmlParseError as e:
    return JsonResponse({"error": str(e)}, status=400)
```

---

## Bugs menores (no crashean, pero son incorrectos)

### BUG-04 — `BasicDataPerson.first_name` mapea a `primerApellido`
**Severidad: MEDIA**
**Archivos:** `models/basic_data_models.py`, `report_builders/basic_data_report_builder.py`

El campo en Python se llama `first_name` pero extrae el atributo XML `primerApellido` (primer apellido). Es un error semántico que produce confusión al leer el modelo.

**Corrección:** Renombrar a `first_surname` o `primer_apellido`, y actualizar el builder, serializer y TypedDict correspondientes.

---

### BUG-05 — `DebtorRole.CO_HOLDER` tiene espacio trailing
**Severidad: MEDIA**
**Archivo:** `enums/financial_info/debtor_role.py`

```python
CO_HOLDER = "Cotitular "  # espacio al final
```

Si alguien compara este valor contra un string limpio (`"Cotitular"`), la comparación falla silenciosamente.

**Corrección:** Quitar el espacio: `CO_HOLDER = "Cotitular"`.

---

### BUG-06 — `_serialize_behavior_monthly_char` ignora valores multi-carácter
**Severidad: MEDIA**
**Archivo:** `serializers/serializer_aggregated_info.py`

La lógica solo transforma `behavior` si tiene exactamente 1 carácter:
```python
if c.behavior is not None and len(c.behavior) == 1:
    behavior_label = transform_payment_behavior_char(c.behavior).value
```
Valores como `"1-6"` (mora 30–180 días) resultan en `behavior_label = None` aunque haya un valor válido presente.

**Corrección:** Manejar el caso multi-carácter con un transformer o una representación apropiada, o al menos documentar la limitación con un comentario.

---

### BUG-07 — `transform_current_debt_status` usa matching de texto libre frágil
**Severidad: MEDIA**
**Archivo:** `transformers/shared_transformers.py`

El campo `current_state` de `CurrentDebtAccount` viene del XML como texto no normalizado. El transformer usa heurísticas como:
```python
if v.startswith("al día") and "mora" not in v: ...
```
Variaciones menores de ortografía (tildes, mayúsculas, espacios extra) producen `UNKNOWN` silenciosamente.

**Corrección:** Si el XML de Datacredito tiene un atributo de código numérico separado para este campo, usarlo. Si no, documentar los valores observados y añadir `.lower().strip()` antes de las comparaciones.

---

## Inconsistencias de nomenclatura

### INC-01 — `ownership_status` vs `ownership_situation`
**Archivos:** `global_report_models.py` vs `bank_account_models.py`, `checking_account_models.py`, `credit_card_models.py`

`PortfolioAccount` usa `ownership_status`, todos los demás modelos usan `ownership_situation`. Ambos mapean al mismo atributo XML (`situacionTitular`) y al mismo enum (`OwnershipSituation`).

**Corrección:** Unificar a `ownership_situation` en `PortfolioAccount`, su builder, serializer y TypedDict.

---

### INC-02 — `opening_date` vs `opened_date`
**Archivos:** `types_portfolio.py` vs `global_report_models.py`

El modelo tiene `opened_date`, el TypedDict tiene `opening_date`. El serializer usa `opening_date` al escribir, con lo que el campo del modelo nunca se referencia con su nombre real en el TypedDict.

**Corrección:** Unificar a `opened_date` en el TypedDict (o bien a `opening_date` en el modelo, eligiendo una convención).

---

### INC-03 — `transform_account_type` usa lookup por nombre, no por valor
**Archivo:** `transformers/global_report_transformer.py`

```python
return AccountType[value]  # lookup por nombre del enum (e.g., "CCB")
```
Todos los demás transformers usan diccionarios explícitos o `.upper()`. Este transformer no hace `.strip()` antes del lookup, lo que puede fallar con whitespace.

**Corrección:** Añadir `.strip()` antes del acceso y documentar que el XML debe enviar el código en mayúsculas exactas.

---

## Code smells y redundancias

### SMELL-01 — Campos `_code` y `_label` idénticos (todos los serializers)

Tras el refactor, todos los pares `campo` / `campo_label` emiten el mismo `.value` del enum. Ejemplos:
- `"rating": account.rating.value` y `"rating_label": account.rating.value`
- `"sector": ...value` y `"sector_label": ...value`

La API expone el doble de campos que información real. Esto es deuda de diseño heredada; se documenta aquí como deuda conocida, no como bug activo.

---

### SMELL-02 — `basic_report` view parsea el XML dos veces
**Archivo:** `views.py`

La vista `basic_report` instancia `BasicDataReportBuilder` y `GlobalReportBuilder` por separado, cada uno lee y parsea el archivo XML completo. `FullReportBuilder` existe precisamente para evitar esto.

**Corrección:** Usar `FullReportBuilder` en `basic_report` y extraer solo los campos necesarios, o refactorizar la vista para que ambas builder compartan el `XmlExtractor`.

---

### SMELL-03 — Importación de función privada entre módulos
**Archivo:** `serializers/serializer_full_report.py`

```python
from data_adapter.xml_adapter.serializers.serializer_global_report import _serialize_account
```

`_serialize_account` tiene prefijo `_` (privada). Importarla desde otro módulo rompe el encapsulamiento y acopla los dos serializers.

**Corrección:** Hacerla pública (`serialize_portfolio_account`) o moverla a un módulo compartido.

---

### SMELL-04 — `global_summary` y `active_obligations` computan el mismo filtro dos veces
**Archivo:** `serializers/serializer_full_report.py`

Ambas secciones iteran `portfolio_accounts` filtrando `is_open=True` y serializando con `_serialize_account`. El mismo subconjunto se computa y serializa dos veces.

**Corrección:** Computar la lista de cuentas abiertas una sola vez y reutilizarla.

---

### SMELL-05 — `CardholderRole` enum sin uso
**Archivo:** `enums/financial_info/cardholder_role.py`

El enum `CardholderRole` (PRINCIPAL, AUTHORIZED_USER_CARD, CO_HOLDER) no está importado en ningún builder, transformer o serializer del sistema. Es código muerto.

**Corrección:** Eliminar o documentar explícitamente para qué nodo XML futuro está destinado.

---

### SMELL-06 — `CheckingAccount` no tiene property `is_open`
**Archivo:** `models/checking_account_models.py`

`BankAccount` y `CreditCard` tienen `is_open`. `CheckingAccount` reutiliza `BankAccountState` (con `SavingsAccountStatus`) pero no expone la propiedad. Si `is_open` no aplica para cuentas corrientes, debería documentarse; si aplica, debería implementarse.

---

### SMELL-07 — `xml_adapter/__init__.py` solo exporta `BasicDataReportBuilder`
**Archivo:** `xml_adapter/__init__.py`

Los builders `GlobalReportBuilder`, `FullReportBuilder`, etc., no están en la API pública del paquete. No es un error funcional, pero quien consuma el paquete desde fuera no tiene un punto de entrada claro.

---

### SMELL-08 — `SerializedQueryRecord` en `types_global_debt.py`
**Archivo:** `types/types_global_debt.py`

`SerializedQueryRecord` está en el mismo archivo que los tipos de deuda global, aunque semánticamente no tiene relación. Hace el nombre del archivo engañoso.

**Corrección:** Mover a `types_query.py`.

---

## Validación contra CLAUDE.md

| Convención | Estado | Detalle |
|---|---|---|
| Mypy strict, 0 errores | ✅ Cumple | Los enums en TypedDicts (BUG-02) son aceptados por mypy porque `StrEnum` es asignable a `str`. |
| `Optional[T]` en lugar de `T \| None` | ✅ Cumple | Consistente en todo el código. |
| `@dataclass(frozen=True)` | ✅ Cumple | Todos los modelos son inmutables. |
| TypedDicts en `xml_adapter/types/` | ✅ Cumple | Estructura correcta. |
| Transformers: función pura, retorna `UNKNOWN` | ⚠️ Parcial | `transform_current_debt_status` usa text matching frágil (BUG-07). El resto cumple. |
| Transformers nunca lanzan excepción | ✅ Cumple | Todos tienen fallback a `UNKNOWN`. |
| `find_node()` + `get_attr()` para opcionales | ⚠️ Parcial | `GlobalReportBuilder` usa `get_bool` en campo opcional (BUG-01). |
| `require_node()` solo para obligatorios | ✅ Cumple | Uso correcto en builders. |
| No usar `ElementTree` directamente en builders | ✅ Cumple | Todo vía `XmlExtractor`. |
| Nombres en snake_case / PascalCase / UPPER_CASE | ⚠️ Parcial | `first_name` → `primerApellido` (BUG-04), `ownership_status` inconsistente (INC-01), espacio trailing en enum (BUG-05). |
| Imports absolutos, sin relativos, sin no usados | ✅ Cumple | Consistente. |
| Jerarquía de excepciones definida | ✅ Definida | Pero no usada en views.py (BUG-03). |

---

## Resumen priorizado

| Prioridad | Item | Tipo |
|---|---|---|
| 🔴 Alta | BUG-01 — `get_bool` en campo opcional | Crash en XML sin `bloqueada` |
| 🔴 Alta | BUG-03 — Sin manejo de errores en views | HTTP 500 en cualquier XML malo |
| 🟠 Media | BUG-02 — Enums en lugar de `.value` en serializers | Inconsistencia + fragilidad |
| 🟠 Media | BUG-04 — `first_name` es `primerApellido` | Error semántico en modelo |
| 🟠 Media | BUG-05 — Espacio trailing en `CO_HOLDER` | Comparaciones silenciosamente rotas |
| 🟠 Media | BUG-06 — `behavior` multi-carácter ignorado | Información perdida silenciosamente |
| 🟡 Baja | INC-01 — `ownership_status` vs `ownership_situation` | Nomenclatura inconsistente |
| 🟡 Baja | INC-02 — `opening_date` vs `opened_date` | Mismatch modelo/TypedDict |
| 🟡 Baja | SMELL-02 — Doble parseo en `basic_report` | Ineficiencia evitable |
| 🟡 Baja | SMELL-03 — Import de función privada | Acoplamiento indebido |
| 🟡 Baja | SMELL-05 — `CardholderRole` sin uso | Código muerto |
| ⚪ Info | SMELL-01 — Campos `_code`/`_label` idénticos | Deuda de diseño pre-existente conocida |
