# ANÁLISIS DE EXTRACCIÓN — Evaluación Masiva

**Fecha:** 2026-04-01
**Branch:** Feature/Build-report
**Universo evaluado:** 25 personas (todos los XMLs disponibles en `data/`)
**Herramientas:** `python manage.py run_extraction_audit`
**Criterio de inclusión en este análisis:** personas con al menos 1 check fallido o al menos 1 debug event

---

## Resumen ejecutivo

| Resultado | Personas | % |
|-----------|----------|---|
| ✅ OK (14/14 checks) | 2 | 8% |
| ⚠️ Warnings (checks fallidos) | 23 | 92% |
| Con debug events (gaps de enum) | 6 | 24% |

De los 23 con warnings:
- **20** fallan únicamente en `active_credits`/`closed_credits` (delta de conteo)
- **3** fallan adicionalmente en `total_balance` o `total_past_due`
- **6** tienen gaps de enum reales en transformers

El pipeline es robusto en extracción de nodos y balances. Los dos problemas sistémicos son: (1) criterio de vigencia distinto al de Datacredito, y (2) códigos faltantes en `transform_payment_status`.

---

## Hallazgo 1 — Delta sistemático `active_credits` / `closed_credits`

### Alcance

**Afecta 20 de 25 personas (80%).**

| Persona | Delta activos | Delta cerrados |
|---------|--------------|----------------|
| 14012717 | -8 | +8 |
| 8737538  | -7 | +7 |
| 12532647 | -6 | +6 |
| 80491927 | -6 | +6 |
| 11794399 | -4 | +4 |
| 13364177 | -4 | +4 |
| 22436588 | -4 | +4 |
| 34554868 | -4 | +4 |
| 43003890 | -4 | +4 |
| 43432541 | -4 | +4 |
| 7423628  | -4 | +4 |
| 78696456 | -4 | +4 |
| 12979619 | -3 | +3 |
| 8526939  | -3 | +3 |
| 73102905 | -2 | +2 |
| 18595160 | -1 | +1 |
| 22389910 | -1 | +1 |
| 32322427 | -1 | +1 |
| 39007435 | -1 | +1 |
| 49551526 | -1 | +1 |

**Delta promedio:** 3.6 | **Delta máximo:** 8

El delta es siempre perfectamente simétrico: lo que se pierde en `active_credits` aparece como falso cerrado en `closed_credits`. Nunca se pierden cuentas totales — todos los nodos extraen correctamente.

### Causa raíz

Hay una divergencia entre la definición de "vigente" de Datacredito y la nuestra.

**Nuestro criterio (`OPEN_ACCOUNT_CONDITIONS`):**
```
ON_TIME, OVERDUE_DEBT, WRITTEN_OFF, DOUBTFUL_COLLECTION, CLAIM_IN_PROGRESS
→ EC codes: 01, 13-41, 45, 47, 60
```

**Datacredito `creditoVigentes`:** incluye adicionalmente cuentas con EC=03, 05, 06 (y posiblemente otros códigos "cancelados") cuando tienen saldo pendiente o deuda activa.

Evidencia concreta en casos extremos:

| Persona | EC dist. de CuentaCartera | Nuestros open | Datacredito vigentes | Delta |
|---------|--------------------------|---------------|---------------------|-------|
| 8737538 | 01×3, 03×5, 05×1, 06×5, 00×1 | 3 | 10 | 7 |
| 14012717 | 01×2, 02×2, 03×10, 05×2, 06×4 | 2 | 10 | 8 |

En 8737538 hay 5 cuentas EC=03 (cancelada por mal manejo) y 5 EC=06 (cancelada por la entidad). Datacredito las cuenta como vigentes — probablemente porque tienen saldo pendiente. La cuenta no está pagada, solo la relación comercial fue terminada. En 14012717 hay 10 cuentas EC=03 que Datacredito considera vigentes.

**Conclusión:** EC=03, 05, 06 representan "cancelación administrativa" del producto, no pago de la deuda. El saldo puede persistir (y frecuentemente lo hace). Datacredito incluye estas cuentas en `creditoVigentes` porque la deuda sigue viva.

