# Plan de Refactoring — Fase 2: Modelos Pendientes

**Objetivo:** Mover transformers del serializer al builder en los modelos que quedan sin migrar.
**Regla:** cada iteración termina con `0 errores mypy` antes de continuar.
**Campos que NUNCA se migran:** `payment_history: Optional[str]` (transformado char a char en el serializer), fechas, NITs, códigos de infraestructura.

---

## Estado de partida

### ✅ Ya migrado (`global_report_models.py`)
| Modelo | Campos migrados |
|---|---|
| `PortfolioCharacteristics` | `account_type`, `obligation_type`, `debtor_quality`, `guarantee`, `contract_type` |
| `PortfolioValues` | `currency_code`, `credit_rating`, `payment_frequency` |
| `PortfolioStates` | `account_statement_code`, `origin_state_code`, `payment_status_code` |
| `PortfolioAccount` | `credit_rating`, `ownership_status`, `industry_sector` |
| `PortfolioAccount.is_open` | `OPEN_ACCOUNT_CODES` → `OPEN_ACCOUNT_CONDITIONS: frozenset[AccountCondition]` |

### ⏳ Pendiente
- `credit_card_models.py` → Iteración A
- `bank_account_models.py` + `checking_account_models.py` → Iteración B
- `query_models.py` + `global_debt_models.py` → Iteración C

---

## Iteración A — CreditCard

### Archivos tocados
- `xml_adapter/models/credit_card_models.py`
- `xml_adapter/report_builders/credit_card_report_builder.py`
- `xml_adapter/serializers/serializer_credit_card.py`

### A.1 — Modelo: campos a migrar

**`CreditCardCharacteristics`**
| Campo actual | Tipo destino | Transformer |
|---|---|---|
| `franchise: Optional[str]` | `Optional[CreditCardFranchise]` | `transform_franchise` |
| `card_class: Optional[str]` | `Optional[CreditCardClass]` | `transform_credit_card_class` |
| `guarantee: Optional[str]` | `Optional[GuaranteeType]` | `transform_guarantee` |

**`CreditCardValues`**
| Campo actual | Tipo destino | Transformer |
|---|---|---|
| `currency_code: Optional[str]` | `Optional[Currency]` | `transform_currency` |
| `rating: Optional[str]` | `Optional[CreditRating]` | `transform_credit_rating` |

**`CreditCardStates`**
| Campo actual | Tipo destino | Transformer |
|---|---|---|
| `plastic_state_code: Optional[str]` | `Optional[PlasticStatus]` | `transform_plastic_status` |
| `account_state_code: Optional[str]` | `Optional[AccountCondition]` | `transform_account_condition` |
| `origin_state_code: Optional[str]` | `Optional[OriginState]` | `transform_origin_state` |
| `payment_status_code: Optional[str]` | `Optional[PaymentStatus]` | `transform_payment_status` |

**`CreditCard` (campos planos)**
| Campo actual | Tipo destino | Transformer |
|---|---|---|
| `payment_method: Optional[str]` | `Optional[PaymentMethod]` | `transform_payment_method` |
| `credit_rating: Optional[str]` | `Optional[CreditRating]` | `transform_credit_rating` |
| `ownership_situation: Optional[str]` | `Optional[OwnershipSituation]` | `transform_ownership_situation` |
| `sector: Optional[str]` | `Optional[IndustrySector]` | `transform_industry_sector` |

### A.2 — `is_open`: migración de frozenset

```python
# Antes
_OPEN_CARD_CODES: frozenset[str] = frozenset({"01","13","14",...})

def is_open(self) -> bool:
    code = self.states.account_state_code   # Optional[str]
    return code in _OPEN_CARD_CODES

# Después
_OPEN_CARD_CONDITIONS: frozenset[AccountCondition] = frozenset({
    AccountCondition.ON_TIME,
    AccountCondition.OVERDUE_DEBT,
    AccountCondition.WRITTEN_OFF,
    AccountCondition.DOUBTFUL_COLLECTION,
})

def is_open(self) -> bool:
    condition = self.states.account_state_code  # Optional[AccountCondition]
    if condition is None:
        return False
    return condition in _OPEN_CARD_CONDITIONS
```

