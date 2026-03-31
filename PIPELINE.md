# Pipeline de datos — data_adapter

## Visión general

```
Archivo XML
    ↓
XmlExtractor          ← navegación segura del árbol XML
    ↓
Report Builders       ← XML → dataclasses inmutables (dominio)
    ↓
Transformers          ← str/int crudos → Enums de dominio  (aplicados en los builders)
    ↓
Dataclass Models      ← estado tipado e inmutable
    ↓
Serializers           ← dataclasses → TypedDicts (JSON-safe)
    ↓
JsonResponse          ← dict serializable por Django
```

---

## Entrada

Un archivo `.xml` de Datacredito/Experian ubicado en `data/<document_id>.xml`.

Nodo raíz: `<Informes>` → `<Informe>` (uno o más).

---

## Capa 1 — XmlExtractor

**Archivo:** `xml_adapter/xml_extractors/xml_extractor.py`

Recibe el `ET.Element` raíz y expone métodos de lectura segura:

| Método | Comportamiento |
|---|---|
| `find_node(path, parent)` | Retorna `Optional[Element]`, nunca lanza |
| `require_node(path, parent)` | Lanza `XmlNodeNotFoundError` si ausente |
| `get_attr(node, attr)` | Retorna `Optional[str]` con `.strip()` |
| `get_attr_required(node, attr)` | Lanza `XmlNodeNotFoundError` si ausente |
| `get_int(node, attr)` | `int(float(raw))` → soporta `"1.0"` |
| `get_float(node, attr)` | Retorna `Optional[float]` |
| `get_bool(node, attr)` | Parsea `"true"/"1"/"false"/"0"`, lanza si el atributo falta |
| `get_date(node, attr)` | Parsea ISO `"YYYY-MM-DD"` → `Optional[date]` |

El extractor se instancia una sola vez en `FullReportBuilder.parse()` y se pasa a cada sub-builder.

---

## Capa 2 — Report Builders

Cada builder recibe `(ex: XmlExtractor, report_node: ET.Element)` y retorna dataclasses.

### FullReportBuilder (orquestador)

**Archivo:** `report_builders/full_report_builder.py`

Punto de entrada del sistema. Parsea el XML una sola vez y delega a cada sub-builder.

```
parse(xml: str|bytes)
    → ET.fromstring()
    → XmlExtractor(root)
    → require_node("Informes/Informe") → report_node
    → BasicDataReportBuilder.build_from_node()
    → GlobalReportBuilder.build_from_node()
    → BankAccountReportBuilder.parse_accounts()
    → CheckingAccountReportBuilder.parse_accounts()
    → CreditCardReportBuilder.parse_cards()
    → QueryBuilder.build()
    → GlobalDebtBuilder.build()
    → AggregatedInfoBuilder.build()
    → MicroCreditBuilder.build()
    → ScoreBuilder.build()
    → AlertBuilder.build()
    → FullReport(...)
```

---

### BasicDataReportBuilder

**Nodo XML:** `<Informe>`

```
<Informe fechaConsulta="..." horaConsulta="..." tipoIdentificacion="..." identificacion="...">
  <NaturalNacional primerNombre="..." segundoNombre="..." primerApellido="..." genero="..." ...>
    <Identificacion ... />
    <Edad ... />
  </NaturalNacional>
</Informe>
```

**Flujo:**
```
<Informe> attrs         → QueryMetadata
<NaturalNacional> attrs → BasicDataPerson
  <Identificacion>      → CustomerIdentification
  <Edad>                → Age
→ BasicReport(metadata, person)
```

**Transformers aplicados:** ninguno (todos los campos son strings o primitivos directos del XML).

---

### GlobalReportBuilder

**Nodo XML:** `<Informe>//CuentaCartera`

```
<CuentaCartera entidad="..." numero="..." ...>
  <Caracteristicas tipoCuenta="..." tipoObligacion="..." garantia="..." ... />
  <Valores>
    <Valor moneda="..." calificacion="..." frecuenciaPago="..." ... />
  </Valores>
  <Estados>
    <EstadoCuenta codigo="..." fecha="..." />
    <EstadoOrigen codigo="..." fecha="..." />
    <EstadoPago codigo="..." meses="..." fecha="..." />
  </Estados>
</CuentaCartera>
```

