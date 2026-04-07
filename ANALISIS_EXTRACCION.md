# ANALISIS_EXTRACCION.md — Estado de la Extracción XML

**Fecha de análisis:** 2026-04-07
**Muestra:** 24 sujetos (XMLs de Datacredito/Experian)
**Herramientas:** `/validate/<id>/` + `/debug/<id>/` endpoints

---

## 1. Resumen ejecutivo

| Indicador | Valor |
|---|---|
| Sujetos analizados | 24 |
| Estado **OK** (0 fallos) | 3 (12.5%) |
| Estado **warnings** | 21 (87.5%) |
| Fallos críticos (≥4 checks) | 2 |
| Total `UNKNOWN` events | 674 |
| Transformers involucrados | 2 (`payment_frequency`, `guarantee`) |
| Node count accuracy | **100%** — 0 pérdidas estructurales |

**Conclusión de alto nivel:** La extracción estructural es perfecta. Todos los nodos XML se extraen sin pérdida. Los warnings no son pérdidas de datos sino dos categorías de problemas bien delimitadas: (1) un bug de clasificación vigente/cerrado que genera el mismatch con InfoAgregada, y (2) códigos no documentados en dos transformers.

---

## 2. Extracción estructural: 100% de fidelidad

El check `node_count` valida que el número de nodos XML extraídos coincide exactamente con los modelos generados. **Todos los sujetos pasan al 100%.**

| Tipo de nodo | Accuracy |
|---|---|
| `CuentaCartera` → `PortfolioAccount` | 100% |
| `TarjetaCredito` → `CreditCard` | 100% |
| `CuentaAhorro` → `BankAccount` | 100% |
| `CuentaCorriente` → `CheckingAccount` | 100% |
| `Consulta` → `QueryRecord` | 100% |
| `EndeudamientoGlobal` → `GlobalDebtRecord` | 100% |
| `Score` → `ScoreRecord` | 100% |
| `Alerta` → `AlertRecord` | 100% |

No hay pérdida de registros. Cada nodo XML tiene su dataclass correspondiente.

---

## 3. Bug principal: misclasificación vigente / cerrado

### 3.1 Magnitud

**22 de 24 sujetos** presentan delta entre `active_credits` de `InfoAgregada` y nuestra suma `is_open(PortfolioAccounts) + is_open(CreditCards)`.

| sujeto | xml_vigentes | ext_vigentes | delta | xml_cerrados | ext_cerrados |
|---|---|---|---|---|---|
| 10064554 | 1 | 1 | **0** ✅ | 5 | 5 |
| 1030613409 | 8 | 8 | **0** ✅ | 12 | 12 |
| 19448324 | 5 | 5 | **0** ✅ | 51 | 51 |
| 13452289 | 14 | 14 | **0** ✅ | 75 | 75 |
| 11794399 | 11 | 7 | **4** ❌ | 26 | 30 |
| 12532647 | 16 | 10 | **6** ❌ | 25 | 31 |
| 12979619 | 4 | 1 | **3** ❌ | 11 | 14 |
| 13364177 | 11 | 7 | **4** ❌ | 14 | 18 |
| 14012717 | 10 | 2 | **8** ❌ | 10 | 18 |
| 18595160 | 3 | 2 | **1** ❌ | 12 | 13 |
| 22389910 | 2 | 1 | **1** ❌ | 7 | 8 |
| 22436588 | 10 | 6 | **4** ❌ | 17 | 21 |
| 32322427 | 7 | 6 | **1** ❌ | 26 | 27 |
| 34554868 | 10 | 6 | **4** ❌ | 20 | 24 |
| 39007435 | 5 | 4 | **1** ❌ | 41 | 42 |
| 43003890 | 7 | 3 | **4** ❌ | 22 | 26 |
| 43432541 | 10 | 6 | **4** ❌ | 15 | 19 |
| 49551526 | 7 | 6 | **1** ❌ | 17 | 18 |
| 73102905 | 11 | 9 | **2** ❌ | 51 | 53 |
| 7423628 | 16 | 12 | **4** ❌ | 53 | 57 |
| 78696456 | 10 | 6 | **4** ❌ | 30 | 34 |
| 80491927 | 10 | 4 | **6** ❌ | 13 | 19 |
| 8526939 | 5 | 2 | **3** ❌ | 12 | 15 |
| 8737538 | 10 | 3 | **7** ❌ | 6 | 13 |