### A.3 — Builder: transformers a agregar

Agregar al builder (`credit_card_report_builder.py`):
```python
from data_adapter.transformers.credit_card_transformer import (
    transform_credit_card_class,
    transform_franchise,
    transform_plastic_status,
)
from data_adapter.transformers.global_report_transformer import transform_account_condition
from data_adapter.transformers.shared_transformers import (
    transform_credit_rating,
    transform_currency,
    transform_guarantee,
    transform_industry_sector,
    transform_origin_state,
    transform_ownership_situation,
    transform_payment_method,
    transform_payment_status,
)
```

Métodos a modificar: `_parse_card`, `_parse_characteristics`, `_parse_values`, `_parse_states`.

### A.4 — Serializer: patrón después del refactor

El serializer actual usa doble campo: `field` (código crudo) + `field_label` (label del transformer).
Después del refactor, el modelo ya no guarda el código crudo — ambos campos emiten `.value`.

```python
# Antes (ejemplo con franchise)
"franchise":       c.franchise,                          # str crudo: "2"
"franchise_label": transform_franchise(c.franchise).value  # label: "Visa"

# Después
"franchise":       c.franchise.value if c.franchise else None,  # label: "Visa"
"franchise_label": c.franchise.value if c.franchise else None,  # label: "Visa" (idéntico)
```

⚠️ **Resultado:** `franchise` y `franchise_label` emiten el mismo valor. La misma situación aplica a `card_class`/`card_class_label`, `guarantee`/`guarantee_label`, `rating`/`rating_label`, `credit_rating`/`credit_rating_label`, `payment_method`/`payment_method_label`, `sector`/`sector_label`, etc. Los TypedDicts NO cambian. Esta redundancia es heredada del diseño original.

Transformers a **eliminar** del serializer (ya no son necesarios):
- `transform_franchise`, `transform_credit_card_class`, `transform_plastic_status`
- `transform_credit_rating`, `transform_guarantee`
- `transform_origin_state`, `transform_ownership_situation`
- `transform_payment_behavior_char` — **NO eliminar**, sigue aplicándose a `payment_history` char a char
- `transform_payment_method`, `transform_payment_status`, `transform_industry_sector`

### A.5 — TypedDicts: sin cambios estructurales

`types_credit_card.py` no cambia. Todos los campos siguen siendo `Optional[str]` (reciben `.value`) o tipos ya correctos.

---

## Iteración B — BankAccount + CheckingAccount

### Archivos tocados
- `xml_adapter/models/bank_account_models.py`
- `xml_adapter/models/checking_account_models.py` ← sólo campos planos
- `xml_adapter/report_builders/bank_account_report_builder.py`
- `xml_adapter/report_builders/checking_account_report_builder.py`
- `xml_adapter/serializers/serializer_bank_account.py`
- `xml_adapter/serializers/serializer_checking_account.py`

### B.1 — Modelo: campos a migrar

**`BankAccountValue`** (compartido entre `BankAccount` y `CheckingAccount`)
| Campo actual | Tipo destino | Transformer |
|---|---|---|
| `currency_code: Optional[str]` | `Optional[Currency]` | `transform_currency` |
| `rating: Optional[str]` | `Optional[CreditRating]` | `transform_credit_rating` |

**`BankAccountState`** (compartido entre `BankAccount` y `CheckingAccount`)
| Campo actual | Tipo destino | Transformer |
|---|---|---|
| `code: Optional[str]` | `Optional[SavingsAccountStatus]` | `transform_savings_account_status` |

