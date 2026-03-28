# Análisis de factibilidad — Mover transformers a los Builders

Fecha de análisis: 2026-03-28
Referencia: `temporary_pipeline.md`

---

## 1. Estado de los prerrequisitos del documento original

El `temporary_pipeline.md` listaba un prerrequisito obligatorio antes de empezar:

| Prerrequisito | Estado |
|---|---|
| Resolver colisión `AccountStatus` (enum vs dataclass) | ✅ **Resuelto** — enum → `AccountCondition`, dataclass → `PortfolioStates` |
| Renombrar `DebtorQualityPortfolio` → `DebtorRole` | ✅ **Resuelto** |
| Renombrar `Sector` → `IndustrySector` | ✅ **Resuelto** |
| Renombrar `PlasticState` → `PlasticStatus`, `AccountStateSavings` → `SavingsAccountStatus`, etc. | ✅ **Resuelto** |
| Split de `types.py` monolítico | ✅ **Resuelto** (9 archivos en `types/`) |

**El proyecto ya cumple todos los prerrequisitos nombrados.** El documento original puede ejecutarse sin deuda técnica pendiente de naming.

---

## 2. Inventario de campos a migrar (estado actual)

Todos estos campos son `Optional[str]` con un transformer existente. Son los candidatos al cambio.

### PortfolioCharacteristics
| Campo actual | Tipo destino | Transformer |
|---|---|---|
| `account_type` | `Optional[AccountType]` | `transform_account_type` |
| `obligation_type` | `Optional[ObligationType]` | `transform_obligation_type` |
| `contract_type` | `Optional[ContractType]` | `transform_contract_type` ⚠️ *ver nota* |
| `debtor_quality` | `Optional[DebtorRole]` | `transform_debtor_role` |
| `guarantee` | `Optional[GuaranteeType]` | `transform_guarantee` |

### PortfolioValues
| Campo actual | Tipo destino | Transformer |
|---|---|---|
| `currency_code` | `Optional[Currency]` | `transform_currency` |
| `credit_rating` | `Optional[CreditRating]` | `transform_credit_rating` |
| `payment_frequency` | `Optional[PaymentFrequency]` | `transform_payment_frequency` |

### PortfolioStates
| Campo actual | Tipo destino | Transformer |
|---|---|---|
| `account_statement_code` | `Optional[AccountCondition]` | `transform_account_condition` ⚠️ *ver nota crítica* |
| `origin_state_code` | `Optional[OriginState]` | `transform_origin_state` |
| `payment_status_code` | `Optional[PaymentStatus]` | `transform_payment_status` |

### PortfolioAccount (campos planos)
| Campo actual | Tipo destino | Transformer |
|---|---|---|
| `credit_rating` | `Optional[CreditRating]` | `transform_credit_rating` |
| `ownership_status` | `Optional[OwnershipSituation]` | `transform_ownership_situation` |
| `industry_sector` | `Optional[IndustrySector]` | `transform_industry_sector` |
| `payment_history` | mantener `Optional[str]` | — (caso especial, ver §4) |

### BankAccountValue
| Campo actual | Tipo destino | Transformer |
|---|---|---|
| `currency_code` | `Optional[Currency]` | `transform_currency` |
| `rating` | `Optional[CreditRating]` | `transform_credit_rating` |

### BankAccountState
| Campo actual | Tipo destino | Transformer |
|---|---|---|
| `code` | `Optional[SavingsAccountStatus]` | `transform_savings_account_status` ⚠️ *ver nota crítica* |

### BankAccount
| Campo actual | Tipo destino | Transformer |
|---|---|---|
| `rating` | `Optional[CreditRating]` | `transform_credit_rating` |
| `ownership_situation` | `Optional[OwnershipSituation]` | `transform_ownership_situation` |
| `sector` | `Optional[IndustrySector]` | `transform_industry_sector` |

### CreditCardCharacteristics
| Campo actual | Tipo destino | Transformer |
|---|---|---|
| `franchise` | `Optional[CreditCardFranchise]` | `transform_franchise` |
| `card_class` | `Optional[CreditCardClass]` | `transform_credit_card_class` |
| `guarantee` | `Optional[GuaranteeType]` | `transform_guarantee` |

