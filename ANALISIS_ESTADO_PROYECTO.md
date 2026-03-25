# Análisis de estado — Credit Solver Engine
> Actualizado: 2026-03-25 | Basado en análisis de 26 XMLs reales + XSD v1.6 + Manual Insumos XML v1.6.4 + revisión crítica de arquitectura y convenciones

---

## 1. Rutas activas

| Ruta | Devuelve |
|---|---|
| `GET /api/data-adapter/basic-report/<id>/` | `basic_report` (persona + metadata) + `global_report` (todas las CuentaCartera) |
| `GET /api/data-adapter/full-report/<id>/` | 13 secciones con toda la info disponible |

`basic-report` es **parcialmente redundante** con `full-report`. Todo lo que devuelve está contenido en él con más detalle.

`full-report` retorna:
`basic_info`, `general_profile`, `global_summary`, `open_bank_accounts`, `closed_bank_accounts`, `checking_accounts`, `active_obligations`, `payment_habits_open`, `payment_habits_closed`, `query_history`, `global_debt_records`, `debt_evolution`, **`micro_credit_info`** *(nuevo)*

---

## 2. Correcciones al análisis anterior (2026-03-24)

El análisis anterior (basado en 5 XMLs) identificó incorrectamente la ubicación de varios nodos.

### Correcciones de ubicación
| Nodo | Ubicación supuesta (análisis anterior) | Ubicación real (verificada en 26 XMLs) |
|---|---|---|
| `PerfilGeneral` | `InfoAgregada` | `InfoAgregadaMicrocredito/Resumen` |
| `VectorSaldosYMoras` | `InfoAgregada` | `InfoAgregadaMicrocredito/Resumen` |
| `EndeudamientoActual` | `InfoAgregada` | `InfoAgregadaMicrocredito/Resumen` |
| `AnalisisVectores` | `InfoAgregada` | `InfoAgregadaMicrocredito` |
| `ImagenTendenciaEndeudamiento` | No documentado | `InfoAgregadaMicrocredito/Resumen` |
| `ResumenEndeudamiento` | `InfoAgregada` ✓ | `InfoAgregada` ✓ (correcto) |

El análisis anterior sobre `Garantia` en `EndeudamientoGlobal`, `independiente` en `EndeudamientoGlobal`, y los campos sin enum (`comportamiento`, `razon` en Consulta, garantias) era correcto.

---

## 3. Estado actual del parsing — Nodos del XML

Basado en XSD v1.6 + Manual v1.6.4 + 26 XMLs de prueba.

### 3.1 Nodos de nivel raíz de `<Informe>` (según XSD)

| Nodo | Estado | Notas |
|---|---|---|
| `NaturalNacional` | ✅ Completo | BasicDataReportBuilder |
| `Score` | ⬜ No parseado | Presente en XSD (ScoreType), **no encontrado en 26 XMLs de prueba** |
| `CuentaAhorro` | ✅ Completo | BankAccountBuilder |
| `CuentaCorriente` | ✅ Completo | CheckingAccountBuilder (con Sobregiro) |
| `TarjetaCredito` | ✅ Completo | CreditCardBuilder |
| `CuentaCartera` | ✅ Completo | GlobalReportBuilder |
| `EndeudamientoGlobal` | ✅ Completo | Incluye `independiente` + `Garantia` *(nuevo)* |
| `Consulta` | ✅ Completo | FullReportBuilder |
| `Alerta` | ⬜ No parseado | Presente en XSD (AlertaType), **no encontrado en 26 XMLs de prueba** |
| `Comentario` | ⬜ No parseado | Presente en XSD, no visto en XMLs |
| `Reclamo` (raíz) | ⬜ No parseado | Presente en XSD, no visto en XMLs |
| `productosValores` | ⬜ No parseado | Presente en XSD, no visto en XMLs |
| `InfoAgregada` | ✅ Completo | Ver sección 3.2 |
| `InfoAgregadaMicrocredito` | ✅ Completo | Ver sección 3.3 *(nuevo)* |
| `Localizacion` | ⬜ No parseado | Presente en XSD, no visto en XMLs |