**Flujo:**
```
findall(".//CuentaCartera")
  _parse_characteristics() → PortfolioCharacteristics
    transform_account_type()       → AccountType
    transform_obligation_type()    → ObligationType
    transform_debtor_role()        → DebtorRole
    transform_guarantee()          → GuaranteeType
    transform_contract_type()      → ContractType
  _parse_value_portfolio() → PortfolioValues
    transform_currency()           → Currency
    transform_credit_rating()      → CreditRating
    transform_payment_frequency()  → PaymentFrequency
  _parse_states() → PortfolioStates
    transform_account_condition()  → AccountCondition
    transform_origin_state()       → OriginState
    transform_payment_status()     → PaymentStatus
  _parse_account_wallet() → PortfolioAccount
    transform_credit_rating()      → CreditRating
    transform_ownership_situation()→ OwnershipSituation
    transform_industry_sector()    → IndustrySector
→ GlobalReport(portfolio_accounts: tuple[PortfolioAccount, ...])
```

`PortfolioAccount.is_open` evalúa `states.account_statement_code in OPEN_ACCOUNT_CONDITIONS` (`ON_TIME`, `OVERDUE_DEBT`, `WRITTEN_OFF`, `DOUBTFUL_COLLECTION`).

---

### BankAccountReportBuilder

**Nodo XML:** `<Informe>//CuentaAhorro`

```
<CuentaAhorro entidad="..." numero="..." sector="..." ...>
  <Caracteristicas clase="..." />
  <Valores>
    <Valor moneda="..." calificacion="..." fecha="..." />
  </Valores>
  <Estado codigo="..." fecha="..." />
</CuentaAhorro>
```

**Flujo:**
```
findall(".//CuentaAhorro")
  _parse_account() → BankAccount
    transform_credit_rating()         → CreditRating        (campo plano)
    transform_ownership_situation()   → OwnershipSituation  (campo plano)
    transform_industry_sector()       → IndustrySector       (campo plano)
  _parse_value() → Optional[BankAccountValue]
    transform_currency()              → Currency
    transform_credit_rating()         → CreditRating
  _parse_state() → Optional[BankAccountState]
    transform_savings_account_status()→ SavingsAccountStatus
→ tuple[BankAccount, ...]
```

`BankAccount.is_open` evalúa `state.code in {ACTIVE, SEIZED, SEIZED_ACTIVE}`.

---

### CheckingAccountReportBuilder

**Nodo XML:** `<Informe>//CuentaCorriente`

Estructura idéntica a `CuentaAhorro` más nodo `<Sobregiro>`. Reutiliza `BankAccountValue` y `BankAccountState`.

```
findall(".//CuentaCorriente")
  _parse_account() → CheckingAccount
    transform_ownership_situation()   → OwnershipSituation
    transform_industry_sector()       → IndustrySector
  _parse_value() → Optional[BankAccountValue]   (misma lógica que BankAccount)
  _parse_state() → Optional[BankAccountState]   (misma lógica que BankAccount)
  _parse_overdraft() → Optional[CheckingAccountOverdraft]
→ tuple[CheckingAccount, ...]
```

---

### CreditCardReportBuilder

**Nodo XML:** `<Informe>//TarjetaCredito`

```
<TarjetaCredito entidad="..." numero="..." sector="..." ...>
  <Caracteristicas franquicia="..." clase="..." garantia="..." ... />
  <Valores>
    <Valor moneda="..." calificacion="..." ... />
  </Valores>
  <Estados>
    <EstadoPlastico codigo="..." fecha="..." />
    <EstadoCuenta codigo="..." fecha="..." />
    <EstadoOrigen codigo="..." fecha="..." />
    <EstadoPago codigo="..." meses="..." fecha="..." />
  </Estados>
</TarjetaCredito>
```

**Flujo:**
```
findall(".//TarjetaCredito")
  _parse_card() → CreditCard
    transform_payment_method()        → PaymentMethod
    transform_credit_rating()         → CreditRating
    transform_ownership_situation()   → OwnershipSituation
    transform_industry_sector()       → IndustrySector
  _parse_characteristics() → CreditCardCharacteristics
    transform_franchise()             → CreditCardFranchise
    transform_credit_card_class()     → CreditCardClass
    transform_guarantee()             → GuaranteeType
  _parse_values() → Optional[CreditCardValues]
    transform_currency()              → Currency
    transform_credit_rating()         → CreditRating
  _parse_states() → CreditCardStates
    transform_plastic_status()        → PlasticStatus
    transform_account_condition()     → AccountCondition
    transform_origin_state()          → OriginState
    transform_payment_status()        → PaymentStatus
→ tuple[CreditCard, ...]
```

