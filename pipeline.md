# Pipeline de datos — `full-report`
> Basado en análisis de código fuente de la rama `Feature/Build-report`.
> Cubre únicamente el endpoint `GET /api/data-adapter/full-report/<document_id>/`.

---

## Índice

1. [Visión general](#1-visión-general)
2. [Capa 0 — Entry point (views.py)](#2-capa-0--entry-point-viewspy)
3. [Capa 1 — XmlExtractor](#3-capa-1--xmlextractor)
4. [Capa 2 — Builders](#4-capa-2--builders)
   - 4.1 FullReportBuilder (orquestador)
   - 4.2 BasicDataReportBuilder
   - 4.3 GlobalReportBuilder
   - 4.4 BankAccountReportBuilder
   - 4.5 CheckingAccountReportBuilder
   - 4.6 CreditCardReportBuilder
   - 4.7 Parsers inline en FullReportBuilder
5. [Capa 3 — Modelos (dataclasses)](#5-capa-3--modelos-dataclasses)
6. [Capa 4 — Serializers](#6-capa-4--serializers)
7. [Capa 5 — TypedDicts (types.py)](#7-capa-5--typeddicts-typespy)
8. [Flujo de datos completo (diagrama)](#8-flujo-de-datos-completo-diagrama)
9. [Problemas y redundancias explícitas](#9-problemas-y-redundancias-explícitas)

---

## 1. Visión general

El endpoint recibe un `document_id`, carga el XML correspondiente del disco, lo procesa y devuelve JSON con 15 secciones estructuradas.

**Capas del pipeline:**

```
XML en disco
    ↓
views.py                  ← entrada HTTP, sin lógica
    ↓
FullReportBuilder         ← orquestador, parsea XML (3 veces, ver §9.1)
    ↓ delega a ↓
BasicDataReportBuilder    ← NaturalNacional
GlobalReportBuilder       ← CuentaCartera
BankAccountReportBuilder  ← CuentaAhorro
CheckingAccountReportBuilder ← CuentaCorriente
CreditCardReportBuilder   ← TarjetaCredito
(inline en FullReportBuilder):
  _parse_query_records    ← Consulta
  _parse_global_debt_records ← EndeudamientoGlobal
  _parse_aggregated_info  ← InfoAgregada
  _parse_micro_credit_info ← InfoAgregadaMicrocredito
  _parse_score_records    ← Score
  _parse_alert_records    ← Alerta
    ↓
FullReport (dataclass frozen, 11 campos)
    ↓
serialize_full_report()   ← orquestador de serialización
    ↓ delega a ↓
serialize_basic_report
serialize_aggregated_info / serialize_micro_credit_info
_serialize_account (portfolio)
serialize_bank_account
serialize_checking_account
serialize_credit_card
serialize_query_record
serialize_global_debt_record
serialize_debt_evolution_quarter
serialize_score_record
serialize_alert_record
    ↓
SerializedFullReport (TypedDict)
    ↓
JsonResponse
```

---

## 2. Capa 0 — Entry point (`views.py`)

**Archivo:** `data_adapter/views.py`

```python
def full_report(request: HttpRequest, document_id: str) -> JsonResponse:
    xml_path = DATA_DIR / f"{document_id}.xml"
    if not xml_path.exists():
        return JsonResponse({"error": f"No XML found for '{document_id}'"}, status=404)
    builder = FullReportBuilder()
    report = builder.parse_file(str(xml_path))
    data = serialize_full_report(report)
    return JsonResponse(data)
```

**Responsabilidades:** resolver el path del XML, crear el builder, llamar al serializer, devolver `JsonResponse`.

**Lo que NO hace:**
- No valida el formato del `document_id`
- No captura `XmlParseError`, `XmlNodeNotFoundError` ni ninguna otra excepción → cualquier error de parseo retorna un 500 no controlado
- No aplica ninguna lógica de negocio

---

## 3. Capa 1 — XmlExtractor

**Archivo:** `data_adapter/xml_adapter/xml_extractors/xml_extractor.py`

Capa de abstracción sobre `ElementTree`. Todos los builders del proyecto usan esta clase exclusivamente para navegar el XML; ninguno accede a `ET.Element` directamente.

### Métodos principales

| Método | Firma de retorno | Comportamiento ante ausencia |
|--------|-----------------|------------------------------|
| `find_node(path, parent)` | `Optional[ET.Element]` | Devuelve `None` |
| `require_node(path, parent)` | `ET.Element` | Lanza `XmlNodeNotFoundError` |
| `get_attr(node, attr)` | `Optional[str]` | Devuelve `None` |
| `get_attr_required(node, attr)` | `str` | Lanza `XmlInvalidValueError` |
| `get_bool(node, attr)` | `bool` | Devuelve `False` |
| `get_int(node, attr)` | `Optional[int]` | Devuelve `None` |
| `get_float(node, attr)` | `Optional[float]` | Devuelve `None` |
| `get_date(node, attr)` | `Optional[date]` | Devuelve `None` |

### Características

- Tolerante por defecto: los métodos `get_*` reciben `Optional[ET.Element]` y devuelven `None` sin lanzar si el nodo es `None`.
- Los métodos `require_node` y `get_attr_required` son los únicos que lanzan; se usan solo para campos obligatorios según el XSD.
- El logging de nodos no encontrados está comentado (impacto en debugging, ver §9.8).

### Posición en el pipeline

`XmlExtractor` es construido **una vez** en `FullReportBuilder._build_full_report()` a partir del `ET.Element` raíz, y luego pasado a `BankAccountReportBuilder`, `CheckingAccountReportBuilder` y `CreditCardReportBuilder`. Sin embargo, **no se pasa** a `BasicDataReportBuilder` ni a `GlobalReportBuilder`, que construyen su propio `ET.Element` internamente (ver §9.1).

---

## 4. Capa 2 — Builders

### 4.1 `FullReportBuilder` (orquestador)

**Archivo:** `data_adapter/xml_adapter/report_builders/full_report_report_builder.py`

**Responsabilidades:**
- Parsear el XML crudo a `ET.Element` (`_parse_xml`)
- Crear el `XmlExtractor`
- Delegar a sub-builders
- Parsear inline los nodos que no tienen builder propio
- Retornar `FullReport`

**API pública:**

```python
def parse(xml_input: str | bytes) -> FullReport
def parse_file(filepath: str) -> FullReport
```

**Flujo interno de `_build_full_report(ex, xml_input)`:**

```
xml_input (str | bytes)
│
├─ BasicDataReportBuilder().parse(xml_input)         → BasicReport
│     ↑ REPARSA el XML desde cero (ver §9.1)
│
├─ GlobalReportBuilder().parse(xml_input)            → GlobalReport
│     ↑ REPARSA el XML desde cero (ver §9.1)
│
├─ BankAccountReportBuilder().parse_accounts(ex, report_node)     → tuple[BankAccount]
├─ CheckingAccountReportBuilder().parse_accounts(ex, report_node) → tuple[CheckingAccount]
├─ CreditCardReportBuilder().parse_cards(ex, report_node)         → tuple[CreditCard]
│
├─ _parse_query_records(ex, report_node)             → tuple[QueryRecord]
├─ _parse_global_debt_records(ex, report_node)       → tuple[GlobalDebtRecord]
├─ _parse_aggregated_info(ex, report_node)           → Optional[AggregatedInfo]
├─ _parse_micro_credit_info(ex, report_node)         → Optional[MicroCreditAggregatedInfo]
├─ _parse_score_records(ex, report_node)             → tuple[ScoreRecord]
└─ _parse_alert_records(ex, report_node)             → tuple[AlertRecord]
                                                          ↓
                                                    FullReport (frozen)
```

**Nodo XML de referencia:**
```
Informes
  └─ Informe                ← report_node
       ├─ NaturalNacional   ← BasicDataReportBuilder
       ├─ CuentaCartera[]   ← GlobalReportBuilder
       ├─ CuentaAhorro[]    ← BankAccountReportBuilder
       ├─ CuentaCorriente[] ← CheckingAccountReportBuilder
       ├─ TarjetaCredito[]  ← CreditCardReportBuilder
       ├─ Consulta[]        ← _parse_query_records (inline)
       ├─ EndeudamientoGlobal[] ← _parse_global_debt_records (inline)
       ├─ InfoAgregada      ← _parse_aggregated_info (inline, ~250 líneas)
       ├─ InfoAgregadaMicrocredito ← _parse_micro_credit_info (inline, ~250 líneas)
       ├─ Score[]           ← _parse_score_records (inline)
       └─ Alerta[]          ← _parse_alert_records (inline)
```

**Tamaño:** ~834 líneas. El archivo es simultáneamente orquestador y parser directo de 6 nodos XML. Ver §9.2.

---

### 4.2 `BasicDataReportBuilder`

**Archivo:** `data_adapter/xml_adapter/report_builders/basic_data_report_builder.py`

**API pública:**
```python
def parse(xml_input: str | bytes) -> BasicReport
def parse_file(filepath: str) -> BasicReport
```

**Nodo XML cubierto:** `NaturalNacional` dentro de `Informe`

**Métodos privados:**

| Método | Nodo XML | Modelo resultante |
|--------|----------|-------------------|
| `_parse_metadata(ex, informe_node)` | atributos de `Informe` | `QueryMetadata` |
| `_parse_persona(ex, node)` | `NaturalNacional` | `BasicDataPerson` |
| `_parse_identification(ex, parent)` | `Identificacion` | `CustomerIdentification` |
| `_parse_edad(ex, parent)` | `Edad` | `Age` |

**Modelo resultante:**
```python
BasicReport(
    metadata: QueryMetadata,   # 6 atributos del nodo Informe
    person: BasicDataPerson    # NaturalNacional + Identificacion + Edad
)
```

**Problema:** Reparsa el XML (`ET.fromstring`) a pesar de que `FullReportBuilder` ya lo tiene parseado. Ver §9.1.

---

### 4.3 `GlobalReportBuilder`

**Archivo:** `data_adapter/xml_adapter/report_builders/global_report_report_builder.py`

**API pública:**
```python
def parse(xml_input: str | bytes) -> GlobalReport
def parse_file(filepath: str) -> GlobalReport
```

**Nodo XML cubierto:** `CuentaCartera[]` dentro de `Informe`

**Métodos privados:**

| Método | Nodo XML | Modelo resultante |
|--------|----------|-------------------|
| `_parse_accounts_portfolio(ex, report_node)` | `.//CuentaCartera` | `tuple[PortfolioAccount]` |
| `_parse_account_wallet(ex, node)` | `CuentaCartera` | `PortfolioAccount` |
| `_parse_characteristics(ex, node)` | `Caracteristicas` | `PortfolioCharacteristics` |
| `_parse_value_portfolio(ex, node)` | `Valores/Valor` | `PortfolioValues` |
| `_parse_states(ex, node)` | `Estados` (3 sub-nodos) | `AccountStatus` |

`AccountStatus` es un modelo compuesto de 3 sub-modelos:
- `EstadoCuenta` → `AccountStateInfo` (code, state)
- `EstadoOrigen` → `OriginStateInfo` (code, state)
- `EstadoPago` → `PaymentStateInfo` (code, state)

`FullReportBuilder` extrae solo `GlobalReport.portfolio_account` (el tuple) y lo pasa directamente a `FullReport.portfolio_accounts`. El objeto `GlobalReport` en sí no persiste.

**Problema:** Reparsa el XML. Ver §9.1.

---

### 4.4 `BankAccountReportBuilder`

**Archivo:** `data_adapter/xml_adapter/report_builders/bank_account_report_builder.py`

**API pública:**
```python
def parse_accounts(ex: XmlExtractor, report_node: ET.Element) -> tuple[BankAccount, ...]
```

**Nodo XML cubierto:** `.//CuentaAhorro` dentro de `report_node`

**Métodos privados:**

| Método | Nodo XML | Modelo resultante |
|--------|----------|-------------------|
| `_parse_account(ex, node)` | `CuentaAhorro` | `BankAccount` |
| `_parse_value(ex, node)` | `Valores/Valor` | `Optional[BankAccountValue]` |
| `_parse_state(ex, node)` | `Estado` | `Optional[BankAccountState]` |
| `_parse_blocked(ex, node)` | atributo `bloqueada` | `bool` |

`_parse_blocked` convierte `"true"`, `"1"`, `"s"`, `"si"` → `True`. Es distinto al `XmlExtractor.get_bool()` estándar que solo maneja `"true"/"false"/"1"/"0"`.

**Este builder ya recibe el `XmlExtractor` pre-construido** — no reparsa el XML. Es el patrón correcto.

---

### 4.5 `CheckingAccountReportBuilder`

**Archivo:** `data_adapter/xml_adapter/report_builders/checking_account_report_builder.py`

**API pública:**
```python
def parse_accounts(ex: XmlExtractor, report_node: ET.Element) -> tuple[CheckingAccount, ...]
```

**Nodo XML cubierto:** `.//CuentaCorriente`

**Diferencia respecto a BankAccountReportBuilder:** parsea adicionalmente el sub-nodo `Sobregiro` → `CheckingAccountOverdraft`.

```python
def _parse_overdraft(ex, node) -> Optional[CheckingAccountOverdraft]
    # atributos: cupo, saldo, estado
```

Recibe `XmlExtractor` pre-construido. Patrón correcto.

---

### 4.6 `CreditCardReportBuilder`

**Archivo:** `data_adapter/xml_adapter/report_builders/credit_card_report_builder.py`

**API pública:**
```python
def parse_cards(ex: XmlExtractor, report_node: ET.Element) -> tuple[CreditCard, ...]
```

**Nodo XML cubierto:** `.//TarjetaCredito`

**Métodos privados:**

| Método | Nodo XML | Modelo resultante |
|--------|----------|-------------------|
| `_parse_card(ex, node)` | `TarjetaCredito` | `CreditCard` |
| `_parse_characteristics(ex, node)` | `Caracteristicas` | `CreditCardCharacteristics` |
| `_parse_values(ex, node)` | `Valores/Valor` | `Optional[CreditCardValues]` |
| `_parse_states(ex, node)` | `Estados` (4 sub-nodos) | `CreditCardStates` |

`CreditCardStates` incluye 4 estados:
- `Estado` (plástico) → `PlasticStateInfo`
- `EstadoCuenta` → `AccountStateInfo`
- `EstadoOrigen` → `OriginStateInfo`
- `EstadoPago` → `PaymentStateInfo`

Recibe `XmlExtractor` pre-construido. Patrón correcto.

---

### 4.7 Parsers inline en `FullReportBuilder`

Los siguientes nodos XML son parseados directamente dentro de `FullReportBuilder`, sin builder propio:

#### `_parse_query_records` → `tuple[QueryRecord, ...]`

Nodo: `.//Consulta`

```python
QueryRecord(
    date, account_type, entity, office, city, reason,
    count, subscriber_nit, sector
)
```

#### `_parse_global_debt_records` → `tuple[GlobalDebtRecord, ...]`

Nodo: `.//EndeudamientoGlobal`

```python
GlobalDebtRecord(
    rating, source, outstanding_balance, credit_type, currency,
    credit_count, report_date, independent,
    entity: GlobalDebtEntity(name, nit, sector),
    guarantee: Optional[GlobalDebtGuarantee(guarantee_type, value, date)]
)
```

#### `_parse_aggregated_info` → `Optional[AggregatedInfo]`

Nodo: `InfoAgregada` (~250 líneas, 8 sub-métodos)

```
InfoAgregada
  ├─ Resumen
  │    ├─ Principales        → AggregatedPrincipals (10 campos)
  │    ├─ Saldos             → AggregatedBalances (9 campos + Sector[] + Mes[])
  │    └─ Comportamiento/Mes → tuple[MonthlyBehavior]
  ├─ Totales
  │    ├─ TipoCuenta[]       → tuple[AccountTypeTotals]
  │    └─ Total[]            → tuple[GrandTotal]
  ├─ ComposicionPortafolio
  │    └─ TipoCuenta[]       → tuple[PortfolioCompositionItem]
  ├─ EvolucionDeuda
  │    ├─ Trimestre[]        → tuple[DebtEvolutionQuarter] (13 campos)
  │    └─ AnalisisPromedio   → Optional[DebtEvolutionAnalysis] (11 campos)
  ├─ HistoricoSaldos
  │    └─ TipoCuenta[]/Trimestre[] → tuple[BalanceHistoryByType]
  └─ ResumenEndeudamiento
       └─ Trimestre[]/Sector[]/Cartera[] → tuple[QuarterlyDebtSummary]
```

#### `_parse_micro_credit_info` → `Optional[MicroCreditAggregatedInfo]`

Nodo: `InfoAgregadaMicrocredito` (~250 líneas, 9 sub-métodos)

```
InfoAgregadaMicrocredito
  ├─ Resumen
  │    ├─ PerfilGeneral      → Optional[GeneralProfile]
  │    │    ├─ CreditosVigentes/Cerrados/Reestructurados/Refinanciados
  │    │    ├─ ConsultaUlt6Meses / Desacuerdos → SectorCreditCount (×6)
  │    │    └─ AntiguedadDesde → SectorSeniority
  │    ├─ VectorSaldosYMoras → Optional[BalanceDelinquencyVector]
  │    │    └─ SaldosYMoras[] → tuple[MonthlyBalancesAndArrears] (11 campos)
  │    ├─ EndeudamientoActual → tuple[CurrentDebtBySector]
  │    │    └─ Sector/TipoCuenta/Usuario/Cuenta (4 niveles de anidamiento)
  │    └─ ImagenTendenciaEndeudamiento → tuple[TrendSeries]
  │         └─ Series[]/Valores/Valor[] → tuple[TrendDataPoint]
  ├─ AnalisisVectores        → tuple[SectorBehaviorVector]
  │    └─ Sector/Cuenta/CaracterFecha[] → AccountBehaviorVector
  └─ EvolucionDeuda          → tuple[DebtEvolutionQuarter] + Optional[DebtEvolutionAnalysis]
       (reutiliza los mismos métodos que _parse_aggregated_info)
```

#### `_parse_score_records` / `_parse_alert_records`

Nodos: `Score[]`, `Alerta[]`

```python
ScoreRecord(score_type, score_value, classification, population_pct, date, reasons: tuple[ScoreReason])
AlertRecord(placed_date, expiry_date, cancelled_date, code, text, source: Optional[AlertSource])
```

---

## 5. Capa 3 — Modelos (dataclasses)

**Archivos:** `data_adapter/xml_adapter/models/*.py`

Todos los modelos son `@dataclass(frozen=True)`. Representan la estructura del XML como objetos Python inmutables. No contienen lógica, solo datos.

### Inventario por archivo

| Archivo | Modelos principales |
|---------|---------------------|
| `full_report_models.py` | `FullReport` (11 campos, contenedor raíz) |
| `basic_data_models.py` | `BasicReport`, `QueryMetadata`, `BasicDataPerson`, `CustomerIdentification`, `Age` |
| `global_report_models.py` | `GlobalReport`, `PortfolioAccount`, `PortfolioCharacteristics`, `PortfolioValues`, `AccountStatus`, `AccountStateInfo`, `OriginStateInfo`, `PaymentStateInfo` |
| `bank_account_models.py` | `BankAccount`, `BankAccountValue`, `BankAccountState` |
| `checking_account_models.py` | `CheckingAccount`, `CheckingAccountOverdraft` |
| `credit_card_models.py` | `CreditCard`, `CreditCardCharacteristics`, `CreditCardValues`, `CreditCardStates`, `PlasticStateInfo`, `AccountStateInfo`, `OriginStateInfo`, `PaymentStateInfo` |
| `query_models.py` | `QueryRecord` (9 campos) |
| `global_debt_models.py` | `GlobalDebtRecord`, `GlobalDebtEntity`, `GlobalDebtGuarantee` |
| `score_alert_models.py` | `ScoreRecord`, `ScoreReason`, `AlertRecord`, `AlertSource` |
| `aggregated_info_models.py` | **47 dataclasses** para `AggregatedInfo` y `MicroCreditAggregatedInfo` |

### `FullReport` — modelo contenedor

```python
@dataclass(frozen=True)
class FullReport:
    basic_data: BasicReport
    portfolio_accounts: tuple[PortfolioAccount, ...]    # de GlobalReport
    bank_accounts: tuple[BankAccount, ...]
    checking_accounts: tuple[CheckingAccount, ...]
    credit_cards: tuple[CreditCard, ...]
    query_records: tuple[QueryRecord, ...]
    global_debt_records: tuple[GlobalDebtRecord, ...]
    aggregated_info: Optional[AggregatedInfo]
    micro_credit_info: Optional[MicroCreditAggregatedInfo]
    score_records: tuple[ScoreRecord, ...]
    alert_records: tuple[AlertRecord, ...]
```

`GlobalReport` (el modelo del GlobalReportBuilder) **no se almacena** en `FullReport`. El builder lo crea, extrae `portfolio_account`, y descarta el contenedor.

---

## 6. Capa 4 — Serializers

**Archivos:** `data_adapter/xml_adapter/serializers/*.py`

Transforman los modelos (dataclasses) en TypedDicts (JSON-safe). Durante la transformación se aplican los **transformers** que convierten códigos crudos del XML en etiquetas legibles.

### `serialize_full_report` — función orquestadora

**Archivo:** `data_adapter/xml_adapter/serializers/serializer_full_report.py`

**Firma:** `serialize_full_report(report: FullReport) -> SerializedFullReport`

**Estructura del JSON de salida (15 secciones):**

| Clave JSON | Origen en `FullReport` | Serializer llamado |
|------------|------------------------|-------------------|
| `basic_info` | `report.basic_data` | `serialize_basic_report()` |
| `general_profile` | `report.aggregated_info` | `serialize_aggregated_info()` |
| `global_summary` | `report.portfolio_accounts` filtradas abiertas | `_serialize_account()` |
| `open_bank_accounts` | `report.bank_accounts` filtradas abiertas | `serialize_bank_account()` |
| `closed_bank_accounts` | `report.bank_accounts` filtradas cerradas | `serialize_bank_account()` |
| `checking_accounts` | `report.checking_accounts` | `serialize_checking_account()` |
| `active_obligations` | `portfolio_accounts` abiertas + `credit_cards` abiertas | `_serialize_account()` / `serialize_credit_card()` |
| `payment_habits_open` | todas las cuentas abiertas | agrupadas por sector (código raw) |
| `payment_habits_closed` | todas las cuentas cerradas | agrupadas por sector (código raw) |
| `query_history` | `report.query_records` | `serialize_query_record()` |
| `global_debt_records` | `report.global_debt_records` | `serialize_global_debt_record()` |
| `debt_evolution` | `report.aggregated_info.debt_evolution` | `serialize_debt_evolution_quarter()` |
| `micro_credit_info` | `report.micro_credit_info` | `serialize_micro_credit_info()` |
| `score_records` | `report.score_records` | `serialize_score_record()` |
| `alert_records` | `report.alert_records` | `serialize_alert_record()` |

### Clasificación de cuentas abiertas/cerradas

El serializer contiene lógica de dominio para determinar si una cuenta está abierta o cerrada:

```python
_OPEN_ACCOUNT_CODES: frozenset[str] = frozenset({"01", "13", "14", "15", ...})  # 44 códigos

def _is_portfolio_account_open(account: PortfolioAccount) -> bool:
    code = account.account_status.account_statement_code
    return code in _OPEN_ACCOUNT_CODES

def _is_bank_account_open(account: BankAccount) -> bool:
    code = account.state.code if account.state else None
    return code in ("01", "06", "07")   # conjunto diferente al de portfolio

def _is_credit_card_open(card: CreditCard) -> bool:
    code = card.states.account_state_code
    return code in _OPEN_ACCOUNT_CODES
```

Ver §9.4 para el problema arquitectural de tener esta lógica en el serializer.

### Transformers aplicados durante serialización

| Transformer | Aplicado en | Campo resultante |
|------------|-------------|-----------------|
| `transform_current_debt_state()` | `_serialize_current_debt_account()` | `current_state_label` |
| `transform_payment_behavior_char()` | `_serialize_behavior_monthly_char()` | `behavior_label` |
| `transform_payment_behavior_char()` | `serialize_global_report` (portfolio) | `payment_history_parsed` |
| `transform_guarantee()` | `serialize_global_report`, `serialize_credit_card` | `guarantee_label` |
| `transform_payment_status()` | `serialize_global_report`, `serialize_credit_card` | `payment_status_label` |
| `transform_query_reason()` | `serialize_query_record` | `reason_label` |

Los transformers se aplican **durante la serialización**, no durante el parseo. Ver §9.6.

### `serialize_aggregated_info`

**Archivo:** `serializer_aggregated_info.py` — 425 líneas, 32+ funciones privadas

Serializa tanto `AggregatedInfo` como `MicroCreditAggregatedInfo`. Ambos dominios conviven en el mismo archivo porque comparten `serialize_debt_evolution_quarter`. Ver §9.9.

---

## 7. Capa 5 — TypedDicts (`types.py`)

**Archivo:** `data_adapter/xml_adapter/types.py` — 617 líneas, ~51 clases TypedDict

Todos los TypedDicts del sistema están en un único archivo. Cada TypedDict refleja la estructura JSON de su modelo correspondiente.

### Inventario por dominio

| Dominio | TypedDicts |
|---------|------------|
| Basic info | `SerializedMetadata`, `SerializedPerson`, `SerializedIdentification`, `SerializedAge`, `SerializedBasicReport` |
| Portfolio (CuentaCartera) | `SerializedPortfolioCharacteristics`, `SerializedPortfolioValues`, `SerializedAccountStatus`, `SerializedPortfolioAccount`, `SerializedAccountStateSummary` |
| Bank accounts | `SerializedBankAccountValue`, `SerializedBankAccountState`, `SerializedBankAccount` |
| Checking accounts | `SerializedCheckingAccountOverdraft`, `SerializedCheckingAccount` |
| Credit cards | `SerializedCreditCardCharacteristics`, `SerializedCreditCardValues`, `SerializedCreditCardStates`, `SerializedCreditCard` |
| Queries | `SerializedQueryRecord` |
| Global debt | `SerializedGlobalDebtEntity`, `SerializedGlobalDebtGuarantee`, `SerializedGlobalDebtRecord` |
| Aggregated info | `SerializedAggregatedPrincipals`, `SerializedAggregatedBalances`, `SerializedAggregatedSummary`, `SerializedAggregatedSummaryInner`, `SerializedMonthlyBalance`, `SerializedMonthlyBehavior`, `SerializedSectorBalance`, `SerializedAccountTypeTotals`, `SerializedGrandTotal`, `SerializedPortfolioStateCount`, `SerializedPortfolioCompositionItem`, `SerializedDebtEvolutionQuarter`, `SerializedDebtEvolutionAnalysis`, `SerializedBalanceHistoryQuarter`, `SerializedBalanceHistoryByType`, `SerializedQuarterlyDebtCartera`, `SerializedQuarterlyDebtSector`, `SerializedQuarterlyDebtSummary` |
| Micro credit | `SerializedSectorCreditCount`, `SerializedSectorSeniority`, `SerializedGeneralProfile`, `SerializedMonthlyBalancesAndArrears`, `SerializedBalanceDelinquencyVector`, `SerializedCurrentDebtAccount`, `SerializedCurrentDebtByUser`, `SerializedCurrentDebtByType`, `SerializedCurrentDebtBySector`, `SerializedBehaviorMonthlyChar`, `SerializedAccountBehaviorVector`, `SerializedSectorBehaviorVector`, `SerializedTrendDataPoint`, `SerializedTrendSeries`, `SerializedMicroCreditAggregatedInfo` |
| Score / Alert | `SerializedScoreReason`, `SerializedScoreRecord`, `SerializedAlertSource`, `SerializedAlertRecord` |
| Raíz | `SerializedFullReport` |

### `SerializedFullReport` — TypedDict raíz

```python
class SerializedFullReport(TypedDict):
    basic_info: SerializedBasicReport
    general_profile: Optional[SerializedAggregatedSummary]
    global_summary: list[SerializedPortfolioAccount]
    open_bank_accounts: list[SerializedBankAccount]
    closed_bank_accounts: list[SerializedBankAccount]
    checking_accounts: list[SerializedCheckingAccount]
    active_obligations: list[dict[str, Any]]         # ← tipo débil (ver §9.5)
    payment_habits_open: dict[str, Any]              # ← tipo débil (ver §9.5)
    payment_habits_closed: dict[str, Any]            # ← tipo débil (ver §9.5)
    query_history: list[SerializedQueryRecord]
    global_debt_records: list[SerializedGlobalDebtRecord]
    debt_evolution: list[SerializedDebtEvolutionQuarter]
    micro_credit_info: Optional[SerializedMicroCreditAggregatedInfo]
    score_records: list[SerializedScoreRecord]
    alert_records: list[SerializedAlertRecord]
```

---

## 8. Flujo de datos completo (diagrama)

```
┌──────────────────────────────────────────────────────────────────┐
│  HTTP GET /api/data-adapter/full-report/<document_id>/           │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                    views.full_report()
                     │ carga archivo XML del disco
                     │
          ┌──────────┴──────────────────────────────────────┐
          │  FullReportBuilder.parse_file(filepath)          │
          │                                                  │
          │  ET.fromstring(xml) ─────────────────────────►  ET.Element (parseo #1)
          │  XmlExtractor(root) ──────────────────────────► ex
          │                                                  │
          │  BasicDataReportBuilder().parse(xml_input) ───► ET.fromstring (parseo #2)
          │    └── BasicReport(metadata, person)             │
          │                                                  │
          │  GlobalReportBuilder().parse(xml_input) ──────► ET.fromstring (parseo #3)
          │    └── GlobalReport → portfolio_accounts tuple   │
          │                                                  │
          │  BankAccountReportBuilder(ex, report_node)       │
          │    └── tuple[BankAccount]          .//CuentaAhorro
          │                                                  │
          │  CheckingAccountReportBuilder(ex, report_node)   │
          │    └── tuple[CheckingAccount]      .//CuentaCorriente
          │                                                  │
          │  CreditCardReportBuilder(ex, report_node)        │
          │    └── tuple[CreditCard]           .//TarjetaCredito
          │                                                  │
          │  _parse_query_records(ex, report_node)           │
          │    └── tuple[QueryRecord]          .//Consulta   │
          │                                                  │
          │  _parse_global_debt_records(ex, report_node)     │
          │    └── tuple[GlobalDebtRecord]     .//EndeudamientoGlobal
          │                                                  │
          │  _parse_aggregated_info(ex, report_node)         │
          │    └── Optional[AggregatedInfo]    InfoAgregada  │
          │                                                  │
          │  _parse_micro_credit_info(ex, report_node)       │
          │    └── Optional[MicroCreditAggregatedInfo]       │
          │                               InfoAgregadaMicrocredito
          │                                                  │
          │  _parse_score_records(ex, report_node)           │
          │    └── tuple[ScoreRecord]          .//Score      │
          │                                                  │
          │  _parse_alert_records(ex, report_node)           │
          │    └── tuple[AlertRecord]          .//Alerta     │
          │                                                  │
          └──────────────────┬───────────────────────────────┘
                             │
                    FullReport (frozen dataclass, 11 campos)
                             │
          ┌──────────────────┴───────────────────────────────┐
          │  serialize_full_report(report)                    │
          │                                                   │
          │  serialize_basic_report(report.basic_data)        │
          │    └── SerializedBasicReport                      │
          │                                                   │
          │  serialize_aggregated_info(report.aggregated_info)│
          │    └── SerializedAggregatedSummary (32 funciones) │
          │        + transformers aplicados                   │
          │                                                   │
          │  [filtrar portfolio_accounts → abiertas/cerradas] │
          │  [filtrar bank_accounts → abiertas/cerradas]      │
          │  [filtrar credit_cards → abiertas/cerradas]       │
          │  [agrupar por sector_code → payment_habits]       │
          │                                                   │
          │  serialize_bank_account × N                       │
          │  serialize_checking_account × N                   │
          │  serialize_credit_card × N                        │
          │  serialize_query_record × N                       │
          │  serialize_global_debt_record × N                 │
          │  serialize_debt_evolution_quarter × N             │
          │  serialize_micro_credit_info(report.micro_credit) │
          │  serialize_score_record × N                       │
          │  serialize_alert_record × N                       │
          │                                                   │
          └──────────────────┬───────────────────────────────┘
                             │
                    SerializedFullReport (TypedDict, 15 claves)
                             │
                    JsonResponse(data)
```

---

## 9. Problemas y redundancias explícitas

### 9.1 Triple parseo del mismo XML (CRÍTICO)

`FullReportBuilder._build_full_report()` parsea el XML **tres veces**:

```python
# Parseo #1 — en FullReportBuilder
root = ET.fromstring(xml_input)
ex = XmlExtractor(root)

# Parseo #2 — BasicDataReportBuilder hace su propio ET.fromstring
basic_data = BasicDataReportBuilder().parse(xml_input)

# Parseo #3 — GlobalReportBuilder hace su propio ET.fromstring
global_report = GlobalReportBuilder().parse(xml_input)
```

`BankAccountReportBuilder`, `CheckingAccountReportBuilder` y `CreditCardReportBuilder` ya tienen la API correcta: reciben `ex` y `report_node`. El problema es que `BasicDataReportBuilder` y `GlobalReportBuilder` solo exponen `parse(xml_input: str)`.

**Solución planificada (sección 9.1 de ANALISIS_ESTADO_PROYECTO.md):** agregar un método `build(ex, report_node)` a ambos builders que acepte el extractor ya construido, sin reparsar.

---

### 9.2 `FullReportBuilder` viola Single Responsibility (~834 líneas)

El archivo es simultáneamente:
1. Orquestador de sub-builders (≤20 líneas de responsabilidad real)
2. Parser inline de `Consulta` (~40 líneas)
3. Parser inline de `EndeudamientoGlobal` (~50 líneas)
4. Parser inline de `InfoAgregada` (~250 líneas, 8 métodos)
5. Parser inline de `InfoAgregadaMicrocredito` (~250 líneas, 9 métodos)
6. Parser inline de `Score` (~20 líneas)
7. Parser inline de `Alerta` (~20 líneas)

Cualquier nuevo nodo XML termina acumulándose aquí. El plan (sección 9.2 de ANALISIS_ESTADO_PROYECTO.md) propone extraer builders individuales para cada nodo.

---

### 9.3 `aggregated_info_models.py` mezcla dos dominios (~340 líneas)

`AggregatedInfo` (mapeada de `InfoAgregada`) y `MicroCreditAggregatedInfo` (mapeada de `InfoAgregadaMicrocredito`) son nodos XML completamente distintos que comparten un único archivo de modelos. Resultado: 47 dataclasses en un archivo sin separación clara de dominio.

Mismo problema en `serializer_aggregated_info.py`: 32+ funciones de serialización de dos dominios distintos en 425 líneas.

---

### 9.4 Lógica de dominio en el serializer

`serializer_full_report.py` contiene reglas de negocio:

```python
_OPEN_ACCOUNT_CODES = frozenset({"01", "13", "14", ...})  # 44 códigos
def _is_portfolio_account_open(account) -> bool: ...
def _is_bank_account_open(account) -> bool: ...
def _is_credit_card_open(card) -> bool: ...
```

Un serializer no debería saber qué estados representan una cuenta vigente. Esta lógica pertenece a un módulo de clasificación o a los modelos.

Adicionalmente, los conjuntos de códigos no son consistentes entre tipos de cuenta:
- `portfolio` y `credit_card` usan `_OPEN_ACCOUNT_CODES` (44 códigos)
- `bank_account` usa hardcodeado `("01", "06", "07")`

---

### 9.5 Tipos débiles en `SerializedFullReport`

Tres campos de `SerializedFullReport` usan tipos sin parámetros que anulan la seguridad de mypy:

```python
active_obligations: list[dict[str, Any]]   # mezcla PortfolioAccount + CreditCard
payment_habits_open: dict[str, Any]        # clave: sector code raw
payment_habits_closed: dict[str, Any]      # clave: sector code raw
```

`active_obligations` debería ser `list[SerializedPortfolioAccount | SerializedCreditCard]`.
`payment_habits_*` debería ser un TypedDict que describa la estructura `{sector_code: list[...]}`.

---

### 9.6 Transformers aplicados en la capa de serialización

Los transformers (`transform_current_debt_state`, `transform_payment_behavior_char`, etc.) se aplican **durante la serialización**, no durante el parseo:

```python
# En serializer_aggregated_info.py
def _serialize_current_debt_account(a: CurrentDebtAccount):
    return {
        "current_state": a.current_state,
        "current_state_label": transform_current_debt_state(a.current_state).value,  # aquí
        ...
    }
```

Consecuencia: los modelos (dataclasses) contienen el código crudo del XML (`"Al día"`, `"N"`, `"1"`), y la etiqueta legible solo existe en el TypedDict. El modelo no puede usarse directamente por la capa de decisión sin re-aplicar los transformers.

---

### 9.7 Sector code raw como clave en `payment_habits`

`_group_by_sector_open/closed` agrupa las cuentas usando el código de sector raw (`"1"`, `"2"`, `"unknown"`) como clave del dict JSON:

```python
sector_key = account.characteristics.sector or "unknown"
```

Inconsistente con el resto de la API, que siempre expone etiquetas legibles. Debería usar el label del enum `Sector`.

---

### 9.8 Logging deshabilitado en `XmlExtractor`

Las líneas de warning en `find_node` están comentadas:
```python
# logger.warning(f"Node not found {path}. Parent: {parent_str}...")
```

Cuando un XML tiene un nodo inesperadamente ausente, el sistema retorna `None` silenciosamente. No hay forma de distinguir en los logs si `aggregated_info` es `None` porque el XML no tiene `InfoAgregada` o porque hay un bug de navegación.

---

### 9.9 `_serialize_debt_evolution_quarter` importado como privado

`serializer_full_report.py` importa una función con prefijo `_` desde `serializer_aggregated_info.py`:

```python
from data_adapter.xml_adapter.serializers.serializer_aggregated_info import (
    _serialize_debt_evolution_quarter,  # ← prefijo privado
    ...
)
```

Una función necesaria en otro módulo debe ser pública. El prefijo `_` indica que no es parte de la API pública del módulo, pero se está usando como si lo fuera.

**Nota:** Según el análisis de la sesión 2026-03-25, esta función fue renombrada a `serialize_debt_evolution_quarter` (sin underscore). Verificar que el import en `serializer_full_report.py` esté actualizado.

---

### 9.10 Inconsistencia en parsing de booleanos

`BankAccountReportBuilder._parse_blocked()` convierte `"true"`, `"1"`, `"s"`, `"si"` → `True`, ignorando `XmlExtractor.get_bool()` que ya maneja `"true"/"false"/"1"/"0"`. Hay lógica de conversión duplicada y parcialmente inconsistente.

---

*Pipeline documentado: 2026-03-27 | Rama: Feature/Build-report*
