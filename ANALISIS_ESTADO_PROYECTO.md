# Análisis de estado — Credit Solver Engine
> Actualizado: 2026-03-24 | Basado en análisis de 5 XMLs reales de Datacredito

---

## 1. Rutas activas

| Ruta | Devuelve |
|---|---|
| `GET /api/data-adapter/basic-report/<id>/` | `basic_report` (persona + metadata) + `global_report` (todas las CuentaCartera) |
| `GET /api/data-adapter/full-report/<id>/` | 12 secciones con toda la info disponible actualmente |

`basic-report` es **parcialmente redundante** con `full-report`. Todo lo que devuelve está contenido en él con más detalle.

`full-report` actualmente retorna:
`basic_info`, `general_profile`, `global_summary`, `open_bank_accounts`, `closed_bank_accounts`, `checking_accounts` *(nuevo)*, `active_obligations`, `payment_habits_open`, `payment_habits_closed`, `query_history`, `global_debt_records`, `debt_evolution`

---

## 2. Nodos XML que AÚN NO se parsean al full-report

Ordenados por relevancia para un motor de decisión crediticia.

### 2.1 `PerfilGeneral` — Conteo de créditos por sector ⚠️ ALTA RELEVANCIA

Dentro de `InfoAgregada`. Desglosa créditos por los 4 sectores (financiero, cooperativo, real, telcos).

```xml
<PerfilGeneral>
  <CreditosVigentes      sectorFinanciero="0" sectorCooperativo="1" sectorReal="9" sectorTelcos="1" totalComoPrincipal="11" totalComoCodeudorYOtros="0" />
  <CreditosCerrados      sectorFinanciero="7" sectorCooperativo="3" sectorReal="11" sectorTelcos="5" totalComoPrincipal="24" totalComoCodeudorYOtros="2" />
  <CreditosReestructurados sectorFinanciero="0" sectorCooperativo="0" sectorReal="0" sectorTelcos="0" totalComoPrincipal="0" totalComoCodeudorYOtros="0" />
  <CreditosRefinanciados sectorFinanciero="0" sectorCooperativo="0" sectorReal="1" sectorTelcos="0" totalComoPrincipal="1" totalComoCodeudorYOtros="0" />
  <ConsultaUlt6Meses     sectorFinanciero="2" sectorCooperativo="0" sectorReal="5" sectorTelcos="0" totalComoPrincipal="0" totalComoCodeudorYOtros="0" />
  <Desacuerdos           sectorFinanciero="0" sectorCooperativo="0" sectorReal="0" sectorTelcos="0" totalComoPrincipal="0" totalComoCodeudorYOtros="0" />
  <AntiguedadDesde       sectorCooperativo="2014-12-14" sectorFinanciero="1996-07-01" sectorReal="2009-05-13" sectorTelcos="2005-10-18" />
</PerfilGeneral>
```

**Campos sin parsear:**
- Créditos reestructurados y refinanciados por sector
- Antigüedad de la primera cuenta **por sector** (más preciso que el campo global `antiguedadDesde`)
- Consultas últimos 6 meses por sector
- Desacuerdos por sector

---

### 2.2 `VectorSaldosYMoras` — Serie mensual de saldos y moras por sector ⚠️ ALTA RELEVANCIA

Dentro de `InfoAgregada`. Serie temporal de 13 meses con mora máxima por sector.

```xml
<VectorSaldosYMoras poseeSectorCooperativo="true" poseeSectorFinanciero="false" poseeSectorReal="true" poseeSectorTelcos="true">
  <SaldosYMoras fecha="2024-03-31"
    totalCuentasMora="1"
    saldoDeudaTotalMora="60221.0"
    saldoDeudaTotal="57105.0"
    morasMaxSectorReal="4"
    morasMaxSectorCooperativo="N"
    morasMaxSectorTelcos="C"
    morasMaximas="4"
    numCreditos30="0"
    numCreditosMayorIgual60="1" />
  <!-- ~13 registros mensuales -->
</VectorSaldosYMoras>
```

**Campos sin parsear:**
- Presencia en cada sector (`poseeSectorX`)
- Mora máxima **por sector** en cada mes (puede ser número, "N"=normal, "C"=castigada)
- Número de créditos en mora 30 días / ≥60 días mensual

---

### 2.3 `EndeudamientoActual` — Deuda vigente detallada por sector/tipo/usuario ⚠️ ALTA RELEVANCIA

Dentro de `InfoAgregada`. Estructura jerárquica: Sector → TipoCuenta → Usuario → Cuenta.

```xml
<EndeudamientoActual>
  <Sector codSector="3">
    <TipoCuenta tipoCuenta="CAC">
      <Usuario tipoUsuario="Principal">
        <Cuenta estadoActual="Al día"
                calificacion="D"
                valorInicial="55000.0"
                saldoActual="75680.0"
                saldoMora="0.0"
                cuotaMes="880.0"
                comportamientoNegativo="false"
                totalDeudaCarteras="326476.0" />
      </Usuario>
    </TipoCuenta>
  </Sector>
</EndeudamientoActual>
```

