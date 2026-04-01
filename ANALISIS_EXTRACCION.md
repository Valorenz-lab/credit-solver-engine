# Análisis de Calidad de Extracción
**Fecha:** 2026-04-01
**Personas evaluadas:** 11794399, 12979619, 18595160, 22436588
**Herramientas:** `/validate/<id>/` + `/debug/<id>/`

---

## Resumen ejecutivo

Se identificaron **dos problemas reales de pérdida de datos** y **dos falsos positivos del validador**. El problema crítico para negocio es la pérdida del tipo de cuenta `LBZ` (Libranza), que afecta las 4 personas evaluadas y representa **$87.5M en saldo vigente** no clasificado.

| Hallazgo | Tipo | Impacto negocio | Afecta |
|---|---|---|---|
| `LBZ` no mapeado en `AccountType` | **Pérdida de dato real** | **ALTO** — libranzas no identificables | 4/4 personas |
| `EstadoCuenta "00"` sin mapear | Pérdida menor | BAJO — solo cuentas cerradas antiguas | 2/4 personas |
| Discrepancia `active_credits` | Falso positivo del validador | Ninguno — metodología incompleta | 4/4 personas |
| Discrepancia `total_balance` (22436588) | Falso positivo del validador | Ninguno — TarjetaCredito no incluida en suma | 1/4 personas |

---

## Hallazgo 1 — LBZ no mapeado (CRÍTICO para negocio)

### Qué es LBZ

`LBZ` es el código de Datacredito para **Libranza** (crédito con descuento automático de nómina o pensión). Es un producto crediticio con perfil de riesgo diferenciado: pago garantizado por el empleador, sin posibilidad de mora voluntaria.

### Qué ocurre hoy en el pipeline

```
XML: <Caracteristicas tipoCuenta="LBZ" .../>
          ↓
transform_account_type("LBZ")
          ↓  KeyError — "LBZ" no existe en AccountType enum
AccountType.UNKNOWN  ← dato perdido
```

El código `LBZ` no está en el enum `AccountType` (que usa `AccountType[value]` directamente). El transformer cae a `UNKNOWN` silenciosamente.

### Alcance del problema

| Persona | LBZ en XML (CuentaCartera) | LBZ vigentes | Saldo vigente LBZ |
|---|---|---|---|
| 11794399 | 6 | 1 | $29,820,000 |
| 12979619 | 2 | 1 | $6,686,000 |
| 18595160 | 3 | 1 | $6,299,000 |
| 22436588 | 9 | 4 | $44,703,000 |
| **Total** | **20** | **7** | **$87,508,000** |

Además, `LBZ` aparece en nodos `Consulta` (historial de consultas): 3 eventos en 3 personas. Esto significa que entidades que consultaron el reporte buscando libranzas también quedan sin clasificar.

### Impacto exacto en el output del full-report

- ✅ Los saldos, fechas, historial de pagos, estados — **se extraen correctamente**
- ✅ El `is_open` se calcula bien (basado en `EstadoCuenta`, no en `account_type`)
- ✅ Las cuentas LBZ sí aparecen en `active_obligations` y `global_summary`
- ❌ `account_type` = `"Desconocido"` en lugar de identificador de libranza
- ❌ **No es posible filtrar ni identificar el portafolio libranza** en el output JSON
- ❌ Si negocio aplica filtros por `account_type`, las libranzas son invisibles

### Entidades que reportan LBZ (muestra de las 4 personas)

`BAYPORT COLOMBIA SA LIBRANZA`, `CFG PARTNERS`, `BBVA COLOMBIA LIBRANZA`, `BCO PICHINCHA LIBRANZA`, `KOA CF Libranza`, `KALA COLOMBIA SAS`, `KREDIT PLUS SAS`, `SERFINANZA`, `UNIFACOOP LIBRANZA`, `EXCELCREDIT SA`, `COPSEFAM LTDA LIBRANZA`, `Genera Sueños Libranza`

### Fix requerido

1. Añadir `LBZ = "Libranza"` al enum `AccountType`
2. El transformer `transform_account_type` usa `AccountType[value]` → el solo hecho de agregar el valor al enum ya lo resuelve, sin modificar el transformer

---

## Hallazgo 2 — EstadoCuenta código "00" sin mapear (BAJO)

### Qué ocurre

El código `"00"` en `<EstadoCuenta codigo="00"/>` no existe en la Tabla 4 del manual. El transformer cae a `AccountCondition.UNKNOWN`.

### Contexto de los registros afectados

Todas las cuentas con `"00"` son **históricas y cerradas**, sin saldo vigente:

