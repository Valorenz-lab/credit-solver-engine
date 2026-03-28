# Guía de refactoring — split de types.py

Estado actual: 617 líneas · 51 TypedDicts · 1 archivo monolítico
Objetivo: 9 archivos por dominio en `xml_adapter/types/`

---

## Estructura de destino

```
xml_adapter/types/
  __init__.py              ← re-exporta todo (compatibilidad de imports)
  types_basic.py
  types_portfolio.py
  types_bank_account.py
  types_credit_card.py
  types_global_debt.py     ← añadido (QueryRecord + GlobalDebt no caben en los otros)
  types_aggregated_info.py
  types_micro_credit.py
  types_score_alert.py
  types_full_report.py
```

El archivo `types.py` original se elimina al finalizar.

---

## Inventario por archivo

### types_basic.py
Modelo de origen: `BasicReport`, `BasicDataPerson`, `QueryMetadata`, `CustomerIdentification`, `Age`
Imports de enums: ninguno

| TypedDict | Línea actual |
|---|---|
| `SerializedMetadata` | 9 |
| `SerializedCustomerIdentification` | 18 |
| `SerializedAge` | 27 |
| `SerializedPerson` | 32 |
| `SerializedReport` | 45 |

Dependencias cross-file: ninguna

---

### types_portfolio.py
Modelo de origen: `PortfolioAccount`, `PortfolioCharacteristics`, `PortfolioValues`, `PortfolioStates`, `GlobalReport`
Imports de enums: `AccountCondition`, `ObligationType`, `DebtorRole`, `PaymentFrequency`

| TypedDict | Línea actual |
|---|---|
| `SerializedPortfolioValues` | 54 |
| `SerializedPortfolioStates` | 71 |
| `SerializedPortfolioCharacteristics` | 85 |
| `SerializedPortfolioAccount` | 96 |
| `SerializedGlobalReport` | 122 |

Dependencias cross-file: ninguna (auto-contenido)

---

### types_bank_account.py
Modelo de origen: `BankAccount`, `BankAccountValue`, `BankAccountState`, `CheckingAccount`, `CheckingAccountOverdraft`
Imports de enums: ninguno

| TypedDict | Línea actual |
|---|---|
| `SerializedBankAccountValue` | 129 |
| `SerializedBankAccountState` | 137 |
| `SerializedBankAccount` | 143 |
| `SerializedCheckingAccountOverdraft` | 164 |
| `SerializedCheckingAccount` | 170 |

Dependencias cross-file: ninguna
Nota: `SerializedCheckingAccount` usa `SerializedBankAccountValue` y `SerializedBankAccountState` — ambas en el mismo archivo, sin problema.

---

### types_credit_card.py
Modelo de origen: `CreditCard`, `CreditCardCharacteristics`, `CreditCardValues`, `CreditCardStates`
Imports de enums: ninguno

| TypedDict | Línea actual |
|---|---|
| `SerializedCreditCardCharacteristics` | 191 |
| `SerializedCreditCardValues` | 203 |
| `SerializedCreditCardStates` | 220 |
| `SerializedCreditCard` | 235 |

Dependencias cross-file: ninguna

---

### types_global_debt.py
Modelo de origen: `QueryRecord`, `GlobalDebtRecord`, `GlobalDebtEntity`, `GlobalDebtGuarantee`
Imports de enums: ninguno
Razón de archivo separado: estos modelos no pertenecen a cuentas ni tarjetas; son registros externos de deuda y consultas.

| TypedDict | Línea actual |
|---|---|
| `SerializedQueryRecord` | 263 |
| `SerializedGlobalDebtEntity` | 277 |
| `SerializedGlobalDebtGuarantee` | 284 |
| `SerializedGlobalDebt` | 291 |

Dependencias cross-file: ninguna

---

### types_aggregated_info.py
Modelo de origen: `AggregatedInfo`, `AggregatedSummary`, `AggregatedBalances`, `AggregatedPrincipals`, y sub-tipos
Imports de enums: ninguno

| TypedDict | Línea actual |
|---|---|
| `SerializedAggregatedPrincipals` | 305 |
| `SerializedSectorBalance` | 318 |
| `SerializedMonthlyBalance` | 324 |
| `SerializedMonthlyBehavior` | 330 |
| `SerializedAggregatedBalances` | 336 |
| `SerializedAggregatedSummaryInner` | 348 |
| `SerializedAccountTypeTotals` | 354 |
| `SerializedGrandTotal` | 364 |
| `SerializedPortfolioStateCount` | 373 |
| `SerializedPortfolioCompositionItem` | 378 |
| `SerializedDebtEvolutionQuarter` | 386 |
| `SerializedDebtEvolutionAnalysis` | 402 |
| `SerializedBalanceHistoryQuarter` | 416 |
| `SerializedBalanceHistoryByType` | 423 |
| `SerializedQuarterlyDebtCartera` | 428 |
| `SerializedQuarterlyDebtSector` | 434 |
| `SerializedQuarterlyDebtSummary` | 442 |
| `SerializedAggregatedSummary` | 447 |

Dependencias cross-file: ninguna (auto-contenido)
⚠️ `SerializedDebtEvolutionQuarter` y `SerializedDebtEvolutionAnalysis` son importadas también por `types_micro_credit.py`

---

### types_micro_credit.py
Modelo de origen: `MicroCreditAggregatedInfo`, `GeneralProfile`, y sub-tipos
Imports de enums: ninguno

