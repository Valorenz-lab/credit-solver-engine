# Análisis de estado — Credit Solver Engine
> Generado: 2026-03-24

---

## 1. Rutas activas y qué devuelven

### `GET /api/data-adapter/basic-report/<document_id>/`

Retorna dos bloques:

```json
{
  "basic_report": { ... },   // persona, metadata, identificación
  "global_report": [ ... ]   // array de CuentaCartera (todas, sin filtrar abiertas/cerradas)
}
```

**Estado:** Funcional pero parcialmente redundante. Todo lo que devuelve está contenido (con más detalle y mejor estructura) en `/full-report/`.

---

### `GET /api/data-adapter/full-report/<document_id>/`

Retorna 11 secciones:

| Sección | Contenido |
|---|---|
| `basic_info` | Persona, metadata de consulta, identificación |
| `general_profile` | `InfoAgregada`: resumen numérico, saldos por sector, historial mensual de comportamiento |
| `global_summary` | CuentaCartera **abiertas** (código `01` y familia) |
| `open_bank_accounts` | CuentaAhorro con estado `01`, `06`, `07` |
| `closed_bank_accounts` | CuentaAhorro con otros estados |
| `active_obligations` | CuentaCartera abiertas + TarjetaCredito abiertas (mezcladas) |
| `payment_habits_open` | CuentaCartera + TDC abiertas, agrupadas por sector |
| `payment_habits_closed` | CuentaCartera + TDC cerradas, agrupadas por sector |
| `query_history` | Historial de consultas (`Consulta`) |
| `global_debt_records` | Endeudamiento global por entidad (`EndeudamientoGlobal`) |
| `debt_evolution` | Evolución trimestral general (`EvolucionDeuda/Trimestre`) |

**Manejo de errores:** Ninguno. Cualquier XML inválido o documento no encontrado (salvo 404 ya implementado) retorna un 500 sin mensaje útil.

---

## 2. Qué falta para "igualar" el PDF de Datacredito

### 2.1 `CuentaCorriente` — Cuentas corrientes (NO extraídas)

El XML tiene nodos `<CuentaCorriente>` completamente distintos a `<CuentaAhorro>`. El builder actual **no los parsea**. En el PDF aparecen en la misma sección de "Cuentas bancarias".

Estructura XML:
```xml
<CuentaCorriente bloqueada="false" entidad="..." numero="..."
    fechaApertura="..." situacionTitular="0" codSuscriptor="010025" sector="1">
  <Caracteristicas clase="0" />
  <Valores />
  <Estado codigo="05" fecha="2008-09-30" />
  <Sobregiro valor="0.0" dias="0" fecha="2008-09-30" />
  <Llave>...</Llave>
</CuentaCorriente>
```

Diferencia clave vs `CuentaAhorro`: tiene `<Sobregiro>` (cupo/días en sobregiro) y `codSuscriptor`.

---

### 2.2 `HistoricoSaldos` — Saldos históricos por tipo de cuenta (NO extraído)

Dentro de `<InfoAgregada>` existe un nodo `<HistoricoSaldos>` con evolución trimestral de saldo **por tipo de cuenta** (`CAC`, `CAB`, `CEL`, `COC`, etc.). El PDF lo muestra como gráfico de barras apiladas.

```xml
<HistoricoSaldos>
  <TipoCuenta tipo="CAC">
    <Trimestre fecha="2024-03-01" totalCuentas="2" cuentasConsideradas="1" saldo="8089000" />
    ...
  </TipoCuenta>
  <TipoCuenta tipo="CEL">
    ...
  </TipoCuenta>
</HistoricoSaldos>
```

**Actualmente el builder lo ignora completamente.** Es la pieza más relevante que falta para replicar el PDF.

---

### 2.3 `AnalisisPromedio` dentro de `EvolucionDeuda` (NO extraído)

Dentro de `<EvolucionDeuda>` hay un nodo `<AnalisisPromedio>` con variaciones porcentuales respecto a trimestres anteriores:

```xml
<AnalisisPromedio cuota="-12.0" cupoTotal="-17.7" saldo="-23.5"
    porcentajeUso="-7.47" score="0.0" calificacion="0"
    aperturaCuentas="0.0" cierreCuentas="0.0"
    totalAbiertas="-6.25" totalCerradas="7.14" moraMaxima="0" />
```

El PDF lo muestra como "variación vs periodo anterior". No está en ningún modelo ni serializer.

---

### 2.4 `score` en `EvolucionDeuda/Trimestre` (campo ignorado)

Cada `<Trimestre>` en `EvolucionDeuda` tiene un atributo `score="0.0"`. El modelo `DebtEvolutionQuarter` no lo incluye. Potencialmente relevante como puntaje crediticio histórico.

---

### 2.5 `<Cheques>` — Historial de cheques devueltos (NO extraído)