**`BankAccount` (campos planos)**
| Campo actual | Tipo destino | Transformer |
|---|---|---|
| `rating: Optional[str]` | `Optional[CreditRating]` | `transform_credit_rating` |
| `ownership_situation: Optional[str]` | `Optional[OwnershipSituation]` | `transform_ownership_situation` |
| `sector: Optional[str]` | `Optional[IndustrySector]` | `transform_industry_sector` |

**`CheckingAccount` (campos planos)**
| Campo actual | Tipo destino | Transformer |
|---|---|---|
| `ownership_situation: Optional[str]` | `Optional[OwnershipSituation]` | `transform_ownership_situation` |
| `sector: Optional[str]` | `Optional[IndustrySector]` | `transform_industry_sector` |

### B.2 — `is_open`: migración de frozenset

```python
# Antes (bank_account_models.py)
_OPEN_BANK_ACCOUNT_CODES: frozenset[str] = frozenset({"01", "06", "07"})

def is_open(self) -> bool:
    if self.state is None or self.state.code is None:
        return False
    return self.state.code in _OPEN_BANK_ACCOUNT_CODES

# Después
_OPEN_BANK_ACCOUNT_STATUSES: frozenset[SavingsAccountStatus] = frozenset({
    SavingsAccountStatus.ACTIVE,      # "01"
    SavingsAccountStatus.SEIZED,      # "06"
    SavingsAccountStatus.SEIZED_ACTIVE,  # "07"
})

def is_open(self) -> bool:
    if self.state is None or self.state.code is None:
        return False
    return self.state.code in _OPEN_BANK_ACCOUNT_STATUSES
```

Verificación de consistencia con `transform_savings_account_status`:
- `"01"` → `SavingsAccountStatus.ACTIVE` ✓
- `"06"` → `SavingsAccountStatus.SEIZED` ✓
- `"07"` → `SavingsAccountStatus.SEIZED_ACTIVE` ✓

### B.3 — Builder bank_account: transformers a agregar

```python
from data_adapter.transformers.shared_transformers import (
    transform_credit_rating,
    transform_currency,
    transform_industry_sector,
    transform_ownership_situation,
    transform_savings_account_status,
)
```

Métodos a modificar: `_parse_account`, `_parse_value`, `_parse_state`.

### B.4 — Builder checking_account: transformers a agregar

```python
from data_adapter.transformers.shared_transformers import (
    transform_credit_rating,
    transform_currency,
    transform_industry_sector,
    transform_ownership_situation,
    transform_savings_account_status,
)
```

Métodos a modificar: `_parse_account`, `_parse_value`, `_parse_state`.

⚠️ **Nota crítica:** `BankAccountValue` y `BankAccountState` son compartidos entre `BankAccount` y `CheckingAccount`. Si el builder de `BankAccount` los migra en `_parse_value` / `_parse_state`, el builder de `CheckingAccount` hace exactamente lo mismo (los métodos son idénticos en estructura). Ambos builders deben migrarse en la misma iteración.

### B.5 — Serializer bank_account: patrón después del refactor

```python
# Antes
"rating":       account.rating,                                      # str crudo
"rating_label": transform_credit_rating(account.rating).value        # label

# Después
"rating":       account.rating.value if account.rating else None,    # label (mismo)
"rating_label": account.rating.value if account.rating else None,    # label (idéntico)
```

Lo mismo para `ownership_situation`/`ownership_situation_label`, `sector`/`sector_label`.

Para `BankAccountState`:
```python
# Antes
"code":  s.code,                                     # str crudo: "01"
"label": transform_savings_account_status(s.code).value  # label

# Después
"code":  s.code.value if s.code else None,           # label
"label": s.code.value if s.code else None,           # label (idéntico)
```