### 3.2 Sub-nodos de `<InfoAgregada>` (verificados en 26 XMLs)

| Nodo | Estado | Notas |
|---|---|---|
| `Resumen/Principales` | ✅ Completo | AggregatedPrincipals |
| `Resumen/Saldos` | ✅ Completo | AggregatedBalances (con sectores + histórico mensual) |
| `Resumen/Comportamiento` | ✅ Completo | MonthlyBehavior (string crudo) |
| `Totales/TipoCuenta` | ✅ Completo | AccountTypeTotals |
| `Totales/Total` | ✅ Completo | GrandTotal |
| `ComposicionPortafolio` | ✅ Completo | PortfolioCompositionItem |
| `Cheques` | ⬜ Vacío | Presente en todos los XMLs pero **siempre sin atributos ni hijos** — no hay qué parsear |
| `EvolucionDeuda` | ✅ Completo | DebtEvolutionQuarter + AnalisisPromedio |
| `HistoricoSaldos` | ✅ Completo | BalanceHistoryByType |
| `ResumenEndeudamiento` | ✅ **Nuevo** | QuarterlyDebtSummary (Trimestre → Sector → Cartera) |

### 3.3 Sub-nodos de `<InfoAgregadaMicrocredito>` (verificados en 26 XMLs)

| Nodo | Estado | Notas |
|---|---|---|
| `Resumen/PerfilGeneral` | ✅ **Nuevo** | Créditos por sector (vigentes, cerrados, reestructurados, refinanciados, consultas, desacuerdos, antigüedad) |
| `Resumen/VectorSaldosYMoras` | ✅ **Nuevo** | 12 meses × mora máxima por sector + saldos |
| `Resumen/EndeudamientoActual` | ✅ **Nuevo** | Sector → TipoCuenta → Usuario → Cuenta (deuda vigente estructurada) |
| `Resumen/ImagenTendenciaEndeudamiento` | ✅ **Nuevo** | Series de tendencia de endeudamiento (12 puntos mensuales) |
| `AnalisisVectores` | ✅ **Nuevo** | Historial mensual de comportamiento por cuenta y sector (CaracterFecha con saldoDeudaTotalMora) |
| `EvolucionDeuda` | ✅ **Nuevo** | Evolutión trimestral del microcrédito |

---

## 4. Nuevos enums y transformers (2026-03-25)

### 4.1 Enums creados

| Enum | Tabla | Archivo |
|---|---|---|
| `PaymentBehavior` | Tabla 5 | `enums/financial_info/payment_behavior.py` |
| `GuaranteeType` | Tabla 11 | `enums/financial_info/guarantee_type.py` |
| `QueryReason` | Tabla 23 | `enums/financial_info/query_reason.py` |

### 4.2 Transformers creados (en `shared_transformers.py`)

| Función | Descripción |
|---|---|
| `transform_guarantee(value)` | Código de garantía → GuaranteeType |
| `transform_query_reason(value)` | Código razón consulta → QueryReason |
| `transform_payment_behavior_char(char)` | Carácter individual de comportamiento → PaymentBehavior |

### 4.3 Transformers que FALTAN aplicar

Estos transformers existen pero **no están siendo aplicados** en los serializers todavía:

| Campo | Nodo | Transformer disponible | Prioridad |
|---|---|---|---|
| `razon` | `Consulta` | `transform_query_reason` | Media |
| `garantia` | `CuentaCartera/Caracteristicas` | `transform_guarantee` | Media |
| `garantia` | `TarjetaCredito/Caracteristicas` | `transform_guarantee` | Media |
| `comportamiento` (char-by-char) | `CuentaCartera`, `TarjetaCredito` | `transform_payment_behavior_char` | Alta (scoring) |

---

## 5. Campos sin enum ni transformer (pendientes)