Dentro de `<InfoAgregada>` existe el nodo `<Cheques />`. En este XML está vacío, pero en otros perfiles puede contener historial de cheques sin fondos — dato que el PDF muestra en una sección propia.

---

### 2.6 Sección de obligaciones cerradas sin lista dedicada

El full-report actual no tiene un campo `closed_obligations` (obligaciones cerradas). Las CuentaCartera y TarjetaCredito cerradas solo aparecen agrupadas en `payment_habits_closed` por sector. Para replicar el PDF (que lista todas las obligaciones históricas) haría falta exponer ese listado.

---

### 2.7 `comportamiento` como string crudo (no decodificado)

El campo `comportamiento` en CuentaCartera y TarjetaCredito llega como string de 47 caracteres:
```
"NNNNNNNNNNNNNNNNNNNNNNNN--NN-------------------"
```
Cada posición representa un mes: `N` = al día, `1`–`6` = meses en mora, `-` = sin dato.

El PDF lo muestra como tabla mes a mes con colores. Actualmente se expone el string raw sin parsear. Para igualar el PDF habría que convertirlo en un array de `{mes, estado}`.

---

## 3. Información en el XML que el PDF ignora (valor potencial)

Estos campos están en el XML pero **no aparecen en los PDFs de Datacredito**, y podrían ser útiles para el motor de decisión:

| Campo XML | Nodo | Descripción | Relevancia para motor |
|---|---|---|---|
| `tipoIdentificacion` + `identificacion` | Todos los nodos de cuenta | NIT / tipo de ID de la entidad acreedora | Trazabilidad de entidades |
| `codSuscriptor` | `CuentaCartera`, `CuentaCorriente` | Código interno del suscriptor Datacredito | Identificación única de reportante |
| `codigoDaneCiudad` | Todos los nodos de cuenta | Código DANE del municipio | Geolocalización precisa |
| `calificacionHD` | `CuentaCartera`, `TarjetaCredito` | Flag booleano de "calificación HD" | Calidad del dato |
| `mesesPermanencia` | `CuentaCartera/Caracteristicas` | Meses que lleva la cuenta activa | Antigüedad por producto |
| `probabilidadIncumplimiento` | `CuentaCartera`, `TarjetaCredito` | Probabilidad de default (float, 0.0–1.0) | Modelo de riesgo directo |
| `score` en `Trimestre` | `EvolucionDeuda` | Score crediticio trimestral | Señal de tendencia |
| `<Llave>` | Todos los nodos de cuenta | Clave compuesta interna de Datacredito | Deduplicación / matching |
| `AnalisisPromedio` | `EvolucionDeuda` | Variación % vs trimestres anteriores | Tendencias de comportamiento |
| `HistoricoSaldos` | `InfoAgregada` | Saldo histórico por tipo de producto | Feature engineering para ML |
| `<InfoDemografica>` | `NaturalNacional` | Datos demográficos adicionales (vacío en algunos XMLs) | Enriquecimiento de perfil |
| `<Cheques>` | `InfoAgregada` | Historial de cheques devueltos | Señal de riesgo directa |
| `Sobregiro` | `CuentaCorriente` | Cupo y días en sobregiro | Liquidez / riesgo |

---

## 4. Observaciones arquitecturales

- **`basic-report` es redundante:** Todo lo que devuelve está en `full-report`. Si el objetivo es tener un endpoint "liviano", debería acotarse a solo `basic_info` (sin global_report).

- **`closed_portfolio_accounts` no tiene sección propia:** Las CuentaCartera cerradas quedan "escondidas" en `payment_habits_closed`. Podría añadirse `closed_obligations` análogo a `active_obligations`.

- **`payment_habits` usa sector como string raw** (`"1"`, `"2"`, etc.) como clave del dict, en lugar del label del enum (`"FINANCIAL"`, `"COOPERATIVE"`). Menor inconsistencia respecto al resto de la API.

- **0 errores mypy** en 63 archivos — base sólida para agregar los campos faltantes con tipos seguros.

---

## 5. Resumen de prioridades (por impacto)

| # | Gap | Esfuerzo | Impacto para replica PDF |
|---|---|---|---|
| 1 | `HistoricoSaldos` en InfoAgregada | Medio | Alto |
| 2 | `CuentaCorriente` (checking accounts) | Medio | Alto |
| 3 | `closed_obligations` lista dedicada | Bajo | Medio |
| 4 | Parseo de `comportamiento` a array | Bajo | Medio |
| 5 | `AnalisisPromedio` en EvolucionDeuda | Bajo | Medio |
| 6 | `score` en Trimestre | Bajo | Bajo |
| 7 | `<Cheques>` | Bajo (si hay datos) | Bajo-medio |
| 8 | Manejo de errores en views (500 → respuestas útiles) | Bajo | — |