**Útil para:** cruce directo de deuda activa por tipo sin tener que reconstruirla desde las cuentas individuales.

---

### 2.4 `ResumenEndeudamiento` — Resumen trimestral por sector y tipo de cartera

Dentro de `InfoAgregada`. 3 trimestres × 4 sectores × 5 tipos de cartera + garantías.

```xml
<ResumenEndeudamiento>
  <Trimestre fecha="2023-12-01">
    <Sector sector="Financiero" codigoSector="1" garantiaAdmisible="0" garantiaOtro="0">
      <Cartera tipo="Comercial"          numeroCuentas="0" valor="0.0" />
      <Cartera tipo="Hipotecario"        numeroCuentas="0" valor="0.0" />
      <Cartera tipo="Consumo"            numeroCuentas="1" valor="10856.0" />
      <Cartera tipo="Tarjeta de Crédito" numeroCuentas="0" valor="0.0" />
      <Cartera tipo="Microcrédito"       numeroCuentas="0" valor="0.0" />
    </Sector>
    <!-- Cooperativo, Real, Telcos -->
  </Trimestre>
</ResumenEndeudamiento>
```

---

### 2.5 `AnalisisVectores` — Historial por cuenta con comportamiento mensual

Dentro de `InfoAgregada`. Organiza cuentas vigentes por sector con 24 meses de `CaracterFecha`.

```xml
<AnalisisVectores>
  <Sector nombreSector="Sector Real">
    <Cuenta entidad="FOCREDISOCIAL" numeroCuenta="000003932" tipoCuenta="CAC"
            estado="Al día" contieneDatos="true">
      <CaracterFecha fecha="2024-03-31" />
      <CaracterFecha fecha="2024-02-29" saldoDeudaTotalMora="6" />
      <!-- 24 registros mensuales -->
    </Cuenta>
    <MorasMaximas>
      <CaracterFecha fecha="2024-03-31" saldoDeudaTotalMora="4" />
    </MorasMaximas>
  </Sector>
</AnalisisVectores>
```

**Campos sin parsear:** `estado` por cuenta ("Al día", "Esta en mora 120", "Cart. castigada"), mora mensual detallada por cuenta.

---

### 2.6 `InfoDemografica` — Actividad económica e identificaciones adicionales

Actualmente modelada como vacía. En algunos XMLs contiene datos de entidades reportantes.

```xml
<InfoDemografica>
  <ActividadEconomica idRegistro="1" tipo="06" CIIU="0000" estado="" fecha="2011-11-30"
    nitReporta="00804015582" razonSocial="COOPERATIVA DE CREDITO..." />
  <OperacionesInternacionales idRegistro="4" operaInt="false" fecha="2019-03-31"
    nitReporta="00900479582" razonSocial="-" />
  <Identificacion idRegistro="3" fechaExpedicion="1982-01-01" lugarExpedicion="15001000"
    nitReporta="00890212341" razonSocial="FUNDACION DELAMUJER..." />
</InfoDemografica>
```

**Nota:** `tipo` en `ActividadEconomica` es un código (02=empleado, 06=independiente, etc.). `CIIU` siempre "0000" en la muestra.

---

### 2.7 `InfoAgregadaMicrocredito` — Sección paralela para microcrédito

Mismo esquema que `InfoAgregada` pero filtrado solo para créditos de microcrédito. Presente en algunos XMLs. Incluye adicionalmente:

```xml
<ImagenTendenciaEndeudamiento>
  <Series serie="Cartera bancaria">
    <Valores>
      <Valor valor="87.3" fecha="2024-03-31" />
      <!-- 12 meses -->
    </Valores>
  </Series>
</ImagenTendenciaEndeudamiento>
```

---

### 2.8 `Garantia` en `EndeudamientoGlobal` — Garantías por obligación global

El modelo `GlobalDebtRecord` parsea la entidad pero omite el nodo `<Garantia>`:

```xml
<EndeudamientoGlobal calificacion="..." fuente="..." saldoPendiente="..." ...>
  <Entidad nombre="..." nit="..." sector="..." />
  <Garantia tipo="9" valor="-1" />   ← NO EXTRAÍDO
</EndeudamientoGlobal>
```

Códigos de `tipo`: 0, 9. Valor puede ser número o -1.

---

### 2.9 `Adjetivo` — Marcador de comportamiento en CuentaCartera

Nodo hijo directo de algunas `CuentaCartera`. Presente en 3 de 5 XMLs.

```xml
<Adjetivo codigo="7" fecha="2021-08-31" />
```

Aparece en cuentas específicas como un flag de estado adicional. Código "7" es el único valor observado.