| Campo | Nodo | Valores observados | Impacto |
|---|---|---|---|
| `payment_status_code` | `EstadoPago.codigo` en CuentaCartera/TarjetaCredito | "01", "05", "08", "20", "45" | Medio |
| `ejecucionContrato` | `CuentaCartera/Caracteristicas` | números cortos | Bajo |
| `formaPago` | `CuentaCartera`, `TarjetaCredito` | "0", "1" (ya existe `PaymentMethod` pero no se aplica aquí) | Bajo |
| `EndeudamientoGlobal.fuente` | `EndeudamientoGlobal` | "1", "2" — Tabla 46 no documentada en manual | Bajo |
| `EndeudamientoGlobal.calificacion` | `EndeudamientoGlobal` | "A", "B", "-" — Tabla 14 | Bajo |
| `account_class` (clase) | `CuentaAhorro/Caracteristicas` | "0", "2", "4" — Tabla 36 | Bajo |
| `EndeudamientoActual/Cuenta.current_state` | `EndeudamientoActual` | "Al día", "Esta en mora 120", "Cart. castigada" — texto libre | Alto (scoring) |

---

## 6. Tablas de códigos referenciadas en el XSD que NO están documentadas en el manual v1.6.4

El manual usa "Ver tabla N" pero **no incluye los valores** en el documento. Las tablas con valores conocidos provienen de `temporal.txt` y análisis de XMLs reales:

| Tabla | Campo | Valores conocidos | Fuente |
|---|---|---|---|
| Tabla 2 | `Identificacion.estado` | Ver `id_validity.py` ✅ | Implementado |
| Tabla 5 | `comportamiento` | N, 1-6, C, D, - | `temporal.txt` + `PaymentBehavior` ✅ |
| Tabla 11 | `garantia` | 0, 1, 2, A-O | `temporal.txt` + `GuaranteeType` ✅ |
| Tabla 23 | `Consulta.razon` | "00"-"08" | `temporal.txt` + `QueryReason` ✅ |
| Tabla 4 | `EstadoPago.codigo` | "01", "05", "08", "20", "45" | XMLs reales (sin enum) |
| Tabla 14 | `calificacion` global | "A"-"E", "-" | XMLs reales (sin enum) |
| Tabla 29 | `situacionTitular` | numérico | No documentado |
| Tabla 36 | `clase` CuentaAhorro | "0", "2", "4" | XMLs reales (sin enum) |
| Tabla 46 | `EndeudamientoGlobal.fuente` | "1", "2" | XMLs reales (sin enum) |
| Tabla 49 | `Garantia.tipo` en EndeudamientoGlobal | "0", "9" | XMLs reales (sin transformer) |

---

## 7. Cumplimiento de convenciones de código

> Revisión estricta contra las reglas definidas en CLAUDE.md. **Idioma del código: inglés** (excepción explícita: nombres de nodos XML del dominio Datacredito).

### 7.1 Violaciones confirmadas

#### A. Nombres de métodos en español (violación de nombrado)

`full_report_builder.py` contiene métodos privados que mezclan el prefijo inglés `_parse_` con nombres de dominio en español:

| Método actual | Debe ser |
|---|---|
| `_parse_perfil_general` | `_parse_general_profile` |
| `_parse_vector_saldos_moras` | `_parse_balance_delinquency_vector` |
| `_parse_endeudamiento_actual` | `_parse_current_debt` |
| `_parse_quarterly_debt_trimestre` | `_parse_quarterly_debt_quarter` (o fusionar) |
| `_parse_analisis_vectores` | `_parse_behavior_vectors` |

La excepción permitida es que el string que identifica el **nodo XML** en las llamadas a `find_node("PerfilGeneral", ...)` sea en español. El nombre del **método Python** debe ser en inglés.

#### B. Docstrings en español en archivos de enums

