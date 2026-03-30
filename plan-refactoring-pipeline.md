# Plan de refactoring — Pipeline PortfolioAccount

## Objetivo
Mover la responsabilidad de los transformers del serializer al builder.
Cada modelo recibe el enum directamente; el serializer solo hace `.value` si el TypedDict espera `str`.

## Estado previo
- **Fase 1 (PortfolioCharacteristics)** ✅ completada: `account_type`, `obligation_type`, `debtor_quality`, `guarantee`

---

## Iteración 1 — `PortfolioValues` + `contract_type`

### Archivos tocados
- `xml_adapter/models/global_report_models.py`
- `xml_adapter/report_builders/global_report_report_builder.py`
- `xml_adapter/serializers/serializer_global_report.py`

### Cambios en modelo (`PortfolioValues`)
| Campo | Antes | Después |
|---|---|---|
| `currency_code` | `Optional[str]` | `Optional[Currency]` |
| `credit_rating` | `Optional[str]` | `Optional[CreditRating]` |
| `payment_frequency` | `Optional[str]` | `Optional[PaymentFrequency]` |

### Cambios en modelo (`PortfolioCharacteristics`)
| Campo | Antes | Después |
|---|---|---|
| `contract_type` | `Optional[str]` | `Optional[ContractType]` |

### Cambios en builder (`_parse_value_portfolio`, `_parse_characteristics`)
- `currency_code=ex.get_attr(...)` → `transform_currency(...)`
- `credit_rating=ex.get_attr(...)` → `transform_credit_rating(...)`
- `payment_frequency=ex.get_attr(...)` → `transform_payment_frequency(...)`
- `contract_type=ex.get_attr(...)` → `transform_contract_type(...)`

### Cambios en serializer (`_serialize_value`, `_serialize_characteristics`)
- `"currency": v.currency_code` → `v.currency_code.value if v.currency_code else None`
- `"credit_rating": v.credit_rating` → `v.credit_rating.value if v.credit_rating else None`
- `"payment_frequency": transform_payment_frequency(v.payment_frequency)` → `v.payment_frequency`
- `"contract_type": c.contract_type` → `c.contract_type.value if c.contract_type else None`
- Eliminar import `transform_payment_frequency` del serializer
- Agregar imports al builder: `transform_currency`, `transform_credit_rating`, `transform_contract_type`

### TypedDicts — sin cambios estructurales
- `SerializedPortfolioValues.currency: Optional[str]` — emite `.value` ✓
- `SerializedPortfolioValues.credit_rating: Optional[str]` — emite `.value` ✓
- `SerializedPortfolioValues.payment_frequency: Optional[PaymentFrequency]` — pasa directo ✓
- `SerializedPortfolioCharacteristics.contract_type: Optional[str]` — emite `.value` ✓

---

## Iteración 2 — `PortfolioStates` + `is_open`

### Archivos tocados
- `xml_adapter/models/global_report_models.py`
- `xml_adapter/report_builders/global_report_report_builder.py`
- `xml_adapter/serializers/serializer_global_report.py`

### Cambios en modelo (`PortfolioStates`)
| Campo | Antes | Después |
|---|---|---|
| `account_statement_code` | `Optional[str]` | `Optional[AccountCondition]` |
| `origin_state_code` | `Optional[str]` | `Optional[OriginState]` |
| `payment_status_code` | `Optional[str]` | `Optional[PaymentStatus]` |

### Cambios en constante + propiedad (`PortfolioAccount`)
```python
# Antes
OPEN_ACCOUNT_CODES: frozenset[str] = frozenset({"01", "13", ...})
@property
def is_open(self) -> bool:
    code = self.states.account_statement_code
    return code in OPEN_ACCOUNT_CODES

# Después
OPEN_ACCOUNT_CONDITIONS: frozenset[AccountCondition] = frozenset({
    AccountCondition.ON_TIME,
    AccountCondition.OVERDUE_DEBT,
    AccountCondition.WRITTEN_OFF,
    AccountCondition.DOUBTFUL_COLLECTION,
})
@property
def is_open(self) -> bool:
    condition = self.states.account_statement_code
    if condition is None:
        return False
    return condition in OPEN_ACCOUNT_CONDITIONS
```

