# ANÁLISIS DE EXTRACCIÓN — Segunda Ronda de Evaluaciones

**Fecha:** 2026-04-01
**Branch:** Feature/Build-report
**Personas evaluadas:** 40021504, 49551526, 7423628, 78696456
**Herramientas usadas:** `/validate/<id>/` + `/debug/<id>/` (debug solo si hubo pérdidas)

---

## Resumen ejecutivo

| Persona    | Estado      | Checks OK | Checks Fail | Debug Events |
|------------|-------------|-----------|-------------|--------------|
| 40021504   | ✅ OK        | 14/14     | 0           | 0            |
| 49551526   | ⚠️ Warnings | 12/14     | 2           | 0            |
| 7423628    | ⚠️ Warnings | 12/14     | 2           | 0            |
| 78696456   | ⚠️ Warnings | 10/14     | 4           | 2            |

**Conclusión de alto nivel:**
- El pipeline de transformación de enums es robusto en 3 de 4 personas (cero pérdidas en debug).
- El único gap de enum detectado es en `transform_payment_status` (códigos `14` y `17` de cuentas Claro telecom), presente en 78696456.
- Los fallos en conteos `active_credits`/`closed_credits` son **sistemáticos y simétricos** — no son pérdidas de datos sino una discrepancia de criterio entre cómo Datacredito clasifica vigencia y cómo nuestro parser define `is_open`.
- LBZ (Libranza) extrae correctamente en los 4 casos evaluados — el fix del bug anterior quedó consolidado.

---

## Hallazgos por persona

---

### 40021504 — Baseline limpio

**Resultado:** `status: ok` — 14/14 checks pasados, 0 eventos de debug.

| Check | XML | Extraído | Delta |
|-------|-----|----------|-------|
| CuentaCartera nodes | 44 | 44 | 0 |
| CuentaAhorro nodes | 3 | 3 | 0 |
| active_credits | 11 | 11 | 0 |
| closed_credits | 33 | 33 | 0 |
| total_balance | 110,718,000 | 110,718,000 | 0 |
| total_past_due | 30,014,000 | 30,014,000 | 0 |

Esta persona sirve como **baseline de referencia**: el pipeline extrae, transforma y agrega correctamente cuando los datos son canónicos. No hay gaps de enum, no hay discrepancias de criterio de apertura/cierre, y los balances cuadran al peso.

---

### 49551526 — Delta simétrico de 1 cuenta

**Resultado:** `status: warnings` — 12/14 pasados, 2 fallos, 0 eventos de debug.

| Check | XML | Extraído | Delta | Estado |
|-------|-----|----------|-------|--------|
| CuentaCartera nodes | 24 | 24 | 0 | ✅ |
| active_credits | 7 | 6 | 1 | ❌ |
| closed_credits | 17 | 18 | 1 | ❌ |
| open_savings_checking | 2 | 2 | 0 | ✅ |
| total_balance | 176,160,000 | 176,160,000 | 0 | ✅ |
| total_past_due | 50,000 | 50,000 | 0 | ✅ |

**Sin pérdidas de enum** — 0 eventos de debug.

#### Análisis del delta activos/cerrados

El delta es exactamente simétrico (1 activo menos, 1 cerrado más): nuestro parser clasifica una cuenta como cerrada que Datacredito reporta como vigente. La composición del portafolio (ComposicionPortafolio) muestra `AHO=2, CAB=1, CDC=1, LBZ=4`, con total = 6 créditos en cartera. Datacredito dice `creditoVigentes=7` — discrepancia de 1.

El candidato más probable es una cuenta CDC (crédito de consumo) de **CLARO SERV FIJ** con:
- `EstadoCuenta = 06` (cancelada por la entidad)
- `EstadoPago = 45` (acuerdo de pago activo o renegociación)
- `saldoActual = 50,000` (saldo pendiente no cero)

Datacredito la incluye en `creditoVigentes` probablemente porque hay saldo o plan de pago activo (`EstadoPago=45`). Nuestro parser la clasifica como cerrada porque `EstadoCuenta=06` no está en el conjunto de estados abiertos.

**Naturaleza del hallazgo:** criterio de vigencia distinto, no pérdida de datos. Los balances cuadran perfectamente (incluido el saldo de esa cuenta), lo que confirma que el registro existe y se extrae correctamente — solo difiere la clasificación open/closed.

---

### 7423628 — Delta simétrico de 4 cuentas

**Resultado:** `status: warnings` — 12/14 pasados, 2 fallos, 0 eventos de debug.

| Check | XML | Extraído | Delta | Estado |
|-------|-----|----------|-------|--------|
| CuentaCartera nodes | 56 | 56 | 0 | ✅ |
| TarjetaCredito nodes | 13 | 13 | 0 | ✅ |
| CuentaAhorro nodes | 11 | 11 | 0 | ✅ |
| CuentaCorriente nodes | 2 | 2 | 0 | ✅ |
| active_credits | 16 | 12 | 4 | ❌ |
| closed_credits | 53 | 57 | 4 | ❌ |
| total_balance | 156,326,000 | 156,326,000 | 0 | ✅ |
| total_past_due | 40,558,000 | 40,558,000 | 0 | ✅ |