### CreditCardValues
| Campo actual | Tipo destino | Transformer |
|---|---|---|
| `currency_code` | `Optional[Currency]` | `transform_currency` |
| `rating` | `Optional[CreditRating]` | `transform_credit_rating` |

### CreditCardStates
| Campo actual | Tipo destino | Transformer |
|---|---|---|
| `plastic_state_code` | `Optional[PlasticStatus]` | `transform_plastic_status` |
| `account_state_code` | `Optional[AccountCondition]` | `transform_account_condition` ⚠️ *ver nota crítica* |
| `origin_state_code` | `Optional[OriginState]` | `transform_origin_state` |
| `payment_status_code` | `Optional[PaymentStatus]` | `transform_payment_status` |

### CreditCard (campos planos)
| Campo actual | Tipo destino | Transformer |
|---|---|---|
| `payment_method` | `Optional[PaymentMethod]` | `transform_payment_method` |
| `credit_rating` | `Optional[CreditRating]` | `transform_credit_rating` |
| `ownership_situation` | `Optional[OwnershipSituation]` | `transform_ownership_situation` |
| `sector` | `Optional[IndustrySector]` | `transform_industry_sector` |

### CheckingAccount
| Campo actual | Tipo destino | Transformer |
|---|---|---|
| `ownership_situation` | `Optional[OwnershipSituation]` | `transform_ownership_situation` |
| `sector` | `Optional[IndustrySector]` | `transform_industry_sector` |

### QueryRecord
| Campo actual | Tipo destino | Transformer |
|---|---|---|
| `account_type` | `Optional[AccountType]` | `transform_account_type` |
| `reason` | `Optional[QueryReason]` | `transform_query_reason` |
| `sector` | `Optional[IndustrySector]` | `transform_industry_sector` |

### GlobalDebtRecord + sub-modelos
| Campo actual | Tipo destino | Transformer |
|---|---|---|
| `rating` | `Optional[CreditRating]` | `transform_credit_rating` |
| `credit_type` | `Optional[GlobalDebtCreditType]` | `transform_global_debt_credit_type` |
| `currency` | `Optional[Currency]` | `transform_currency` |
| `entity.sector` | `Optional[IndustrySector]` | `transform_industry_sector` |
| `guarantee.guarantee_type` | `Optional[GuaranteeType]` | `transform_guarantee` |

**Total de campos a migrar: ~40 campos en 13 modelos.**

---

## 3. Riesgos identificados

### 🔴 Riesgo crítico — OPEN_ACCOUNT_CODES: transformer incompleto

Este es el hallazgo más importante del análisis. El documento original no lo detectó.

`OPEN_ACCOUNT_CODES` en `global_report_models.py` tiene **35 códigos string crudos** (ej: `"01"`, `"13"`, `"14"`, ..., `"47"`).

El `transform_account_condition` solo mapea **12 valores numéricos** (0–11). La conversión hace `int("13")` → `13`, que no está en el mapping → devuelve `AccountCondition.UNKNOWN`.

**Consecuencia si se migra `account_statement_code` a `Optional[AccountCondition]` antes de completar el transformer:** `is_open` usaría un `frozenset[AccountCondition]` donde la mayoría de los códigos activos colapsarían en `UNKNOWN`, rompiendo silenciosamente la lógica de negocio.

**Impacto:** afecta `PortfolioAccount.is_open` y `CreditCard.is_open`. Antes de migrar `account_statement_code`, hay que:
1. Auditar todos los códigos de `OPEN_ACCOUNT_CODES` contra Tabla 4 del XSD
2. Completar el transformer para mapear todos esos códigos a sus `AccountCondition` correctos
3. Solo entonces convertir `OPEN_ACCOUNT_CODES: frozenset[str]` a `OPEN_ACCOUNT_STATUSES: frozenset[AccountCondition]`

El mismo riesgo aplica a `BankAccountState.code` → `SavingsAccountStatus` vs `_OPEN_BANK_ACCOUNT_CODES: frozenset[str]`.