| Archivo | Problema |
|---|---|
| `guarantee_type.py` | Docstring `"Tabla 11 — Tipo de garantía en hábito de pago obligaciones vigentes."` — en español |
| `current_debt_state.py` | Docstring con texto explicativo en español |
| `payment_status.py` | Comentario `"Tabla 4 — Estado de pago acumulado"` — en español |
| `payment_behavior.py` | Docstring `"Tabla 5 — Comportamiento de pago."` — en español |
| `query_reason.py` | Docstring `"Tabla 23 — Razón de la consulta"` — en español |

El patrón correcto sería: `"""Table 11 — Guarantee type (garantia field in CuentaCartera/Caracteristicas)."""`. La referencia a la tabla y el nombre del campo XML puede quedar en español porque es el nodo real.

#### C. Enum con valor semánticamente duplicado

`QueryReason` tiene dos keys con el mismo valor string:
```python
SOLICITUD_PRODUCTO   = "Solicitud de producto"   # code "01"
SOLICITUD_PRODUCTO_B = "Solicitud de producto"   # code "04"
```
El sufijo `_B` es una señal de que el nombre no refleja el dominio. Si los códigos `01` y `04` representan conceptos distintos en Datacredito, los labels deberían diferenciarse. Si no se conoce la distinción, el enum key debe reflejar eso: `SOLICITUD_PRODUCTO_01`, `SOLICITUD_PRODUCTO_04`.

#### D. Helpers internos como funciones anidadas en métodos de clase

`full_report_builder.py` define funciones dentro de métodos privados:
- `_sector_count(tag)` dentro de `_parse_perfil_general`
- `_bool_str(val)` dentro de `_parse_current_debt_user`
- `_bool_attr(attr)` dentro de `_parse_vector_saldos_moras`

Esto viola la convención de métodos privados de clase: deben ser `_snake_case` como métodos del objeto, no funciones locales inline. Además oscurece la lógica y no son testeables de forma aislada.

#### E. Función privada exportada como API pública

`serializer_aggregated_info.py` expone `_serialize_debt_evolution_quarter` (prefijo `_` indica privado), pero `serializer_full_report.py` la importa directamente:

```python
from data_adapter.xml_adapter.serializers.serializer_aggregated_info import (
    _serialize_debt_evolution_quarter,  # private — violation
    ...
)
```

Una función necesaria por otro módulo debe ser pública (sin underscore).

#### F. Tipos `dict[str, Any]` en TypedDicts de alto nivel

`SerializedFullReport` en `types.py`:
```python
active_obligations: list[dict[str, Any]]     # debería ser lista tipada
payment_habits_open: dict[str, Any]          # debería ser TypedDict
payment_habits_closed: dict[str, Any]        # debería ser TypedDict
```

`list[dict[str, Any]]` anula la seguridad de tipos que da mypy. El campo `active_obligations` mezcla `SerializedPortfolioAccount` y `SerializedCreditCard` — debería ser `list[SerializedPortfolioAccount | SerializedCreditCard]` o un TypedDict de unión.

#### G. Lógica de dominio embebida en un serializer

`serializer_full_report.py` tiene:
```python
_OPEN_ACCOUNT_CODES = frozenset({"01", "13", "14", ...})  # 34 códigos
```

y funciones `_is_portfolio_account_open`, `_is_bank_account_open`, `_is_credit_card_open`. Esto es **lógica de dominio** (qué estados representan una cuenta vigente), no transformación de datos. Un serializer no debe contener reglas de negocio. Estos predicados deben vivir en los modelos o en un módulo de clasificación.

#### H. Sector code raw como clave del dict de hábitos de pago

`payment_habits_open` / `payment_habits_closed` usan el código raw del sector como clave (`"1"`, `"2"`, `"unknown"`), no el label del enum. Inconsistente con el resto de la API que siempre expone labels legibles.

### 7.2 Cumplimiento correcto (destacable)