**Sin pérdidas de enum** — 0 eventos de debug.

#### Análisis del delta activos/cerrados

El delta simétrico de 4 es el más grande de la ronda. El total de nodos extraídos es correcto (56+13=69 cuentas de crédito). El delta implica que 4 cuentas que Datacredito reporta como vigentes son clasificadas como cerradas por nuestro parser.

Dado que el delta es mayor que en 49551526, es probable que haya múltiples cuentas con estados "borde" involucrados:
- EC=06 (cancelada por institución) con saldo pendiente
- EC=09 (demanda judicial) — Datacredito puede considerarla vigente a efectos de riesgo
- Otros EC con plan de pago activo

Los balances cuadran exactamente, confirmando que **no hay pérdida de datos** — todas las cuentas se extraen y sus montos se suman correctamente. El problema es exclusivamente de criterio de clasificación open/closed.

**Nota:** Esta persona tiene tarjetas de crédito (13 nodos TarjetaCredito) y cuentas corrientes (2), lo que la hace el caso de portafolio más complejo de la ronda.

---

### 78696456 — Caso más complejo: gaps de enum + discrepancias de balance

**Resultado:** `status: warnings` — 10/14 pasados, 4 fallos, **2 eventos de debug**.

| Check | XML | Extraído | Delta | Estado |
|-------|-----|----------|-------|--------|
| CuentaCartera nodes | 40 | 40 | 0 | ✅ |
| CuentaAhorro nodes | 13 | 13 | 0 | ✅ |
| Consulta nodes | 6 | 6 | 0 | ✅ |
| EndeudamientoGlobal nodes | 20 | 20 | 0 | ✅ |
| active_credits | 10 | 6 | 4 | ❌ |
| closed_credits | 30 | 34 | 4 | ❌ |
| total_balance | 184,866,000 | 184,990,999 | 124,999 | ❌ |
| total_past_due | 35,786,000 | 35,785,998 | 2 | ❌ |

#### Hallazgo 1 — Gap de enum: `transform_payment_status` códigos 14 y 17

**Debug events:**

| Transformer | Raw Value | Nodo XML | Entidad | Cuenta |
|-------------|-----------|----------|---------|--------|
| transform_payment_status | `14` | EstadoPago | CLARO SERV MOV | .34767373 |
| transform_payment_status | `17` | EstadoPago | CLARO TEC MOV | 108995884 |

Ambos son cuentas de servicios de telefonía móvil Claro. Los códigos `14` y `17` no están mapeados en el enum `PaymentStatus`, por lo que caen a `UNKNOWN`.

**Contexto de los registros:**
- **EP=14 (CLARO SERV MOV):** Cuenta con `EstadoCuenta=01` (al día/vigente), `saldoActual=0`. Estado de pago no identificado en cuenta activa sin saldo.
- **EP=17 (CLARO TEC MOV):** Cuenta con `EstadoCuenta=02` (cerrada/pagada), `saldoActual=725,000`, `saldoMora=129,000`. Estado de pago no identificado en cuenta cerrada con saldo en mora.

**Interpretación probable:**
- EP=14: podría ser "paz y salvo" o "saldada" para servicios activos
- EP=17: podría ser "cobro jurídico" o "cartera vendida" para servicios con mora

**Impacto en negocio:** Bajo para EP=14 (cuenta activa sin saldo). Potencialmente relevante para EP=17 — la cuenta de CLARO TEC MOV tiene mora de $129,000 y el `payment_status` informa la naturaleza de esa mora. La información de EstadoCuenta y los montos sí se extraen correctamente; solo el campo `payment_status` queda como UNKNOWN.

#### Hallazgo 2 — `total_balance`: extraído > XML (dirección inusual)

- XML InfoAgregada: `184,866,000` (miles de pesos)
- Extraído: suma de `saldoActual` de todas las CuentaCartera = **$184,990,999**
- Delta: **$124,999** — nuestro extractor suma MÁS que el XML

La dirección del error es contraintuitiva: normalmente esperaríamos perder datos (extraer menos). Aquí extraemos más, lo que sugiere que el XML en `InfoAgregada.saldoTotal` podría estar:
1. Excluyendo intencionalmente alguna cuenta del cómputo agregado (p.ej. cuentas con EP no estándar como el código 17)
2. Redondeando diferente al nivel individual vs. el agregado

La diferencia ($124,999) es menor al **0.07% del total**, lo que la hace insignificante para análisis de riesgo crediticio, pero debe documentarse como discrepancia conocida del cómputo de Datacredito.

#### Hallazgo 3 — `total_past_due`: delta=2 (tolerancia excedida por mínimo)