| TypedDict | Línea actual |
|---|---|
| `SerializedSectorCreditCount` | 460 |
| `SerializedSectorSeniority` | 469 |
| `SerializedGeneralProfile` | 476 |
| `SerializedMonthlyBalancesAndArrears` | 486 |
| `SerializedBalanceDelinquencyVector` | 500 |
| `SerializedCurrentDebtAccount` | 508 |
| `SerializedCurrentDebtByUser` | 520 |
| `SerializedCurrentDebtByType` | 525 |
| `SerializedCurrentDebtBySector` | 530 |
| `SerializedBehaviorMonthlyChar` | 535 |
| `SerializedAccountBehaviorVector` | 541 |
| `SerializedSectorBehaviorVector` | 551 |
| `SerializedTrendDataPoint` | 556 |
| `SerializedTrendSeries` | 561 |
| `SerializedMicroCreditAggregatedInfo` | 566 |

Dependencias cross-file:
- `from data_adapter.xml_adapter.types.types_aggregated_info import SerializedDebtEvolutionQuarter, SerializedDebtEvolutionAnalysis`

---

### types_score_alert.py
Modelo de origen: `ScoreRecord`, `ScoreReason`, `AlertRecord`, `AlertSource`
Imports de enums: ninguno

| TypedDict | Línea actual |
|---|---|
| `SerializedScoreReason` | 576 |
| `SerializedScoreRecord` | 580 |
| `SerializedAlertSource` | 589 |
| `SerializedAlertRecord` | 594 |

Dependencias cross-file: ninguna

---

### types_full_report.py
Modelo de origen: `FullReport`
Imports de enums: ninguno

| TypedDict | Línea actual |
|---|---|
| `SerializedFullReport` | 603 |

Dependencias cross-file (imports necesarios):
```
from data_adapter.xml_adapter.types.types_basic          import SerializedReport
from data_adapter.xml_adapter.types.types_portfolio      import SerializedPortfolioAccount
from data_adapter.xml_adapter.types.types_bank_account   import SerializedBankAccount, SerializedCheckingAccount
from data_adapter.xml_adapter.types.types_credit_card    import SerializedCreditCard
from data_adapter.xml_adapter.types.types_global_debt    import SerializedQueryRecord, SerializedGlobalDebt
from data_adapter.xml_adapter.types.types_aggregated_info import SerializedAggregatedSummary, SerializedDebtEvolutionQuarter
from data_adapter.xml_adapter.types.types_micro_credit   import SerializedMicroCreditAggregatedInfo
from data_adapter.xml_adapter.types.types_score_alert    import SerializedScoreRecord, SerializedAlertRecord
```

---

## __init__.py — re-exportación

Para no tocar todos los imports existentes en serializers y demás, el `__init__.py`
re-exporta todos los TypedDicts con `from .types_X import *` o imports explícitos.

Esto permite que los archivos que hoy hacen:
```python
from data_adapter.xml_adapter.types import SerializedFoo
```
sigan funcionando sin cambios durante la migración.

Opción recomendada: imports explícitos (mypy strict los valida mejor que `*`).

---

## Archivos a actualizar después del split

Todos los imports de `from data_adapter.xml_adapter.types import ...` siguen funcionando
vía `__init__.py` sin tocar los serializers. Solo hay que actualizar si se quiere
apuntar directamente al sub-archivo.

| Serializer | TypedDicts que importa |
|---|---|
| `serializer_basic_report.py` | `SerializedAge`, `SerializedCustomerIdentification`, `SerializedMetadata`, `SerializedPerson`, `SerializedReport` |
| `serializer_global_report.py` | `SerializedGlobalReport`, `SerializedPortfolioAccount`, `SerializedPortfolioCharacteristics`, `SerializedPortfolioStates`, `SerializedPortfolioValues` |
| `serializer_bank_account.py` | `SerializedBankAccount`, `SerializedBankAccountState`, `SerializedBankAccountValue` |
| `serializer_checking_account.py` | `SerializedBankAccountState`, `SerializedBankAccountValue`, `SerializedCheckingAccount`, `SerializedCheckingAccountOverdraft` |
| `serializer_credit_card.py` | `SerializedCreditCard`, `SerializedCreditCardCharacteristics`, `SerializedCreditCardStates`, `SerializedCreditCardValues` |
| `serializer_query.py` | `SerializedQueryRecord` |
| `serializer_global_debt.py` | `SerializedGlobalDebt`, `SerializedGlobalDebtEntity`, `SerializedGlobalDebtGuarantee` |
| `serializer_aggregated_info.py` | múltiples de `types_aggregated_info` + `types_micro_credit` |
| `serializer_score_alert.py` | `SerializedAlertRecord`, `SerializedAlertSource`, `SerializedScoreRecord`, `SerializedScoreReason` |
| `serializer_full_report.py` | `SerializedFullReport` + múltiples sub-tipos |

---

## Orden de ejecución

1. Crear directorio `xml_adapter/types/`
2. Crear los 8 archivos de dominio (sin dependencias primero): `basic` → `portfolio` → `bank_account` → `credit_card` → `global_debt` → `score_alert` → `aggregated_info` → `micro_credit` → `full_report`
3. Crear `__init__.py` con re-exports de los 51 TypedDicts
4. Verificar mypy
5. Eliminar `types.py` original