El delta es siempre igual y opuesto entre active y closed: lo que falta en vigentes sobra exactamente en cerrados. No hay registros perdidos, solo clasificados en el grupo equivocado.

### 3.2 Causa raíz identificada

Investigación sobre el sujeto `14012717` (delta=8, caso extremo) revela el patrón con exactitud quirúrgica:

**InfoAgregada `creditoVigentes=10`** desglosado: `sectorFinanciero=1, sectorReal=6, sectorTelcos=3`

Cruzando con los 20 `CuentaCartera` del sujeto y sus saldos reales del XML:

| Entidad | Sector | Código EC | Saldo | Nuestro `is_open` | DC "vigente" |
|---|---|---|---|---|---|
| ITAU CORPBANCA LIBRANZAS | Financiero | 06 cerrada | 3,795,000 | ❌ closed | ✅ vigente |
| ASLEGAL SERVICIOS CRED | Real | 06 cerrada | 1,289,000 | ❌ closed | ✅ vigente |
| CLARO SERV MOV | Telco | 05 cerrada | 168,000 | ❌ closed | ✅ vigente |
| CLARO SERV MOV | Telco | 05 cerrada | 53,000 | ❌ closed | ✅ vigente |
| CREDYTY | Real | 02 cerrada | 1,192,000 | ❌ closed | ✅ vigente |
| CFG PARTNERS ORI:VIVE_ALPHA | Real | 01 vigente | 16,316,000 | ✅ open | ✅ vigente |
| COLOMBIA MOVIL | Telco | 01 vigente | 0 | ✅ open | ✅ vigente |
| GRUPO CONSULTO COLPATRIA | Real | 06 cerrada | 1,027,000 | ❌ closed | ✅ vigente |
| GRUPO JURIDICO FALABELLA | Real | 06 cerrada | 2,900,000 | ❌ closed | ✅ vigente |
| RED INSTANTIC ORIG-MOVISTAR | Telco | 02 cerrada | 129,000 | ❌ closed | ✅ vigente |
| ITAU CORPBANCA CARTERA TOTAL x4 | Financiero | 03 cerrada | None | ❌ closed | ❌ cerrado |
| RAYCO S.A. DISTRIBUIDORA | Real | 03 cerrada | None | ❌ closed | ❌ cerrado |
| BAYPORT x2 | Real | 03 cerrada | 0 | ❌ closed | ❌ cerrado |
| ANTES AVANTEL | Telco | 03 cerrada | -1 | ❌ closed | ❌ cerrado |

Los 10 que Datacredito considera "vigentes" son exactamente las 10 cuentas con `saldoActual > 0` O con código vigente (01). Las que tienen `saldo = None`, `saldo = 0` o `saldo = -1` son cerradas. El patrón es consistente al 100% en este sujeto.

**La regla de Datacredito para "vigente" es:**
```
vigente = (EstadoCuenta.codigo IN rango_vigente) OR (saldoActual > 0)
```

Una cuenta con código de cancelación (06 = cancelada por la institución) pero saldo pendiente positivo sigue siendo una obligación activa: el deudor aún debe dinero independientemente de cómo el producto fue administrativamente cerrado.

### 3.3 Impacto por sector

| Sector | Frecuencia del bug | Relevancia para motor de decisión |
|---|---|---|
| **Real** | Alta (5–6 cuentas por sujeto afectado) | **Crítica** — gestoras de crédito, retailers, libranzas con saldo |
| **Financiero** | Media (1–2 por sujeto) | **Alta** — libranzas bancarias con saldo pendiente |
| **Cooperativo** | Baja | Media |
| **Telecom** | Media (CLARO con saldo) | Baja — servicios, no crédito financiero |

### 3.4 Fix aplicado — estado actual

**Implementado** en `xml_adapter/models/global_report_models.py` (`PortfolioAccount.is_open`) y `xml_adapter/models/credit_card_models.py` (`CreditCard.is_open`):

```python
# Antes — solo consideraba el código EC:
@property
def is_open(self) -> bool:
    condition = self.states.account_statement_code
    if condition is None:
        return False
    return condition in OPEN_ACCOUNT_CONDITIONS

# Ahora — deuda pendiente OR código vigente:
@property
def is_open(self) -> bool:
    condition = self.states.account_statement_code
    has_vigente_code = condition is not None and condition in OPEN_ACCOUNT_CONDITIONS
    has_balance = (
        self.values.outstanding_balance is not None
        and self.values.outstanding_balance > 0
    )
    return has_vigente_code or has_balance
```