### 🔴 Riesgo crítico — `contract_type` sin transformer

`PortfolioCharacteristics.contract_type: Optional[str]` tiene el enum `ContractType` definido, pero **no existe `transform_contract_type`** en ningún transformer. Hay que crearlo antes de migrar este campo.

### 🟡 Riesgo medio — Serializers: cambio de `.value` en ~20 puntos

Hoy el serializer hace: `"sector_label": transform_industry_sector(account.sector).value`
Después haría: `"sector_label": account.sector.value if account.sector else None`

Esto afecta ~20 puntos de uso en 6 serializers. Mypy detecta cualquier error, pero hay que hacerlo cuidadosamente. Los TypedDicts **no cambian** — siguen emitiendo `str` via `.value`.

### 🟡 Riesgo medio — `payment_history` (caso especial, ya documentado)

`payment_history: Optional[str]` se parsea carácter a carácter. Migrar esto al builder requeriría añadir `payment_history_parsed: Optional[tuple[PaymentBehavior, ...]]` como campo adicional. El string crudo tiene valor para auditoría y debug. **Recomendación: no migrar este campo.**

### 🟢 Riesgo bajo — Scope sin tests

~13 modelos, ~12 builders, ~11 serializers tocados. Sin tests, mypy es la única red. Esto es un riesgo conocido y mitigado por el plan de fases: cada fase termina con `0 errores mypy`.

---

## 4. Justificación del cambio

**Muy justificado.** Las razones del documento original siguen vigentes y se añade una nueva:

- El engine (`engines/`) está vacío. Si se llena con raw codes, la deuda técnica se multiplica.
- `is_open` ya opera con lógica de negocio pero comparando strings crudos — esto es inconsistente con el diseño del modelo.
- El refactor de naming que ya se hizo (enums con clasificadores semánticos) pierde valor si los modelos no los usan.
- La nueva razón: el riesgo crítico de `OPEN_ACCOUNT_CODES` ya existe hoy — si alguien añade un nuevo código al XSD, hay que actualizarlo en dos lugares (el transformer Y el frozenset). Con enums en el modelo, hay un solo lugar.

---

## 5. Plan de implementación (actualizado)

### Prerrequisito nuevo (antes de Fase 1)

**P0 — Completar transformer de `AccountCondition`**
- Auditar `OPEN_ACCOUNT_CODES` (35 códigos) contra Tabla 4 del XSD
- Mapear todos los códigos numéricos que faltan en `transform_account_condition`
- Hacer lo mismo para `_OPEN_BANK_ACCOUNT_CODES` vs `transform_savings_account_status`
- Verificar mypy: 0 errores

**P1 — Crear `transform_contract_type`**
- Añadir en `global_report_transformer.py`
- Mapear los códigos de `ContractType` (FIXED_TERM, INDEFINITE, NOT_REPORTED)
- Verificar mypy: 0 errores

---

### Fase 1 — Piloto: `PortfolioCharacteristics` (excluyendo `contract_type`)

Modelos: `PortfolioCharacteristics`
Builders: `GlobalReportBuilder._parse_characteristics()`
Serializers: `serializer_global_report._serialize_characteristics()`

Campos a migrar:
- `account_type: Optional[str]` → `Optional[AccountType]`
- `obligation_type: Optional[str]` → `Optional[ObligationType]`
- `debtor_quality: Optional[str]` → `Optional[DebtorRole]`
- `guarantee: Optional[str]` → `Optional[GuaranteeType]`

Impacto en TypedDicts: `SerializedPortfolioCharacteristics` — los campos que hoy son `Optional[str]` se quedan como `Optional[str]` (reciben `.value`). Sin cambio.
Gate: 0 errores mypy → commit.

---

### Fase 2 — `PortfolioValues` + campos planos de `PortfolioAccount` + `contract_type`

Modelos: `PortfolioValues`, `PortfolioAccount` (campos planos, no `payment_history`)
Builders: `GlobalReportBuilder._parse_values()`, `GlobalReportBuilder._parse_account()`
Serializers: `serializer_global_report._serialize_value()`, `_serialize_account()`