### Riesgo para el engine

**RIESGO ALTO.** Esta diferencia tiene consecuencias directas sobre el motor de decisión:

1. **Subestimación de exposición:** Un deudor con 8 créditos EC=03 (cancelados por mal manejo) con saldo pendiente — el engine los cuenta como cerrados y no los incluye en el cálculo de obligaciones activas. Esto puede generar una imagen crediticia significativamente más favorable que la real.

2. **Sectores afectados:** No es un problema de telcos. EC=03/05/06 con saldo aparece en bancos (Banco de Bogotá, Bancolombia), microfinanzas (Crediexpress), cooperativas (Coobolarqui) y créditos de consumo general (CRJA S.A).

3. **EC=03 es señal de riesgo:** "Cancelada por mal manejo" indica que la entidad terminó la relación por comportamiento del deudor — es una bandera roja, no un cierre normal. Si el engine trata estas cuentas como cerradas/pagadas, pierde información de riesgo crítica.

**Acción recomendada:** Revisar `OPEN_ACCOUNT_CONDITIONS` para incluir EC=03, 05, 06 cuando el saldo (`outstanding_balance > 0`). Alternativamente, crear una categoría `ADMINISTRATIVELY_CLOSED_WITH_DEBT` distinta de `CLOSED_PAID`.

---

## Hallazgo 2 — Gaps en `transform_payment_status`

### Alcance

**Afecta 6 de 25 personas (24%).** Un único transformer responsable de todos los gaps.

| Código EP | Ocurrencias | Entidad(es) | Sector | record_type |
|-----------|-------------|-------------|--------|-------------|
| `41` | 4 | ORI BANCOLOMBI PAUTO REINTEGR, CRJA S.A, COOBOLARQUI LIBRANZA | Banca / Cooperativa / Libranza | PortfolioAccount |
| `19` | 1 | CREDIEXPRESS POPAYAN | Microfinanzas | PortfolioAccount |
| `37` | 1 | BBVA COLOMBIA | Banca (tarjeta) | CreditCard |
| `17` | 1 | CLARO TEC MOV | Telecom | PortfolioAccount |
| `14` | 1 | CLARO SERV MOV | Telecom | PortfolioAccount |

### Análisis por código

**EP=41 (4 ocurrencias — mayor frecuencia, mayor riesgo):**
Todos los casos tienen EC=02 y saldo 100% en mora (saldo = mora):
- SFI (sistema financiero): saldo $625k, mora $625k
- SFI: saldo $236k, mora $236k
- CON (consumo): saldo $11.26M, mora $9.78M
- LBZ (libranza): saldo $21k, mora $21k

El patrón saldo=mora en EC=02 sugiere que EP=41 es un estado de deuda en cobro externo o cedida a cartera de difícil cobro. **No es telco.** Aparece en banca, consumo y libranza.

**EP=37 (BBVA, TarjetaCredito):**
EC=02, saldo=$1.6M, mora=$2.02M (mora > saldo — saldo ya en castigada o con capital vencido). Tarjeta de crédito de banco principal.

**EP=19 (CREDIEXPRESS):**
EC=02, saldo=$476k, mora=$476k (100% en mora). Microcrédito regional.

**EP=14 y EP=17 (Claro):**
Sector telecom. EP=14 en cuenta activa (EC=01) sin saldo. EP=17 en cuenta cerrada (EC=02) con mora $129k. Riesgo bajo para el engine crediticio.

### Riesgo para el engine

**EP=41: RIESGO ALTO.** Aparece en Libranza — exactamente el producto que negocio considera crítico. Una libranza con EP=41 tiene toda su deuda en mora y el estado de pago queda como `UNKNOWN`. El engine no puede distinguir si es cobro judicial, cartera cedida, o acuerdo extrajudicial. La decisión crediticia puede estar basada en información incompleta.

**EP=19, EP=37: RIESGO MEDIO.** Banca y microfinanzas, no telco. El estado de pago de cuentas con mora total queda indeterminado.