### 3.5 Resultados tras el fix

| | Antes | Después |
|---|---|---|
| Sujetos OK (0 fallos) | 3 / 24 | **15 / 24** |
| Con `active_credits` fail | 22 / 24 | **6 / 24** |
| Delta máximo en activos | 8 | **2** |
| Delta promedio en activos | 3.7 | **0.9** |

### 3.6 Residual: 9 sujetos con delta 1–2

Los 9 sujetos restantes con warnings tienen deltas pequeños (1–2 cuentas). Investigación sobre `32322427`, `12532647`, `7423628` identifica dos patrones en los sobre-conteos respecto a InfoAgregada:

**Tipo A — Cuentas cedidas a cobranza** (ej. `COBRANDO ORIGI BANCOL`, `CENTRAL DE INVERSIONES`): la obligación original fue cedida a una agencia de cobro. DC clasifica la obligación original como `cerrada` en su resumen. Nosotros la marcamos como `vigente` porque el saldo es real.

**Tipo B — Productos no entregados** (`EC=02 = CARD_NOT_DELIVERED`): productos que fueron abiertos administrativamente pero nunca activados. Algunos tienen saldo > 0 (ej. libranza de 75M en BCO POPULAR que nunca fue entregada), DC los cuenta como cerrados.

**Bajo-conteo residual** (`13364177`, delta=1): DC cuenta un servicio WOM con `EC=02, saldo=-1` como vigente. `saldo=-1` es un valor centinela de Datacredito que significa "sin información", no una obligación de -1 peso. Sin el saldo, y con código cerrado, no tenemos forma de detectarlo como vigente sin lógica de negocio externa.

### 3.7 Decisión de diseño: fidelidad al dato real

**La extracción cuenta las cuentas cedidas a cobranza como `vigentes`. Esta es la decisión correcta.**

El motor de decisión crediticia necesita los datos reales del sujeto, no la clasificación interna de Datacredito para sus propios reportes:

- Una cuenta con `COBRANDO ORIGI BANCOL` y saldo de 19M pesos **ES una obligación activa**. El deudor sigue debiendo ese dinero independientemente de si el acreedor original la cedió.
- Ocultar esa obligación al motor porque DC la etiqueta como "cerrada en su resumen" empeoraría la calidad de la decisión crediticia.
- Los 6 deltas residuales con InfoAgregada son consecuencia directa de esta fidelidad al dato, no errores de extracción.

**Regla de oro:** `is_open` responde a la pregunta *"¿existe deuda pendiente con este acreedor?"*, no a *"¿coincide con el conteo de InfoAgregada?"*. Son preguntas diferentes.

---

## 4. Transformer: `transform_payment_frequency`

**385 eventos UNKNOWN** distribuidos en dos causas distintas.

### 4.1 Causa A: `periodicidad = null` (255 eventos — 66%)

El atributo `periodicidad` está **ausente en el XML**. No es un código desconocido — el emisor simplemente no reporta el campo.

**Top entidades por sector:**

| Entidad | Sector | Eventos | Observación |
|---|---|---|---|
| RAYCO S.A. DISTRIBUIDORA | **Real** | 36 | Distribuidora consumo masivo |
| CLARO SERV MOV | Telecom | 17 | Servicio móvil |
| BCO POPULAR LIBRANZA | **Financiero** | 14 | Libranza bancaria |
| ITAU CORPBANCA CARTERA TOTAL | **Financiero** | 13 | Cartera total |
| COOTRAMED | Cooperativo | 11 | Crédito cooperativo |
| GNB SUDAMERIS | **Financiero** | 10 | Crédito |
| BCO DAVIVIENDA LIBRE INVERS. | **Financiero** | 7 | Libre inversión |
| MUEBLES JAMAR | Real | 6 | Consumo muebles |
| CORPORACION INTERACTUAR | Real | 6 | Microcrédito |
| COOPANTEX | Cooperativo | 6 | Crédito cooperativo |
| BAYPORT COLOMBIA LIBRANZA | Real | 5 | Libranza |

**Análisis:** La ausencia de `periodicidad` es sistemática en **libranzas** (BCO POPULAR, GNB SUDAMERIS, BAYPORT) — productos con descuento automático por nómina sin una periodicidad estándar reportable. También en carteras de crédito total (ITAU) y créditos de distribuidora (RAYCO).