### Cambios en builder (`_parse_states`)
- `account_statement_code=ex.get_attr(ec, "codigo")` → `transform_account_condition(...)`
- `origin_state_code=ex.get_attr(eo, "codigo")` → `transform_origin_state(...)`
- `payment_status_code=ex.get_attr(ep, "codigo")` → `transform_payment_status(...)`
- Fallback `PortfolioStates(None, None, None, None, None, None, None)` — sin cambio (sigue None)

### Cambios en serializer (`_serialize_portfolio_states`)
- `"account_statement_code": transform_account_condition(e.account_statement_code)` → `e.account_statement_code`
- `"origin_state_code": e.origin_state_code` → `e.origin_state_code.value if e.origin_state_code else None`
- `"payment_status_code": e.payment_status_code` → `e.payment_status_code.value if e.payment_status_code else None`
- `"payment_status_label": transform_payment_status(e.payment_status_code).value` → `e.payment_status_code.value if e.payment_status_code else None`
- Eliminar imports `transform_account_condition`, `transform_payment_status` del serializer
- Agregar imports al builder: `transform_account_condition`, `transform_origin_state`, `transform_payment_status`

### TypedDicts — sin cambios estructurales
- `SerializedPortfolioStates.account_statement_code: Optional[AccountCondition]` — pasa directo ✓
- `SerializedPortfolioStates.origin_state_code: Optional[str]` — emite `.value` ✓
- `SerializedPortfolioStates.payment_status_code: Optional[str]` — emite `.value` ✓
- `SerializedPortfolioStates.payment_status_label: Optional[str]` — emite `.value` (mismo que payment_status_code) ✓

---

## Iteración 3 — `PortfolioAccount` campos planos

### Archivos tocados
- `xml_adapter/models/global_report_models.py`
- `xml_adapter/report_builders/global_report_report_builder.py`
- `xml_adapter/serializers/serializer_global_report.py`

### Cambios en modelo (`PortfolioAccount`)
| Campo | Antes | Después |
|---|---|---|
| `credit_rating` | `Optional[str]` | `Optional[CreditRating]` |
| `ownership_status` | `Optional[str]` | `Optional[OwnershipSituation]` |
| `industry_sector` | `Optional[str]` | `Optional[IndustrySector]` |

### Cambios en builder (`_parse_account_wallet`)
- `credit_rating=ex.get_attr(...)` → `transform_credit_rating(...)`
- `ownership_status=ex.get_attr(...)` → `transform_ownership_situation(...)`
- `industry_sector=ex.get_attr(...)` → `transform_industry_sector(...)`

### Cambios en serializer (`_serialize_account`)
- `"credit_rating": c.credit_rating` → `c.credit_rating.value if c.credit_rating else None`
- `"ownership_status": c.ownership_status` → `c.ownership_status.value if c.ownership_status else None`
- `"industry_sector": c.industry_sector` → `c.industry_sector.value if c.industry_sector else None`

### TypedDicts — sin cambios estructurales
- `SerializedPortfolioAccount.credit_rating: Optional[str]` — emite `.value` ✓
- `SerializedPortfolioAccount.ownership_status: Optional[str]` — emite `.value` ✓
- `SerializedPortfolioAccount.industry_sector: Optional[str]` — emite `.value` ✓

---

## Campos que NO se migran
- `payment_history: Optional[str]` — string de chars, se transforma carácter a carácter solo en el serializer
- `entity_id_type`, `entity_id`, `dane_city_code`, `subscriber_code` — strings de infraestructura sin enum
- `hd_rating: bool`, `is_blocked: bool` — booleanos, sin cambio
- `default_probability: Optional[float]` — numérico, sin cambio
- Fechas (todos los campos `*_date`) — strings ISO, sin cambio