Para `BankAccountValue`:
```python
# Antes
"currency_code":  v.currency_code,     # str crudo (currency_label hardcodeado None — ver §Bugs)
"rating":         v.rating,            # str crudo
"rating_label":   transform_credit_rating(v.rating).value

# Después
"currency_code":  v.currency_code.value if v.currency_code else None,
"rating":         v.rating.value if v.rating else None,
"rating_label":   v.rating.value if v.rating else None,
```

Transformers a **eliminar** del serializer_bank_account: todos excepto ninguno queda.
Transformers a **eliminar** del serializer_checking_account: todos.

### B.6 — TypedDicts: sin cambios estructurales

`types_bank_account.py` no cambia.

---

## Iteración C — QueryRecord + GlobalDebtRecord

### Archivos tocados
- `xml_adapter/models/query_models.py`
- `xml_adapter/models/global_debt_models.py`
- `xml_adapter/report_builders/query_builder.py`
- `xml_adapter/report_builders/global_debt_builder.py`
- `xml_adapter/serializers/serializer_query.py`
- `xml_adapter/serializers/serializer_global_debt.py`

### C.1 — Modelo: campos a migrar

**`QueryRecord`**
| Campo actual | Tipo destino | Transformer |
|---|---|---|
| `account_type: Optional[str]` | `Optional[AccountType]` | `transform_account_type` |
| `reason: Optional[str]` | `Optional[QueryReason]` | `transform_query_reason` |
| `sector: Optional[str]` | `Optional[IndustrySector]` | `transform_industry_sector` |

**`GlobalDebtRecord`**
| Campo actual | Tipo destino | Transformer |
|---|---|---|
| `rating: Optional[str]` | `Optional[CreditRating]` | `transform_credit_rating` |
| `credit_type: Optional[str]` | `Optional[GlobalDebtCreditType]` | `transform_global_debt_credit_type` |
| `currency: Optional[str]` | `Optional[Currency]` | `transform_currency` |

**`GlobalDebtEntity`**
| Campo actual | Tipo destino | Transformer |
|---|---|---|
| `sector: Optional[str]` | `Optional[IndustrySector]` | `transform_industry_sector` |

**`GlobalDebtGuarantee`**
| Campo actual | Tipo destino | Transformer |
|---|---|---|
| `guarantee_type: Optional[str]` | `Optional[GuaranteeType]` | `transform_guarantee` |

### C.2 — Builder query_builder: transformers a agregar

```python
from data_adapter.transformers.global_report_transformer import transform_account_type
from data_adapter.transformers.shared_transformers import transform_industry_sector, transform_query_reason
```

Método a modificar: `_parse_record`.

### C.3 — Builder global_debt_builder: transformers a agregar

```python
from data_adapter.transformers.global_debt_transformer import transform_global_debt_credit_type
from data_adapter.transformers.shared_transformers import (
    transform_credit_rating,
    transform_currency,
    transform_guarantee,
    transform_industry_sector,
)
```

Métodos a modificar: `_parse_record`, `_parse_guarantee` (inline en `_parse_record` para entity).

### C.4 — Serializer query: patrón después del refactor

```python
# Antes
"account_type": record.account_type,   # str crudo
"reason":       record.reason,         # str crudo
"reason_label": transform_query_reason(record.reason).value,
"sector":       record.sector,         # str crudo
"sector_label": transform_industry_sector(record.sector).value,

# Después
"account_type": record.account_type.value if record.account_type else None,
"reason":       record.reason.value if record.reason else None,
"reason_label": record.reason.value if record.reason else None,  # idéntico
"sector":       record.sector.value if record.sector else None,
"sector_label": record.sector.value if record.sector else None,  # idéntico
```

### C.5 — Serializer global_debt: patrón después del refactor

```python
# GlobalDebtRecord
"rating":            record.rating.value if record.rating else None,
"credit_type":       record.credit_type.value if record.credit_type else None,
"credit_type_label": record.credit_type.value if record.credit_type else None,  # idéntico
"currency":          record.currency.value if record.currency else None,

# GlobalDebtEntity
"sector":       e.sector.value if e.sector else None,
"sector_label": e.sector.value if e.sector else None,  # idéntico

# GlobalDebtGuarantee
"guarantee_type":       g.guarantee_type.value if g.guarantee_type else None,
"guarantee_type_label": g.guarantee_type.value if g.guarantee_type else None,  # idéntico
```