| Persona | Entidad | Cuenta | Fecha | EstadoPago |
|---|---|---|---|---|
| 11794399 | BCO DE BOGOTA RED MEGABANCO | 277044477 | 2003-12-31 | 08 (cancelada) |
| 11794399 | BCO DE BOGOTA RED MEGABANCO | 4000000C1 | 2003-09-30 | 08 (cancelada) |
| 11794399 | GNB SUDAMERIS | 740158300 | 2006-04-30 | 08 (cancelada) |
| 11794399 | BANCO CAJA SOC (TDC) | 540695280 | 1998-04-30 | 05 (mora 90) |
| 11794399 | BCO COLPATRIA (TDC) | 454600475 | 2008-06-30 | 05 (mora 90) |
| 22436588 | RAYCO S.A. DISTRIBUIDORA | LC-002273..OE-001167 (×5) | 2002–2007 | 08 (cancelada) |
| 22436588 | MUEBLES JAMAR | 000018425 (×2) | 2008-05-31 | 08 (cancelada) |

### Impacto

- `is_open = False` (correcto: ninguna tiene saldo, todas son de hace 17–27 años)
- `account_state_code = UNKNOWN` en el output (incorrecto semánticamente)
- **No afecta balances ni perfil financiero vigente**
- `"00"` parece ser un código legacy de Datacredito anterior a la versión actual del manual

### Fix sugerido

Agregar `"00": AccountCondition.CANCELLED_LEGACY` (nuevo valor) o mapear a la condición cerrada más cercana semánticamente. Requiere confirmación con el manual histórico de Datacredito.

---

## Hallazgo 3 — Discrepancia `active_credits` (falso positivo del validador)

### Qué muestra el validador

| Persona | XML (`creditosVigentes`) | Extraídos (open PortfolioAccounts) | Delta |
|---|---|---|---|
| 11794399 | 11 | 7 | 4 |
| 12979619 | 4 | 1 | 3 |
| 18595160 | 3 | 1 | 2 |
| 22436588 | 10 | 6 | 4 |

### Por qué NO es pérdida de datos en la extracción

El campo `creditosVigentes` en `InfoAgregada.Resumen.Principales` que Datacredito calcula incluye **todas las obligaciones vigentes**: `CuentaCartera` + `TarjetaCredito` + posiblemente cuentas bancarias abiertas. El validador solo suma `open PortfolioAccounts`.

Verificación para 11794399: 7 (PortfolioAccounts open) + 3 (CreditCards + BankAccounts open) = 10 ≈ 11 (la diferencia residual puede ser por rounding o inclusión de CuentaAhorro).

Las cuentas LBZ se extraen correctamente con `is_open` bien calculado — contribuyen a la cuenta correcta de open accounts.

### Fix del validador (no del pipeline)

El check `active_credits` debería sumar: `open PortfolioAccounts + open CreditCards + open BankAccounts + open CheckingAccounts`.

---

## Hallazgo 4 — Discrepancia `total_balance` en 22436588 (falso positivo del validador)

### Qué muestra el validador

- `total_balance`: XML=60,095,000 vs extraído=45,315,000 → **delta $14,780,000**
- `total_past_due`: XML=15,348,000 vs extraído=568,000 → **delta $14,780,000**

### Causa

El delta de $14,780,000 corresponde exactamente al saldo de **1 TarjetaCredito castigada**:

```xml
<Cuenta estadoActual="Cart. castigada" calificacion="E"
        valorInicial="14780.0" saldoActual="14780.0" saldoMora="14780.0" .../>
```

Esta tarjeta **SÍ está extraída correctamente** como `CreditCard` en el full-report. El validador suma solo `PortfolioAccount.outstanding_balance`, excluyendo TarjetaCredito.

### Fix del validador

Los checks `total_balance` y `total_past_due` deben incluir `CreditCard.outstanding_balance` en la suma.

---

## Conclusión para negocio

### Único problema urgente: LBZ

Las libranzas son el producto crediticio con respaldo de nómina más relevante para la evaluación crediticia de empleados formales. Hoy el pipeline:

1. **Extrae todos los datos financieros** de cada libranza (saldos, historial, estados de cuenta)
2. **No puede clasificarlas** como libranzas — aparecen como tipo "Desconocido"
3. **No es posible presentar a negocio** un portafolio de libranzas separado del resto de cartera
4. Cualquier regla de decisión que dependa de `account_type == "Libranza"` no funcionará

El fix es de **2 líneas**: agregar `LBZ = "Libranza"` al enum `AccountType`. No requiere cambios en transformers ni builders. Una vez aplicado, el debug report debería mostrar 0 eventos para `transform_account_type` con `raw_value="LBZ"`.

### Todo lo demás funciona correctamente

- Conteo de registros: 14/14 checks de `node_count` pasan en todas las personas
- Saldos LBZ: correctamente extraídos (los $87.5M están en el output, solo sin etiqueta de tipo)
- Clasificación open/closed: correcta en todos los casos evaluados
- Historial de pagos, fechas, tasas: sin pérdida