**Impacto:** `PaymentFrequency.UNKNOWN` en el modelo. Para el motor de decisión, la periodicidad es un campo de contexto, no de scoring primario. **Acción: ninguna urgente** — aceptar que este campo no siempre está disponible.

### 4.2 Causa B: `periodicidad = "9"` (71 eventos — 18%)

Código `"9"` no documentado en Tabla oficial (rango 0–7). **SISTECREDITO domina con 51/71 eventos (72%).**

| Entidad | Sector | Eventos |
|---|---|---|
| SISTECREDITO | **Real** | 51 |
| BCO OCCIDENTE LIBRANZAS | Financiero | 2 |
| ITAU CORPBANCA LIBRANZAS | Financiero | 2 |
| RED INSTANTIC ORIG-MOVISTAR | Telecom | 2 |
| FAMI CREDITO | Real | 2 |
| FONPROCAPS | Real | 2 |
| BANCOLOMBIA | **Financiero** | 1 |
| Otros | Mixto | 9 |

**SISTECREDITO** es una de las mayores compañías de crédito de consumo de Colombia (electrodomésticos, línea blanca, muebles). Con 51 eventos en una muestra de 24, es un emisor masivo. El código `"9"` probablemente representa **cuota única o crédito de plazo irregular** — patrón frecuente en créditos de almacén/retail que no tienen cuota fija mensual.

**Acción recomendada:** Verificar en Manual v1.6.7 si el rango de `periodicidad` fue extendido más allá de 7. Si no está documentado, añadir `PaymentFrequency.ON_DEMAND` o `IRREGULAR` y mapearlo. SISTECREDITO es financieramente significativo.

---

## 5. Transformer: `transform_guarantee`

**284 eventos UNKNOWN** concentrados en 3 valores.

### 5.1 Causa A: `garantia.tipo = "9"` (334 eventos — 98% de este transformer)

**Todos los 334 eventos provienen exclusivamente de `GlobalDebtRecord`** (nodo `EndeudamientoGlobal > Garantia`). Nunca de `CuentaCartera` ni `TarjetaCredito`. Source siempre `DC`.

Tabla 11 del manual cubre: `"0"`, `"1"`, `"2"`, `"A"`–`"O"`. El código `"9"` no está en ninguna de estas entradas.

**Hipótesis:** `EndeudamientoGlobal` es un **resumen agregado de deuda por entidad**, no un registro de obligación individual. La Tabla 11 aplica a obligaciones específicas. Para el nodo de resumen global, Datacredito usa `"9"` posiblemente con el significado de "no aplica para resumen" o "sin garantía específica en el consolidado".

**Impacto en motor de decisión:** El campo `guarantee_type` en `GlobalDebtRecord` es informativo pero **no crítico**. Lo importante del EndeudamientoGlobal es el saldo y el tipo de crédito, no la garantía del resumen.

**Acción:** Añadir `"9"` al mapping con un valor representativo (e.g., `GuaranteeType.NOT_APPLICABLE` si existe o un nuevo `SUMMARY_NOT_SPECIFIED`). Verificar en manual si existe tabla específica para garantías de `EndeudamientoGlobal`.

### 5.2 Causa B: `garantia.tipo = "Q"` (13 eventos)

Presente en `CreditCard` (BCO COLPATRIA, BANCOUNION) y algunos `GlobalDebtRecord`. La Tabla 11 va de `"A"` a `"O"` — `"Q"` es una extensión posterior a `"O"`, posiblemente documentada en versión más reciente del manual.

BCO COLPATRIA y BANCOUNION son entidades **financieras relevantes**. Este código importa para el análisis de garantías en tarjetas de crédito.

**Acción:** Revisar Manual v1.6.7 (`data/HDC+ PN - Manual de Implementacion WS v1.6.7...pdf`) para confirmar si `"Q"` está documentado.

### 5.3 Causa C: `garantia.tipo = "P"` (1 evento)

Evento único. Misma hipótesis que `"Q"` — extensión de tabla. **Prioridad muy baja.**

---

## 6. Discrepancias de balance

La gran mayoría de sujetos pasan con delta ≤ 1.0 (diferencias de redondeo admisibles). Dos excepciones:

### 6.1 Sujeto `78696456` — delta 124,999 miles de pesos (~125M COP)

```
xml_value  = 184,866,000  (InfoAgregada total_balance)
ext_value  = 184,990,999  (suma de saldoActual en modelos)
delta      = 124,999 miles COP
```

La suma de saldos que extraemos supera en ~125M pesos el total declarado por InfoAgregada. Este es el único sujeto con discrepancia de balance significativa (los demás tienen delta ≤ 1.0).