- **UPPER_CASE en enum keys**: Todos los enums usan `UPPER_CASE` correctamente (`AL_DIA`, `SIN_GARANTIA`, `MORA_30`).
- **`@dataclass(frozen=True)`**: Aplicado en todos los modelos sin excepción.
- **`Optional[T]` y no `T | None`**: Consistente en todo el proyecto.
- **Imports absolutos**: Sin imports relativos en ningún archivo.
- **Transformers sin excepciones**: Todos retornan un valor `UNKNOWN` como fallback.
- **`XmlExtractor` usado consistentemente**: No hay acceso directo a `ElementTree` en builders.
- **Un enum por archivo**: Se cumple en todos los archivos de `enums/`.
- **TypedDicts en `types.py`**: Se cumple (aunque el archivo crece sin límite, ver sección 8).

---

## 8. Arquitectura — Observaciones críticas

### 8.1 Triple parseo del mismo XML

`FullReportBuilder.parse(xml_input)` parsea el mismo XML **3 veces**:

```
FullReportBuilder._parse_xml(xml_input)          → parseo #1 → extractor (usado para el resto)
BasicDataReportBuilder().parse(xml_input)         → parseo #2 (instancia su propio ET.fromstring)
GlobalReportBuilder().parse(xml_input)            → parseo #3 (instancia su propio ET.fromstring)
```

`BankAccountBuilder`, `CheckingAccountBuilder` y `CreditCardBuilder` ya reciben `ex` y `report_node` — no re-parsean. El problema está en los dos builders que tienen una API `parse(xml_input: str)` que no acepta un extractor pre-existente.

### 8.2 `FullReportBuilder` viola Single Responsibility Principle (830 líneas)

El archivo es simultáneamente:
1. **Orquestador** de sub-builders existentes (BankAccount, CreditCard, etc.)
2. **Parser inline** de `Consulta` → `QueryRecord`
3. **Parser inline** de `EndeudamientoGlobal` → `GlobalDebtRecord`
4. **Parser inline** de `InfoAgregada` → `AggregatedInfo` (~200 líneas)
5. **Parser inline** de `InfoAgregadaMicrocredito` → `MicroCreditAggregatedInfo` (~250 líneas)
6. **Parser inline** de `Score` → `ScoreRecord`
7. **Parser inline** de `Alerta` → `AlertRecord`

Cualquier nuevo nodo del XML que se agregue termina en este archivo. El patrón de crecimiento es insostenible.

### 8.3 `types.py` como archivo dios (617 líneas)

Todos los TypedDicts del sistema viven en un solo archivo sin separación por dominio. Cada nueva sección del XML agrega entre 2 y 8 clases nuevas. El archivo actualmente cubre:
- Basic info (5 clases)
- Portfolio accounts (5 clases)
- Bank accounts (3 clases)
- Checking accounts (2 clases)
- Credit cards (4 clases)
- Query records (1 clase)
- Global debt (3 clases)
- Aggregated info (12 clases)
- Micro credit (11 clases)
- Score/Alert (4 clases)
- Full report container (1 clase)

### 8.4 `payment_habits_open/closed` — sector raw como clave

Las funciones `_group_by_sector_open/closed` en `serializer_full_report.py` usan el código raw `"1"`, `"2"`, `"unknown"` como clave del dict, no el label del enum. Inconsistente con el resto de la API.

### 8.5 `closed_portfolio_accounts` sin sección propia

Las CuentaCartera cerradas solo aparecen dentro de `payment_habits_closed`, sin lista plana accesible. Para el motor de decisión, una lista plana de obligaciones cerradas es igual de relevante.

### 8.6 `comportamiento` expuesto como string crudo

El campo `payment_history` en CuentaCartera/TarjetaCredito es un string de ~47 chars. El transformer `transform_payment_behavior_char` existe pero no se aplica en todos los paths.

- **0 errores mypy** en 69 archivos fuente.

---

## 9. Plan de refactor — Separación de responsabilidades

> Objetivo: cada archivo tiene una única razón para cambiar. El árbol XML se parsea una sola vez.

### 9.1 Principio central: separar parser de builder

**Problema actual:** los builders son responsables tanto de navegar/parsear el XML como de construir los modelos. Para parsear necesitan el XML crudo → parsean múltiples veces.