---

### 2.10 `EndeudamientoGlobal.independiente` — Atributo no parseado

El nodo `<EndeudamientoGlobal>` tiene un atributo `independiente` que no está en el modelo `GlobalDebtRecord`:

```xml
<EndeudamientoGlobal calificacion="A" fuente="1" saldoPendiente="45605.0"
  tipoCredito="CMR" moneda="1" numeroCreditos="1"
  independiente="true"   ← NO EXTRAÍDO
  fechaReporte="2024-03-31">
```

---

## 3. Campos sin enum o transformer

Extraídos como string crudo sin traducción:

| Campo | Nodo | Valores observados | Impacto |
|---|---|---|---|
| `garantia` | `CuentaCartera/Caracteristicas`, `TarjetaCredito/Caracteristicas` | "0", "1", "2" | Medio — indica tipo de garantía |
| `ejecucionContrato` | `CuentaCartera/Caracteristicas` | "0", "1", "2", "6" | Bajo |
| `formaPago` | `CuentaCartera`, `TarjetaCredito` | "0", "1" | Bajo — ya existe `PaymentMethod` enum pero no se aplica aquí |
| `Consulta.razon` | `Consulta` | texto libre / código | Bajo |
| `EndeudamientoGlobal.fuente` | `EndeudamientoGlobal` | "1", "2", etc. | Bajo |
| `account_class` (clase) | `CuentaAhorro/Caracteristicas` | "0", "2", "4" | Bajo — "4"=digital (Nequi/Daviplata) |
| `VectorSaldosYMoras.morasMaximas` | `SaldosYMoras` | número, "N", "C", "-" | **Alto** — indicador directo de mora |
| `EndeudamientoActual/Cuenta.estadoActual` | `Cuenta` | "Al día", "Esta en mora 120", "Cart. castigada", "Dudoso recaudo", "Pago Vol" | Alto — texto, no código |
| `Adjetivo.codigo` | `Adjetivo` | "7" | Desconocido |
| `ActividadEconomica.tipo` | `InfoDemografica` | "02", "06" | Bajo (02=empleado, 06=independiente aprox.) |

---

## 4. Campos ya parseados que podrían tener enum

| Campo | Transformer actual | Observación |
|---|---|---|
| `payment_status_code` (EstadoPago.codigo) | Ninguno | Valores "01", "05", "06", "08", "45" — reutilizar `AccountStatus` enum o crear uno propio |
| `account_statement_code` (EstadoCuenta.codigo) | `transform_status_account` ✓ | Ya funciona |
| `origin_state_code` (EstadoOrigen.codigo) | `transform_origin_state` ✓ | Ya funciona |
| `codSector` en `EndeudamientoActual` | `transform_sector` (pendiente aplicar) | "1", "2", "3", "4" |

---

## 5. Observaciones de arquitectura

- **Parseo múltiple del mismo XML**: `FullReportBuilder` instancia `BasicDataReportBuilder` y `GlobalReportBuilder` internamente, cada uno re-parsea el XML. Técnicamente funciona pero es ineficiente. Refactor pendiente.
- **`payment_habits_open/closed`** usa el sector como clave raw del dict ("1", "2"), no el label del enum. Inconsistente con el resto de la API.
- **`closed_portfolio_accounts`** no tiene sección propia en el full-report. Las CuentaCartera cerradas quedan dentro de `payment_habits_closed`, sin lista plana accesible.
- **`comportamiento`** (string de 47 chars tipo `"NNNNN--NNN..."`) está expuesto crudo. Cada posición = 1 mes. Parseable a array de `{mes, estado}` si se necesita.
- **0 errores mypy** (antes de los cambios recientes) — base sólida.

---

## 6. Resumen de prioridades de parseo

| # | Qué | Esfuerzo | Relevancia motor |
|---|---|---|---|
| 1 | `PerfilGeneral` (créditos/antigüedad por sector) | Bajo | **Alta** |
| 2 | `VectorSaldosYMoras` (mora mensual por sector) | Medio | **Alta** |
| 3 | `EndeudamientoActual` (deuda vigente estructurada) | Medio | **Alta** |
| 4 | `ResumenEndeudamiento` (trimestral por cartera) | Medio | Media |
| 5 | `Garantia` en `EndeudamientoGlobal` | Bajo | Media |
| 6 | `EndeudamientoGlobal.independiente` | Mínimo | Media |
| 7 | `AnalisisVectores` (historial por cuenta) | Alto | Media |
| 8 | `InfoDemografica` (actividad económica) | Bajo | Baja-media |
| 9 | `Adjetivo` en `CuentaCartera` | Mínimo | Desconocida |
| 10 | `InfoAgregadaMicrocredito` | Alto | Baja (subset de InfoAgregada) |
| 11 | `ImagenTendenciaEndeudamiento` | Medio | Baja |