`CreditCard.is_open` evalúa `states.account_state_code in {ON_TIME, OVERDUE_DEBT, WRITTEN_OFF, DOUBTFUL_COLLECTION}`.

---

### QueryBuilder

**Nodo XML:** `<Informe>//Consulta`

```
findall(".//Consulta")
  _parse_record() → QueryRecord
    transform_account_type()     → AccountType
    transform_query_reason()     → QueryReason
    transform_industry_sector()  → IndustrySector
→ tuple[QueryRecord, ...]
```

---

### GlobalDebtBuilder

**Nodo XML:** `<Informe>//EndeudamientoGlobal`

```
<EndeudamientoGlobal calificacion="..." tipoCredito="..." moneda="..." ...>
  <Entidad nombre="..." nit="..." sector="..." />
  <Garantia tipo="..." valor="..." fecha="..." />
</EndeudamientoGlobal>
```

**Flujo:**
```
findall(".//EndeudamientoGlobal")
  _parse_record() → GlobalDebtRecord
    transform_credit_rating()              → CreditRating
    transform_global_debt_credit_type()    → GlobalDebtCreditType
    transform_currency()                   → Currency
    GlobalDebtEntity:
      transform_industry_sector()          → IndustrySector
  _parse_guarantee() → Optional[GlobalDebtGuarantee]
    transform_guarantee()                  → GuaranteeType
→ tuple[GlobalDebtRecord, ...]
```

---

### AggregatedInfoBuilder

**Nodo XML:** `<Informe>/InfoAgregada`

Parsea el nodo más complejo del XML, que concentra el perfil financiero agregado.

```
<InfoAgregada>
  <Resumen>
    <Principales />
    <Totales />
    <ComposicionPortafolio />
  </Resumen>
  <EvolucionDeuda>
    <Trimestre />     (0..n)
  </EvolucionDeuda>
  <ResumenEndeudamiento />
  <HistoricoSaldos />
</InfoAgregada>
```

**Flujo:**
```
find_node("InfoAgregada")
  _parse_summary() → AggregatedSummary
    _parse_principals()          → AggregatedPrincipals
    _parse_balances()            → AggregatedBalances
    _parse_composition()         → tuple[PortfolioCompositionItem, ...]
  parse_debt_evolution_quarters()→ tuple[DebtEvolutionQuarter, ...]
  parse_debt_evolution_analysis()→ DebtEvolutionAnalysis
  _parse_quarterly_debt()        → Optional[QuarterlyDebtSummary]
  _parse_historic_balances()     → tuple[BalanceHistoryByType, ...]
→ Optional[AggregatedInfo]
```

---

### MicroCreditBuilder

**Nodo XML:** `<Informe>/InfoAgregadaMicrocredito`

Misma estructura lógica que `AggregatedInfoBuilder`. Reutiliza `parse_debt_evolution_quarters` y `parse_debt_evolution_analysis` del módulo `aggregated_info_builder`.

```
find_node("InfoAgregadaMicrocredito")
  _parse_summary() → MicroCreditSummary
    _parse_general_profile()      → GeneralProfile
    _parse_balance_vectors()      → tuple[MonthlyBalancesAndArrears, ...]
    _parse_current_debt()         → CurrentDebtByUser
    _parse_trend_image()          → TrendSeries
  _parse_behavior_vectors()       → tuple[SectorBehaviorVector, ...]
  parse_debt_evolution_quarters() → tuple[DebtEvolutionQuarter, ...]
  parse_debt_evolution_analysis() → DebtEvolutionAnalysis
→ Optional[MicroCreditAggregatedInfo]
```

---

### ScoreBuilder / AlertBuilder

**Nodos XML:** `<Informe>/Score` y `<Informe>/Alerta` (hijos directos, búsqueda no recursiva).

```
ScoreBuilder:
  findall("Score") → tuple[ScoreRecord, ...]
    cada <Score> → ScoreRecord(value, model, date, reasons: tuple[ScoreReason, ...])

AlertBuilder:
  findall("Alerta") → tuple[AlertRecord, ...]
    cada <Alerta> → AlertRecord(code, description, sources: tuple[AlertSource, ...])
```