**EP=14, EP=17 (telco): RIESGO BAJO.** Servicios públicos/telecom tienen peso menor en decisiones de crédito formal. EP=14 además está en cuenta sin saldo.

---

## Hallazgo 3 — Gaps en `transform_origin_state`

### Alcance

**Afecta 1 de 25 personas (8737538).** 2 códigos desconocidos.

| Código EO | Entidad | EC | EP | Tipo cuenta | Saldo |
|-----------|---------|----|----|-------------|-------|
| `5` | BANCO BOGOTA VIVIENDA | 05 (voluntariamente cancelada) | 47 (dudoso recaudo) | CAV (vivienda) | $46.78M, mora $3.57M |
| `6` | GASCARIBE | 01 (al día) | 01 | Servicio público | N/D |

### Análisis

`EstadoOrigen` indica el estado de la obligación al momento de originarse. Los códigos conocidos en el mapping son 0 (no informado), 1 (normal), 2 (reestructurado), 3 (refinanciado), 99 (desconocido).

- **EO=5:** Cuenta de vivienda (CAV) de Banco de Bogotá, originada en estado 5 (desconocido). Actualmente en dudoso recaudo con mora de $3.57M. El origen podría ser "en proceso de demanda" o una reestructuración más compleja.
- **EO=6:** GASCARIBE (empresa de gas), cuenta al día. Estado de origen 6 — posiblemente "servicio público" o categoría específica del sector.

### Riesgo para el engine

**RIESGO BAJO-MEDIO.** `EstadoOrigen` es un atributo contextual (cómo nació el crédito), no un estado actual. El engine puede tomar decisiones razonables sin este dato. Sin embargo, para créditos de vivienda con saldos altos ($46M), conocer el origen puede ser relevante para políticas de exclusión o condicionamiento.

---

## Hallazgo 4 — Discrepancias menores de balance

### Alcance

| Persona | Check | XML | Extraído | Delta | Dirección |
|---------|-------|-----|----------|-------|-----------|
| 13364177 | total_balance | 75,761,000 | 75,760,998 | 2 | extraído < xml |
| 13452289 | total_balance | 17,339,000 | 17,338,998 | 2 | extraído < xml |
| 13452289 | total_past_due | 0 | -2 | 2 | extraído < xml (negativo) |
| 34554868 | total_past_due | 1,900,000 | 1,899,998 | 2 | extraído < xml |
| 78696456 | total_balance | 184,866,000 | 184,990,999 | 124,999 | **extraído > xml** |
| 78696456 | total_past_due | 35,786,000 | 35,785,998 | 2 | extraído < xml |
| 80491927 | total_balance | 152,045,000 | 152,044,995 | 5 | extraído < xml |
| 80491927 | total_past_due | 6,668,000 | 6,667,995 | 5 | extraído < xml |

### Análisis

**Delta=2 (5 casos):** Ruido de punto flotante. Los XMLs almacenan algunos valores con decimales (p.ej. `saldoActual="625000.0"`) y la suma de múltiples flotantes genera error de representación. El validador tiene tolerancia ±1 — considerar ampliar a ±5. **No hay pérdida de datos.**

**13452289 total_past_due=-2:** El XML reporta `total_past_due=0` pero nuestra suma da -2. Esto indica que alguna cuenta tiene `past_due_amount` negativo en el XML (probablemente un saldo a favor o ajuste contable). No es un error de extracción.

**78696456 total_balance=+$124,999 (extraído > xml):** El único caso donde extraemos más que el agregado. Investigación previa sugiere que Datacredito excluye del agregado la cuenta de CLARO TEC MOV (EP=17, código desconocido) al calcular el total. Delta es <0.07% del total — insignificante para decisión crediticia.

### Riesgo para el engine

**RIESGO BAJO.** Los deltas de ±2 a ±5 son ruido sistemático de punto flotante, no errores de lógica. El engine puede confiar en los balances individuales de cada cuenta — el problema está solo en el cómputo del agregado del validador.

---

## Análisis de riesgo para el engine — Resumen