Transformers a **eliminar** del serializer_global_debt: `transform_guarantee`, `transform_industry_sector`, `transform_global_debt_credit_type`.

### C.6 — TypedDicts: sin cambios estructurales

`types_global_debt.py` no cambia.

---

## Trampas y reglas transversales

### Regla 1 — `payment_history` nunca va al modelo como enum
El campo `payment_history: Optional[str]` se transforma character a character con `transform_payment_behavior_char` directamente en el serializer. No es un código único — es una secuencia histórica. No migrar.

### Regla 2 — Los `*_label` quedan redundantes tras la migración
Todos los pares `field_code + field_label` quedan emitiendo el mismo `.value` porque el modelo ya no guarda el código crudo. Los TypedDicts no cambian; la API expone ambos campos con el mismo valor. Esta redundancia es deuda pre-existente en el diseño de la API — no es scope de este refactor.

### Regla 3 — No olvidar los fallbacks `None` en builders
Cuando un builder construye el modelo con `None` (nodo XML ausente), los campos ahora son `Optional[Enum]` — el valor `None` sigue siendo válido y el transformer no se llama. El transformer solo se llama cuando hay un valor: `transform_x(ex.get_attr(node, "attr"))`.

### Regla 4 — Modelos compartidos: migrar en la misma iteración
`BankAccountValue` y `BankAccountState` son usados por `BankAccount` y `CheckingAccount` — ambos builders deben migrarse juntos en Iteración B para evitar inconsistencias de tipos.

---

## Bugs pre-existentes (no scope del refactor)

Documentados para no confundirlos con errores introducidos.

### Bug 1 — `currency_label: None` hardcodeado (3 serializers)
| Archivo | Línea | Descripción |
|---|---|---|
| `serializer_bank_account.py` | 43 | `"currency_label": None` — transformer existe pero no se aplica |
| `serializer_checking_account.py` | 48 | `"currency_label": None` — ídem |
| `serializer_credit_card.py` | 83 | `"currency_label": None` — ídem |

**Causa:** Se dejó el campo pero nunca se implementó `transform_currency` para esa posición.
**Impacto:** La API siempre devuelve `null` en `currency_label`. Bajo.
**Corrección:** Después del refactor, el modelo almacenará `Optional[Currency]`, por lo que `currency_label` pasará a ser `v.currency_code.value if v.currency_code else None` de forma natural — **este bug desaparece automáticamente en Iteración B**.

### Bug 2 — `is_blocked: Optional[bool]` en `SerializedPortfolioAccount`
**Archivo:** `types_portfolio.py`, línea 58
**Problema:** El TypedDict permite `None`, pero el modelo `PortfolioAccount.is_blocked: bool` nunca es `None`. Mypy strict podría aceptarlo (asignación `bool` → `Optional[bool]` es válida), pero es impreciso.
**Corrección:** Cambiar a `is_blocked: bool` en el TypedDict en una limpieza futura.

### Bug 3 — `payment_status_code` y `payment_status_label` emiten el mismo valor (post-refactor)
**Archivo:** `serializer_global_report.py`, líneas 86-87
**Causa:** Introducido en nuestra migración. Antes, `payment_status_code` era el código crudo (`"20"`) y `payment_status_label` el label (`"En Mora 30 días"`). Ahora ambos emiten `.value` del enum.
**Impacto:** Medio — el código crudo ya no está disponible en la API.
**Decisión pendiente:** Si el engine o consumidores necesitan el código crudo (`"20"`), hay que evaluar si conservarlo en el TypedDict. Por ahora se acepta la pérdida.