---

## Capa 3 — Transformers

Funciones puras `transform_x(value: Optional[str]) -> SomeEnum`. Nunca lanzan — retornan `UNKNOWN` como fallback.

| Módulo | Transformers |
|---|---|
| `basic_info_transformer` | `transform_gender`, `transform_id_type`, `transform_id_validity` |
| `global_report_transformer` | `transform_account_type`, `transform_account_condition`, `transform_debtor_role`, `transform_payment_frequency`, `transform_obligation_type`, `transform_contract_type` |
| `credit_card_transformer` | `transform_franchise`, `transform_credit_card_class`, `transform_plastic_status` |
| `global_debt_transformer` | `transform_global_debt_credit_type` |
| `shared_transformers` | `transform_credit_rating`, `transform_currency`, `transform_guarantee`, `transform_industry_sector`, `transform_origin_state`, `transform_ownership_situation`, `transform_payment_method`, `transform_payment_status`, `transform_savings_account_status`, `transform_query_reason`, `transform_payment_behavior_char`, `transform_current_debt_status` |

---

## Capa 4 — Serializers

Funciones puras `serialize_x(model) -> TypedDict`. Los campos enum emiten `.value` (string legible). Los campos `Optional[Enum]` se serializan como `x.value if x else None`.

Excepción deliberada: `payment_history` se transforma carácter a carácter con `transform_payment_behavior_char` directamente en el serializer (es una secuencia histórica, no un código único).

**Mapa serializer → TypedDict:**

| Serializer | Entrada | TypedDict de salida |
|---|---|---|
| `serialize_basic_report` | `BasicReport` | `SerializedReport` |
| `serialize_global_report` | `GlobalReport` | `SerializedGlobalReport` |
| `serialize_bank_account` | `BankAccount` | `SerializedBankAccount` |
| `serialize_checking_account` | `CheckingAccount` | `SerializedCheckingAccount` |
| `serialize_credit_card` | `CreditCard` | `SerializedCreditCard` |
| `serialize_query_record` | `QueryRecord` | `SerializedQueryRecord` |
| `serialize_global_debt_record` | `GlobalDebtRecord` | `SerializedGlobalDebt` |
| `serialize_aggregated_info` | `AggregatedInfo` | `SerializedAggregatedSummary` |
| `serialize_micro_credit_info` | `MicroCreditAggregatedInfo` | `SerializedMicroCreditAggregatedInfo` |
| `serialize_score_record` | `ScoreRecord` | `SerializedScoreRecord` |
| `serialize_alert_record` | `AlertRecord` | `SerializedAlertRecord` |
| `serialize_full_report` | `FullReport` | `SerializedFullReport` |

---

## Capa 5 — Salida (views.py)

Dos endpoints Django:

| Endpoint | Builder usado | Respuesta |
|---|---|---|
| `GET /api/data-adapter/basic-report/<document_id>/` | `BasicDataReportBuilder` + `GlobalReportBuilder` (separados) | `JsonResponse(SerializedReport + global_accounts)` |
| `GET /api/data-adapter/full-report/<document_id>/` | `FullReportBuilder` | `JsonResponse(SerializedFullReport)` |

---

## Estructura de `SerializedFullReport`

```json
{
  "basic_info":           { ... },   // QueryMetadata + BasicDataPerson
  "general_profile":      { ... },   // InfoAgregada: resumen, balances, composición
  "global_summary":       [ ... ],   // CuentaCartera is_open=True
  "open_bank_accounts":   [ ... ],   // CuentaAhorro is_open=True
  "closed_bank_accounts": [ ... ],   // CuentaAhorro is_open=False
  "checking_accounts":    [ ... ],   // CuentaCorriente (sin filtro)
  "active_obligations":   [ ... ],   // CuentaCartera is_open + TarjetaCredito is_open
  "payment_habits_open":  { ... },   // Hábitos abiertos agrupados por sector
  "payment_habits_closed":{ ... },   // Hábitos cerrados agrupados por sector
  "query_history":        [ ... ],   // Consulta
  "global_debt_records":  [ ... ],   // EndeudamientoGlobal
  "debt_evolution":       [ ... ],   // Trimestres InfoAgregada
  "micro_credit_info":    { ... },   // InfoAgregadaMicrocredito
  "score_records":        [ ... ],   // Score
  "alert_records":        [ ... ]    // Alerta
}
```