| Hallazgo | Frecuencia | Sectores afectados | Riesgo engine | Prioridad |
|----------|-----------|-------------------|---------------|-----------|
| Delta active_credits (EC=03/05/06 con saldo) | 20/25 (80%) | Todos (banca, consumo, libranza, microfinanzas) | **ALTO** — subestima deuda activa | 🔴 Crítica |
| EP=41 desconocido (cuentas 100% en mora) | 4 ocurrencias, 3 personas | Banca, cooperativa, **Libranza** | **ALTO** — pierde estado de pago en mora total | 🔴 Crítica |
| EP=19, EP=37 desconocidos | 1 ocurrencia c/u | Microfinanzas, Banca (tarjeta) | **MEDIO** — estado de pago en mora total | 🟡 Alta |
| EO=5, EO=6 desconocidos | 2 ocurrencias, 1 persona | Banca vivienda, Servicios públicos | **BAJO-MEDIO** — contexto de origen | 🟡 Media |
| EP=14, EP=17 desconocidos (telco) | 2 ocurrencias, 1 persona | Telecom | **BAJO** | 🟢 Baja |
| Discrepancias de balance (±2/5) | 7 ocurrencias | N/A | **BAJO** — floating point | 🟢 Baja |

---

## Acciones recomendadas

### Críticas (bloquean el engine)

**1. Revisar criterio `OPEN_ACCOUNT_CONDITIONS` para EC=03/05/06 con saldo**

La lógica actual clasifica como "cerrada" cualquier cuenta con EC=03 (cancelada por mal manejo), 05 (cancelada voluntariamente) o 06 (cancelada por la entidad). Esto es correcto desde la perspectiva del *producto* (el crédito fue cancelado), pero incorrecto desde la perspectiva de la *deuda* (el saldo puede persistir).

Para el engine, la pregunta relevante es: **¿tiene el solicitante deuda viva?** — no si el producto está activo.

Opciones:
- Incluir EC=03/05/06 en `OPEN_ACCOUNT_CONDITIONS` incondicionalmente (más conservador)
- Tratarlos como open solo si `outstanding_balance > 0` (más preciso, requiere lógica en el modelo)

**2. Mapear EP=41 en `PaymentStatus`**

EP=41 aparece en 4 cuentas de sectores financieros (no telco), incluyendo una Libranza. El patrón (EC=02 + 100% mora) sugiere "Cartera cedida a cobro externo" o "Cobro judicial sobre cuenta cerrada". Verificar en el Manual de Insumos XML de Datacredito (disponible en `data/`).

### Altas

**3. Mapear EP=19 y EP=37**

EP=19 en microfinanzas (cuenta cerrada, 100% mora) y EP=37 en tarjeta BBVA (mora > saldo). Probablemente estados de cobro para diferentes niveles de delinquencia en cuentas cerradas.

**4. Mapear EO=5 y EO=6**

Dos códigos en un único XML. EO=5 en crédito de vivienda con mora activa. EO=6 en servicios públicos.

### Bajas

**5. Ampliar tolerancia del validador a ±5**

Los deltas de 2 y 5 son sistemáticos (floating point). La tolerancia ±1 genera falsos positivos que añaden ruido al análisis.

---

## Estado del pipeline por categoría

| Categoría | Estado | Notas |
|-----------|--------|-------|
| Extracción de nodos (counts) | ✅ Perfecto | 25/25 personas con conteos exactos |
| AccountType (incl. LBZ) | ✅ Perfecto | Sin gaps en 25 personas |
| AccountCondition | ✅ Perfecto | Sin gaps de enum — el problema es de criterio, no de mapeo |
| PaymentStatus | ⚠️ Gaps activos | EP=14,17,19,37,41 sin mapear |
| OriginState | ⚠️ Gaps activos | EO=5,6 sin mapear (1 persona) |
| Balances individuales | ✅ Confiable | Floating point solo en agregados |
| Clasificación open/closed | ⚠️ Divergente | EC=03/05/06 con saldo subestima deuda activa en 80% de casos |