**Principio propuesto:** el XML se parsea **una sola vez** en `FullReportBuilder`. El resultado del parseo (el `XmlExtractor` + el `report_node`) se **pasa hacia abajo** a todos los builders. Ningún builder toca `ET.fromstring`.

Esto requiere que `BasicDataReportBuilder` y `GlobalReportBuilder` expongan un método secundario:

```python
# Método nuevo a agregar (no reemplaza parse() para mantener compatibilidad)
def build(self, ex: XmlExtractor, report_node: ET.Element) -> BasicReport: ...
def build(self, ex: XmlExtractor, report_node: ET.Element) -> GlobalReport: ...
```

`BankAccountBuilder`, `CheckingAccountBuilder`, `CreditCardBuilder` ya tienen esta API — son el modelo correcto.

### 9.2 Extraer builders de `FullReportBuilder`

Crear los siguientes builders, todos con firma `build(ex, report_node) -> <Model>`:

| Builder nuevo | Nodo XML | Modelo resultante | Tamaño estimado |
|---|---|---|---|
| `query_builder.py` | `Consulta` | `tuple[QueryRecord, ...]` | ~40 líneas |
| `global_debt_builder.py` | `EndeudamientoGlobal` | `tuple[GlobalDebtRecord, ...]` | ~60 líneas |
| `aggregated_info_builder.py` | `InfoAgregada` | `Optional[AggregatedInfo]` | ~200 líneas |
| `micro_credit_builder.py` | `InfoAgregadaMicrocredito` | `Optional[MicroCreditAggregatedInfo]` | ~250 líneas |
| `score_alert_builder.py` | `Score`, `Alerta` | `tuple[ScoreRecord, ...]`, `tuple[AlertRecord, ...]` | ~60 líneas |

`FullReportBuilder` quedaría en ~60 líneas de pura orquestación.

### 9.3 Dividir `types.py` en módulo por dominio

```
xml_adapter/types/
  __init__.py           ← re-exporta todo (compatibilidad)
  types_basic.py        ← SerializedMetadata, SerializedPerson, SerializedReport
  types_portfolio.py    ← SerializedPortfolioAccount, SerializedPortfolioCharacteristics, ...
  types_bank_account.py ← SerializedBankAccount, SerializedBankAccountValue, ...
  types_checking_account.py
  types_credit_card.py  ← SerializedCreditCard, SerializedCreditCardValues, ...
  types_query.py        ← SerializedQueryRecord
  types_global_debt.py  ← SerializedGlobalDebt, SerializedGlobalDebtEntity, ...
  types_aggregated_info.py  ← 12 TypedDicts de InfoAgregada
  types_micro_credit.py ← 11 TypedDicts de MicroCreditAggregatedInfo
  types_score_alert.py  ← SerializedScoreRecord, SerializedAlertRecord, ...
  types_full_report.py  ← SerializedFullReport (el container raíz)
```

El `__init__.py` re-exporta todo para que los imports existentes no rompan. La migración puede hacerse gradualmente.

### 9.4 Mover lógica de dominio fuera del serializer

`_OPEN_ACCOUNT_CODES` y los predicados `_is_portfolio_account_open`, `_is_bank_account_open`, `_is_credit_card_open` deben moverse a:

```python
# data_adapter/xml_adapter/classifiers/account_classifier.py
def is_portfolio_account_open(account: PortfolioAccount) -> bool: ...
def is_bank_account_open(account: BankAccount) -> bool: ...
def is_credit_card_open(card: CreditCard) -> bool: ...
```

El serializer importa las funciones del clasificador. Así la regla "qué es una cuenta vigente" tiene un único lugar.

### 9.5 Hacer pública `_serialize_debt_evolution_quarter`

Renombrar a `serialize_debt_evolution_quarter` (sin underscore) en `serializer_aggregated_info.py`. Actualizar el import en `serializer_full_report.py`.

### 9.6 Prioridad de ejecución del refactor