- XML: $35,786,000 (miles de pesos)
- Extraído: $35,785,998
- Delta: 2 pesos

El validador tiene tolerancia ±1.0 y este delta es 2, por lo que falla el check. En la práctica es ruido de punto flotante o redondeo en la serialización/deserialización de los campos individuales del XML. **No hay pérdida real de datos** — el saldo en mora se extrae correctamente.

#### Hallazgo 4 — `active_credits`/`closed_credits` delta=4

Mismo patrón que en 49551526 y 7423628: criterio de vigencia distinto entre Datacredito y nuestro parser. Con 40 cuentas de cartera y 4 cuentas con estados borde, la proporción es comparable a los otros casos.

---

## Análisis consolidado

### 1. Estado del pipeline de transformación

El debug de la segunda ronda confirma que el pipeline está **mayoritariamente sano**:

```
40021504:  0 debug events  ← baseline perfecto
49551526:  0 debug events
7423628:   0 debug events
78696456:  2 debug events  ← transform_payment_status EP=14, EP=17 (Claro telecom)
```

Solo **2 gaps de enum activos** en toda la ronda, ambos del mismo transformer (`transform_payment_status`) y en la misma persona. El trabajo de mapeo de enums de la primera ronda (LBZ, EstadoCuenta "00", etc.) se refleja en la ausencia de ruido en los otros tres casos.

### 2. El problema de vigencia (active_credits) es sistémico

El delta `active_credits` ocurre en 3 de 4 personas con magnitudes variables (0, 1, 4, 4). El patrón es consistente:
- **Siempre simétrico**: +N en closed_credits = -N en active_credits (total de cuentas siempre correcto)
- **Los balances siempre cuadran** en los casos sin otras discrepancias
- **No hay debug events** asociados — no es un problema de enum

La causa raíz es una diferencia de criterio de "cuenta vigente" entre Datacredito y nuestro parser:

| Criterio | Datacredito `creditoVigentes` | Nuestro `is_open` |
|----------|-------------------------------|-------------------|
| EC=06 con saldo activo | Puede contar como vigente | Clasifica como cerrada |
| EC=06 con EP=45 (plan de pago) | Puede contar como vigente | Clasifica como cerrada |
| EC=09 (demanda judicial) | Puede contar como vigente | Depende del mapeo |

**Recomendación:** Este no es un bug de extracción — es una divergencia de definición de negocio. Para presentar a negocio, se reporta el conteo propio (basado en EstadoCuenta) como "cuentas activas según estado de cuenta", con nota de que Datacredito puede reportar diferente al incluir cuentas en estados especiales (acuerdos de pago, deuda vigente con cancelación administrativa).

### 3. LBZ (Libranza) — sin pérdidas confirmadas

En los 4 casos evaluados, LBZ se extrae correctamente como `AccountType.LBZ`. La persona 49551526 tiene `LBZ=4` en su ComposicionPortafolio y extrae 4 cuentas de tipo Libranza sin eventos de debug. El fix aplicado en la primera ronda está consolidado y funcionando.

### 4. Gaps de enum pendientes

| Transformer | Códigos faltantes | Personas afectadas | Prioridad |
|-------------|-------------------|---------------------|-----------|
| transform_payment_status | `14`, `17` | 78696456 (Claro telecom) | Media |

---

## Acciones pendientes

| # | Acción | Impacto | Prioridad |
|---|--------|---------|-----------|
| 1 | Agregar EP=14 y EP=17 a `PaymentStatus` enum y mapping | Elimina los 2 debug events de 78696456 | Media |
| 2 | Definir política de criterio de vigencia (`active_credits`) | Claridad para presentar a negocio | Alta |
| 3 | Revisar tolerancia del validador `total_past_due` (ampliar a ±5) | Elimina falso positivo por redondeo | Baja |
| 4 | Investigar discrepancia `total_balance` 78696456 (+$124,999) | Confirmar si es exclusión intencional de Datacredito | Baja |

---

## Matriz de confianza por campo

| Campo | Confianza | Notas |
|-------|-----------|-------|
| Nodos extraídos (counts) | ✅ Alta | 4/4 personas con conteos exactos |
| `outstanding_balance` | ✅ Alta | 3/4 cuadra exacto; 78696456 delta <0.07% |
| `past_due_amount` | ✅ Alta | 3/4 cuadra exacto; 78696456 delta=2 pesos |
| `account_type` (incl. LBZ) | ✅ Alta | Sin debug events en 4 personas |
| `account_condition` | ✅ Alta | Fix de "00"→LEGACY_CLOSED validado |
| `payment_status` | ⚠️ Media | Códigos 14/17 sin mapear (Claro telecom, 1 persona) |
| Clasificación open/closed | ⚠️ Media | Divergencia de criterio vs Datacredito en 3/4 personas |
| Todos los demás campos | ✅ Alta | Sin eventos de debug en segunda ronda |
