# Análisis de estado — Credit Solver Engine
> Actualizado: 2026-03-25 | Basado en análisis de 26 XMLs reales + XSD v1.6 + Manual Insumos XML v1.6.4

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

## 7. Arquitectura — Observaciones

- **Parseo múltiple del mismo XML**: `FullReportBuilder` instancia `BasicDataReportBuilder` y `GlobalReportBuilder` internamente, cada uno re-parsea el XML. Técnicamente funciona pero es ineficiente. Refactor pendiente.
- **`payment_habits_open/closed`** usa el sector como clave raw del dict ("1", "2"), no el label del enum. Inconsistente con el resto de la API.
- **`closed_portfolio_accounts`** no tiene sección propia en el full-report. Las CuentaCartera cerradas quedan dentro de `payment_habits_closed`, sin lista plana accesible.
- **`comportamiento`** en CuentaCartera/TarjetaCredito (string de 47 chars) se expone crudo. El transformer `transform_payment_behavior_char` existe para procesarlo char-a-char si se necesita.
- **0 errores mypy** en 69 archivos fuente.

---

## 8. Resumen de prioridades restantes

| # | Qué | Estado | Relevancia motor |
|---|---|---|---|
| 1 | Aplicar `transform_payment_behavior_char` en serializer de CuentaCartera/TarjetaCredito — campo `payment_history_parsed` | ✅ Implementado | **Alta** (scoring) |
| 2 | Aplicar `transform_query_reason` en serializer de QueryRecord — campo `reason_label` | ✅ Implementado | Media |
| 3 | Aplicar `transform_guarantee` en serializer de CuentaCartera/TarjetaCredito — campo `guarantee_label` | ✅ Implementado | Media |
| 4 | Enum `PaymentStatus` + transformer `transform_payment_status` para `payment_status_code` (EstadoPago, Tabla 4) — campo `payment_status_label` | ✅ Implementado | Media |
| 5 | Modelos `ScoreRecord`/`AlertRecord`, parseo en builder, serializer, TypedDicts en `types.py` — campos `score_records`/`alert_records` en full-report | ✅ Implementado | Media |
| 6 | Enum `CurrentDebtState` + `transform_current_debt_state` para `current_state` en `EndeudamientoActual` — campo `current_state_label` | ✅ Implementado | **Alta** (scoring) |
| 7 | Refactor: parseo único del XML en `FullReportBuilder` (actualmente re-parsea 2 veces) | ⏳ Pendiente | Performance |
| 8 | Manejo de errores en views (actualmente 500 en cualquier excepción) | ⏳ Pendiente | Producción |

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