| Fase | Cambio | Impacto | Riesgo |
|---|---|---|---|
| 1 | `BasicDataReportBuilder.build(ex, node)` + `GlobalReportBuilder.build(ex, node)` → eliminar triple parseo | Performance | Bajo (agrega método, no borra) |
| 2 | Extraer `aggregated_info_builder.py` y `micro_credit_builder.py` de `FullReportBuilder` | Mantenibilidad | Medio |
| 3 | Extraer `query_builder.py`, `global_debt_builder.py`, `score_alert_builder.py` | Mantenibilidad | Bajo |
| 4 | Dividir `types.py` en módulo | Navegabilidad | Bajo (solo imports) |
| 5 | Mover clasificadores al módulo `classifiers/` | Corrección arquitectural | Bajo |
| 6 | Renombrar métodos en español de `FullReportBuilder` | Consistencia | Bajo |

---

## 10. Análisis de posible sobreingeniería

### 10.1 Lo que NO es sobreingeniería (justificado)

- **`XmlExtractor`**: la capa de abstracción sobre ElementTree está justificada. Provee acceso None-safe uniforme, tipos coercionados (`get_int`, `get_float`), y centraliza el manejo de errores. Sin ella, cada builder haría su propia gestión de `AttributeError` y `None`.

- **`@dataclass(frozen=True)` en todos los modelos**: inmutabilidad como regla garantiza que ningún código posterior mutará datos intermedios. Correcta para un pipeline de transformación.

- **Un enum por archivo**: el proyecto tiene ~85 valores de enum en ~22 archivos. Puede parecer excesivo para el estado actual, pero es correcto dado que el motor de decisión futuro consumirá estos enums individualmente. La granularidad es la adecuada.

- **Separación en capas** (builder → model → serializer → TypedDict): el flujo es razonable y cada capa tiene una responsabilidad distinta.

### 10.2 Sobreingeniería detectada

#### A. `transformers/` — tres archivos separados para transformers de enums análogos

Existen `global_report_transformer.py`, `credit_card_transformer.py`, `global_debt_transformer.py`, `basic_info_transformer.py`, `shared_transformers.py`. El criterio de separación no es consistente: algunos son por tipo de cuenta (global_report, credit_card), otros por uso compartido (shared). `shared_transformers.py` ya tiene 224 líneas y sigue creciendo. No hay una regla clara de "qué va en shared vs. en el transformer propio".

**Sugerencia:** alinear los archivos de transformers con los dominios de enum: `transform_basic_info.py`, `transform_financial_account.py`, `transform_aggregated_info.py`. O simplemente un único `transformers.py` dado que son funciones puras pequeñas sin estado.

#### B. `full_report_models.py` como dataclass contenedor sin lógica

`FullReport` es un dataclass con 11 campos que no tiene ningún método ni lógica. Es básicamente un NamedTuple glorificado. Esto es aceptable, pero vale notar que su única función es agrupar los resultados de los builders para pasarlos al serializer. Si en algún momento el serializer se llama directamente desde el builder (pasando los resultados uno a uno), este modelo intermedio puede eliminarse.

#### C. Endpoint `basic-report` redundante

`GET /api/data-adapter/basic-report/<id>/` devuelve un subconjunto de lo que devuelve `full-report`. No tiene lógica adicional. Mantenerlo implica mantener un builder y serializer duplicados. A menos que se justifique por performance (parseo parcial más rápido), debería eliminarse o convertirse en un subconjunto del full-report.

#### D. `aggregated_info_models.py` con modelos de dos dominios distintos

`AggregatedInfo` (InfoAgregada) y `MicroCreditAggregatedInfo` (InfoAgregadaMicrocredito) son dos nodos XML completamente distintos que comparten archivo de modelos. Esto no es sobreingeniería sino lo contrario: fue una simplificación que ahora genera un archivo de 339 líneas con 30+ dataclasses mezcladas. Dividirlo en `aggregated_info_models.py` y `micro_credit_models.py` sería correcto.