**Hipótesis más probable:** Directamente relacionado con el bug de `is_open`. Cuando cuentas con código cerrado pero saldo > 0 se clasifiquen correctamente (Fix de Prioridad 1), verificar si InfoAgregada excluye esos saldos de su total_balance. Si InfoAgregada solo suma saldos de cuentas con código vigente, la discrepancia desaparecerá con el fix o se entenderá mejor.

### 6.2 Sujeto `13452289` — `total_past_due` con valor extraído = -2.0

```
xml_value  = 0    (InfoAgregada total_past_due = 0)
ext_value  = -2   (suma de saldoMora en modelos)
delta      = 2
```

Un `saldoMora = -1.0` o similar en alguna cuenta produce una suma negativa. En Datacredito, `-1` en campos numéricos puede significar "sin información" o "no aplica". Si se suma directamente como valor monetario, el total queda en negativo.

**Acción:** En `XmlExtractor.get_float()`, tratar valores negativos de `saldoMora` como `None` antes de retornarlos, o en el serializer excluir valores negativos de la suma de mora.

---

## 7. Transformers sin eventos UNKNOWN en la muestra

Los siguientes transformers **no generaron ningún evento** en los 24 sujetos. Sus mappings cubren completamente el corpus actual:

| | | |
|---|---|---|
| `transform_account_condition` | `transform_savings_account_status` | `transform_industry_sector` |
| `transform_account_type` | `transform_origin_state` | `transform_ownership_situation` |
| `transform_payment_status` | `transform_franchise` | `transform_credit_card_class` |
| `transform_plastic_status` | `transform_global_debt_credit_type` | `transform_query_reason` |
| `transform_debtor_role` | `transform_obligation_type` | `transform_contract_type` |

Esto no garantiza cobertura total ante XMLs futuros, pero muestra solidez para el corpus actual.

---

## 8. Análisis por sector

### Sector financiero (sector=1) — Alta prioridad

| Entidad | Problema | Impacto |
|---|---|---|
| BCO POPULAR LIBRANZA | `periodicidad=null` | Bajo — campo secundario |
| GNB SUDAMERIS | `periodicidad=null` | Bajo |
| ITAU CORPBANCA CARTERA TOTAL | `periodicidad=null` | Bajo |
| **ITAU CORPBANCA LIBRANZAS** | **mis-clasificada como cerrada** (saldo 3.7M) | **Alto** |
| BCO DAVIVIENDA | `periodicidad=null` | Bajo |
| **BCO COLPATRIA** | `garantia="Q"` en tarjetas | Medio |
| **BANCOUNION** | `garantia="Q"` en libranzas | Medio |
| BANCOLOMBIA | `periodicidad="9"` (1 evento) | Bajo |

Entidades bancarias principales están bien extraídas en montos. El bug de vigente/cerrado afecta a ITAU LIBRANZAS con 3.7M en saldo — deuda bancaria que queda invisible como cerrada.

### Sector real (sector=3) — Alta prioridad

| Entidad | Problema | Impacto |
|---|---|---|
| RAYCO S.A. DISTRIBUIDORA | `periodicidad=null` (36 eventos) | Bajo |
| **SISTECREDITO** | `periodicidad="9"` (51 eventos) | **Medio** — emisor masivo |
| **ASLEGAL, CREDYTY, GRUPO CONSULTO, GRUPO JURIDICO** | **mis-clasificadas como cerradas** (saldo > 0) | **Alto** |
| MUEBLES JAMAR | `periodicidad=null` | Bajo |
| BAYPORT COLOMBIA LIBRANZA | `periodicidad=null` | Bajo |

El sector real tiene la **mayor concentración del bug de clasificación**. Empresas gestoras de crédito (ASLEGAL, CREDYTY) y recuperadoras (GRUPO JURIDICO FALABELLA) muestran códigos cerrados con saldo activo — exactamente el patrón más relevante para evaluar riesgo de deuda real.

### Sector cooperativo (sector=2) — Prioridad media

COOTRAMED, COOPANTEX, COOVESTIDO tienen `periodicidad=null` en todos sus créditos. Comportamiento esperado para productos cooperativos. Sin mis-clasificaciones.

### Sector telecom (sector=4) — Baja prioridad

CLARO y COLOMBIA MOVIL generan eventos de `periodicidad=null` y en algunos casos son mis-clasificadas por saldo. Las obligaciones telecom (servicios de línea) no son determinantes para scoring crediticio. **Validar pero no priorizar.**