Campos a migrar en `PortfolioValues`:
- `currency_code` → `Optional[Currency]`
- `credit_rating` → `Optional[CreditRating]`
- `payment_frequency` → `Optional[PaymentFrequency]`

Campos a migrar en `PortfolioAccount`:
- `credit_rating` → `Optional[CreditRating]`
- `ownership_status` → `Optional[OwnershipSituation]`
- `industry_sector` → `Optional[IndustrySector]`
- `contract_type` (en `PortfolioCharacteristics`) → `Optional[ContractType]` (requiere P1)

Gate: 0 errores mypy → commit.

---

### Fase 3 — `PortfolioStates` + `CreditCardStates` + actualizar `is_open`

Este es el paso más delicado. Requiere P0 completado.

Modelos: `PortfolioStates`, `CreditCardStates`
Builders: parseo de estados en `GlobalReportBuilder`, `CreditCardReportBuilder`
Serializers: `_serialize_portfolio_states()`, `_serialize_states()`

Campos a migrar:
- `account_statement_code` → `Optional[AccountCondition]`
- `origin_state_code` → `Optional[OriginState]`
- `payment_status_code` → `Optional[PaymentStatus]`
- `plastic_state_code` → `Optional[PlasticStatus]`

Migración de `is_open`:
```python
# Antes
OPEN_ACCOUNT_CODES: frozenset[str]
return code in OPEN_ACCOUNT_CODES

# Después
OPEN_ACCOUNT_STATUSES: frozenset[AccountCondition]
return self.states.account_statement_code in OPEN_ACCOUNT_STATUSES
```

Gate: 0 errores mypy → commit.

---

### Fase 4 — `BankAccount`, `CheckingAccount` + `BankAccountState` + `is_open`

Mismo patrón. Menor complejidad conceptual.
Incluye actualizar `_OPEN_BANK_ACCOUNT_CODES` → `_OPEN_BANK_ACCOUNT_STATUSES: frozenset[SavingsAccountStatus]`

Gate: 0 errores mypy → commit.

---

### Fase 5 — `CreditCard`, `CreditCardCharacteristics`, `CreditCardValues`

Mismo patrón. Builders de tarjeta de crédito.
Gate: 0 errores mypy → commit.

---

### Fase 6 — `QueryRecord`, `GlobalDebtRecord`

Builders de consultas y deuda global.
Gate: 0 errores mypy → commit.

---

### Fase 7 — `AggregatedInfo` / `MicroCreditAggregatedInfo` (opcional, baja urgencia)

Estos modelos son complejos y el engine no los consumirá en las primeras iteraciones.
Defer hasta que el engine los necesite.

---

## 6. Impacto en TypedDicts

Los TypedDicts en `types/` **no cambian estructuralmente**. Los serializers seguirán emitiendo `str` via `.value`:

```python
# Hoy (serializer llama transformer)
"sector_label": transform_industry_sector(account.sector).value

# Después (serializer usa .value directamente)
"sector_label": account.sector.value if account.sector else None
```

Los campos `_code` (código crudo) que hoy exponen algunos serializers (ej: `"sector": account.sector`) desaparecen del modelo. Si la API los necesita, el serializer puede omitirlos o el TypedDict puede eliminar esos campos. Esto es una decisión de API, no de modelo.

---

## 7. Veredicto final

| Dimensión | Evaluación |
|---|---|
| ¿Es posible hacerlo ahora? | **Sí**, con dos prerrequisitos pequeños (P0, P1) |
| ¿Está justificado? | **Sí, fuertemente** — el engine vacío es el momento ideal |
| Riesgo principal | `OPEN_ACCOUNT_CODES` incompleto — bloquea Fase 3, no las anteriores |
| Esfuerzo estimado | Fases 1-2: bajo. Fase 3: medio. Fases 4-6: bajo-medio |
| Reversibilidad | Alta — cada fase es un commit independiente y mypy valida cada paso |
| Urgencia | Media — no urgente, pero el costo crece con cada línea de engine escrita |

**Recomendación: ejecutar P0 + P1 + Fases 1 y 2 en la próxima sesión. Fases 3 en adelante cuando se confirme el mapping completo del XSD.**