#### E. Serializer `serializer_aggregated_info.py` de 425 líneas

El serializer de `InfoAgregada` y `InfoAgregadaMicrocredito` juntos produce 425 líneas. Misma causa que D: dos dominios en un archivo. El split en `serializer_aggregated_info.py` y `serializer_micro_credit.py` está justificado.

---

## 11. Resumen de prioridades restantes

| # | Qué | Estado | Relevancia motor |
|---|---|---|---|
| 1 | Aplicar `transform_payment_behavior_char` en serializer de CuentaCartera/TarjetaCredito — campo `payment_history_parsed` | ✅ Implementado | **Alta** (scoring) |
| 2 | Aplicar `transform_query_reason` en serializer de QueryRecord — campo `reason_label` | ✅ Implementado | Media |
| 3 | Aplicar `transform_guarantee` en serializer de CuentaCartera/TarjetaCredito — campo `guarantee_label` | ✅ Implementado | Media |
| 4 | Enum `PaymentStatus` + transformer `transform_payment_status` para `payment_status_code` (EstadoPago, Tabla 4) — campo `payment_status_label` | ✅ Implementado | Media |
| 5 | Modelos `ScoreRecord`/`AlertRecord`, parseo en builder, serializer, TypedDicts en `types.py` — campos `score_records`/`alert_records` en full-report | ✅ Implementado | Media |
| 6 | Enum `CurrentDebtState` + `transform_current_debt_state` para `current_state` en `EndeudamientoActual` — campo `current_state_label` | ✅ Implementado | **Alta** (scoring) |
| 7 | Refactor separación de responsabilidades (ver sección 9) | ⏳ Pendiente | Mantenibilidad / Performance |
| 8 | Manejo de errores en views (actualmente 500 en cualquier excepción) | ⏳ Pendiente | Producción |
| 9 | Correcciones de convenciones (ver sección 7.1) | ⏳ Pendiente | Consistencia |

### Estado de sesión (2026-03-25) — Pendiente de verificar

Los cambios 1-6 están **escritos en disco** pero **mypy aún no fue ejecutado**. Antes de continuar:

1. Ejecutar `mypy data_adapter/` desde el entorno virtual (`.venv/bin/activate`)
2. Corregir los errores que aparezcan (si los hay)
3. Verificar con un XML real que el endpoint `/api/data-adapter/full-report/<id>/` devuelve los nuevos campos

### Archivos modificados en prioridades 1-6

| Archivo | Cambios |
|---|---|
| `data_adapter/xml_adapter/types.py` | Nuevos campos en `SerializedPortfolioAccount`, `SerializedCreditCard`, `SerializedPortfolioCharacteristics`, `SerializedCreditCardCharacteristics`, `SerializedAccountStatus`, `SerializedQueryRecord`, `SerializedCurrentDebtAccount`; nuevos TypedDicts `SerializedScoreReason`, `SerializedScoreRecord`, `SerializedAlertSource`, `SerializedAlertRecord`; `SerializedFullReport` con `score_records` y `alert_records` |
| `data_adapter/xml_adapter/serializers/serializer_global_report.py` | `payment_history_parsed`, `guarantee_label`, `payment_status_label` |
| `data_adapter/xml_adapter/serializers/serializer_credit_card.py` | `payment_history_parsed`, `guarantee_label`; corregido `payment_status_label` (usaba `transform_payment_method` por error, ahora usa `transform_payment_status`) |
| `data_adapter/xml_adapter/serializers/serializer_query.py` | `reason_label` |
| `data_adapter/xml_adapter/serializers/serializer_aggregated_info.py` | `current_state_label` en `_serialize_current_debt_account` |
| `data_adapter/xml_adapter/serializers/serializer_score_alert.py` | **Nuevo** — `serialize_score_record`, `serialize_alert_record` |
| `data_adapter/xml_adapter/serializers/serializer_full_report.py` | Importa `serializer_score_alert`, añade `score_records` y `alert_records` al return dict |