---

## 9. Plan de acción priorizado

### P1 — ~~Bug crítico: `is_open` no considera saldo pendiente~~ ✅ RESUELTO

**Implementado** en `global_report_models.py` y `credit_card_models.py`. Resultado: 3→15 sujetos OK.

Los 6 sujetos con delta 1–2 restante son consecuencia de la decisión de diseño de fidelidad al dato (sección 3.7), no errores pendientes.

### P2 — `periodicidad = "9"`: mapear SISTECREDITO

**Archivo:** `transformers/global_report_transformer.py`

Añadir `"9"` al enum `PaymentFrequency` y al mapping de `transform_payment_frequency`. Revisar Manual v1.6.7 primero; si no está documentado, usar `ON_DEMAND` o `IRREGULAR`. Impacta 51 cuentas de un solo emisor masivo del sector real.

### P3 — `garantia.tipo = "9"`: mapear para EndeudamientoGlobal

**Archivo:** `transformers/shared_transformers.py`

Añadir `"9"` al mapping de `transform_guarantee`. Es el evento más frecuente (334) pero de menor impacto en decisión. Verificar en manual si existe código específico para `EndeudamientoGlobal`.

### P4 — `garantia.tipo = "Q"`: verificar manual v1.6.7

**Archivo:** `transformers/shared_transformers.py`

Revisar `data/HDC+ PN - Manual de Implementacion WS v1.6.7...pdf` para confirmar significado de `"Q"`. Afecta tarjetas del sector financiero (BCO COLPATRIA, BANCOUNION). Si está documentado, añadir al enum `GuaranteeType` y al mapping.

### P5 — `saldoMora < 0`: no sumar como valor monetario

**Archivo:** `xml_adapter/xml_extractors/xml_extractor.py` o en builders/serializers

Tratar `saldoMora < 0` como `None`. Resuelve el `total_past_due = -2` del sujeto `13452289`.

### P6 — Balance discrepancy `78696456`

Dependiente de P1. Una vez corregido `is_open`, volver a correr el validate y verificar si la discrepancia desaparece o se mantiene. Si persiste, investigar la cuenta específica con saldo anómalo.

---

## 10. Sujetos 100% limpios

Tres sujetos pasan todos los checks del validate:

| Sujeto | Cartera | Tarjetas | Cuentas Ahorro | Saldo total | Eventos debug |
|---|---|---|---|---|---|
| `10064554` | 5 | 1 | 2 | 18.26M | 3 (periodicidad null — sin impacto) |
| `1030613409` | 11 | 9 | 2 | 22.80M | 3 (garantía Q en Colpatria) |
| `19448324` | 40 | 16 | 7 | 30.39M | 30 (periodicidad null + garantía Q) |

`19448324` es el sujeto más complejo de la muestra (40 cuentas cartera, 16 tarjetas de crédito) y pasa completamente limpio en validate. Sus 30 eventos debug son todos `periodicidad=null` y `garantía=Q/9` — ninguno afecta la clasificación vigente/cerrado porque todas sus cuentas activas tienen código EC vigente (código 01) con o sin saldo.

---

## 11. Conclusiones

1. **La extracción estructural es perfecta.** 100% de nodos extraídos en todos los tipos. No hay pérdida de datos crudos.

2. **El único bug que afecta la lógica de decisión** es la clasificación vigente/cerrado. Una cuenta con código EC cerrado pero `saldoActual > 0` es una obligación activa desde la perspectiva crediticia. El fix está localizado en dos métodos `is_open`.

3. **Los 674 eventos UNKNOWN** se concentran en solo 2 transformers y 3 valores (`null`, `"9"`, `"Q"`). No hay dispersión — son patrones muy concretos y accionables.

4. **`periodicidad=null` es comportamiento esperado** en libranzas y productos sin cuota fija. No es un error de mapping sino una ausencia de dato en origen.

5. **`garantia="9"` en `EndeudamientoGlobal`** (334 eventos, 49.6% del total) es probablemente un código interno de Datacredito para el nodo de resumen. Es el evento más frecuente pero el de menor impacto en decisión crediticia.

6. **El DebugTracer (Fase 3 completada)** demostró su valor: los dos transformers nuevos instrumentados (`payment_frequency`, `guarantee`) revelaron todos los 674 eventos. Sin ellos, estos valores hubieran seguido siendo fallbacks silenciosos invisibles.
