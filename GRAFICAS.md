# GRAFICAS.md — Plan de Visualización del Reporte Crediticio

**Fecha:** 2026-04-07
**Contexto:** Visualizar los datos extraídos del XML de Datacredito para revisión humana. Objetivo final es el motor de decisión, pero primero hay que poder ver lo que se extrae.

---

## 1. Qué datos tenemos disponibles para graficar

### 1.1 Datos del sujeto (BasicReport)
| Campo | Útil para |
|---|---|
| Nombre, cédula, género | Cabecera del dashboard |
| Fecha de la consulta | Referencia temporal de todos los datos |

### 1.2 PortfolioAccount (CuentaCartera) — el corazón del reporte
Cada cuenta tiene:
| Campo | Valor de ejemplo | Para qué gráfica |
|---|---|---|
| `lender` | "ITAU CORPBANCA LIBRANZAS" | Labels en todas las vistas |
| `opened_date` | "2016-07-21" | Timeline de vigencia |
| `maturity_date` | "2025-12-01" | Timeline de vigencia |
| `outstanding_balance` | 3,795,000 COP | Gráficas de saldo |
| `installment_value` | 4,479,000 COP | Resumen de cuotas / libranzas |
| `past_due_amount` | 1,289,000 COP | Mora por cuenta |
| `days_past_due` | 45 | Indicador de riesgo |
| `missed_payments` | 3 | Indicador de riesgo |
| `payment_history` | `"NNNCC654321NNN---"` | Heatmap de comportamiento |
| `payment_frequency` | `PaymentFrequency.MONTHLY` | Identificar libranzas/desprendibles |
| `obligation_type` | `ObligationType.LIBRANZA` | Filtrar desprendibles |
| `industry_sector` | `IndustrySector.FINANCIERO` | Composición por sector |
| `is_open` | True / False | Separar activas vs cerradas |
| `account_condition` | `AccountCondition.ON_TIME` | Estado del crédito |
| `default_probability` | 0.12 | Score de riesgo por cuenta |

**El campo `payment_history` es el más rico:**
Cada carácter = 1 mes (de más reciente a más antiguo):
- `N` = al día
- `1`–`6` = mora (1=1-30 días, 2=31-60, ..., 6=181+)
- `C` = cartera castigada
- `-` = sin información / cuenta inactiva ese mes

### 1.3 CreditCard (TarjetaCredito)
| Campo | Para qué gráfica |
|---|---|
| `total_credit_limit` | Gráfica de cupo disponible |
| `outstanding_balance` | Ocupación del cupo |
| `available_limit` | Capacidad de endeudamiento restante |
| `payment_history` | Heatmap (misma lógica que CuentaCartera) |
| `franchise` | VISA, MC, AMEX — etiqueta visual |
| `is_open` | Filtro activas/cerradas |

### 1.4 AggregatedInfo (InfoAgregada) — datos agregados pre-calculados por Datacredito
**El más completo para gráficas temporales:**
| Estructura | Campos clave | Para qué |
|---|---|---|
| `monthly_history` (24 registros) | `date, total_balance, total_past_due` | Evolución mensual de deuda/mora |
| `debt_evolution` (trimestres) | `date, balance, installment, score, new_accounts, closed_accounts, total_open` | Evolución trimestral |
| `behavior_history` | `date, behavior(char), count` | Comportamiento dominante por mes |
| `balances.by_sector` | `sector, balance, participation(%)` | Distribución por sector |
| `balances.total_balance` | float | KPI principal |
| `balances.total_past_due` | float | KPI mora |
| `balances.monthly_installment` | float | Cuota mensual total (flujo de caja) |
| `balances.past_due_30/60/90` | float | Antigüedad de mora |
| `principals.active_credits` | int | Contador activos |
| `principals.oldest_account_date` | str | Antigüedad crediticia |

### 1.5 QueryRecord (Consulta)
| Campo | Para qué |
|---|---|
| `date` | Timeline de consultas |
| `entity` | Quién consultó |
| `sector` | Financiero / Real / Telecom |
| `reason` | Tipo de consulta |

### 1.6 GlobalDebtRecord (EndeudamientoGlobal)
Resumen de deuda por entidad — útil para comparar vs PortfolioAccounts individuales.

---

## 2. Gráficas a implementar

### G1 — Cabecera: Perfil básico + KPIs
**Tipo:** HTML/tarjetas de métricas (no necesita Chart.js)
```
[Nombre completo]   Cédula: XXXXXXXX   Consulta: 2024-03-22
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Créditos activos: 10    Saldo total: $26,869,000
  Créditos cerrados: 10   Mora total:  $10,367,000
  Cuota mensual:  $9,965,000   Antigüedad: 2011
```
**Fuente:** `BasicReport` + `AggregatedInfo.summary`

---

### G2 — Evolución mensual: Saldo y Mora (24 meses)
**Tipo:** Line chart, 2 series
**Datos:**
```python
# AggregatedInfo.summary.balances.monthly_history
labels = [m.date for m in monthly_history]           # "2024-02-29", ...
balance_data = [m.total_balance for m in ...]         # 26,869,000 COP
past_due_data = [m.total_past_due for m in ...]       # 10,367,000 COP
```
**Valor:** Ver tendencia — ¿el saldo baja? ¿la mora crece? ¿hubo un evento de endeudamiento?

**Nota:** `monthly_history` viene del más reciente al más antiguo. Invertir para el eje X.

---

### G3 — Composición de deuda por sector
**Tipo:** Doughnut chart
**Datos:**
```python
# AggregatedInfo.summary.balances.by_sector
labels = [s.sector for s in by_sector]               # "Financiero", "Real", ...
data   = [s.balance for s in by_sector]
```
**Valor:** ¿Qué sector concentra la deuda? Un sujeto con 80% en sector Real (gestoras de cobro) es diferente a uno con 80% financiero.

---

### G4 — Heatmap de comportamiento por cuenta
**Tipo:** Tabla HTML con colores (no Chart.js, CSS puro)
**Estructura:**
```
Entidad              | ← 24 meses → (carácter por mes)
ITAU LIBRANZAS       | [N][N][N][N][C][C][6][5][4][3][2][1][N]...
ASLEGAL SERVICIOS    | [C][C][C][C][1][6][6][6][6][6][5][4][N]...
CFG PARTNERS         | [N][N][N]...
```
**Colores:**
- `N` → verde (#22c55e)
- `1` → amarillo (#fbbf24)
- `2-3` → naranja (#f97316)
- `4-6` → rojo (#ef4444)
- `C` → rojo oscuro (#991b1b)
- `-` → gris (#e5e7eb)

**Fuente:** `PortfolioAccount.payment_history` + `CreditCard.payment_history`
**Valor:** La visualización más densa de información. De un vistazo se ve si el sujeto tiene patrones de mora recurrente, si se está deteriorando o mejorando, cuántas cuentas están en rojo simultáneamente.

---

### G5 — Timeline de vigencia de obligaciones (Gantt horizontal)
**Tipo:** Horizontal bar chart (Chart.js type: 'bar' con eje horizontal)
**Datos:** Una barra por obligación activa/cerrada
```python
# PortfolioAccount donde opened_date is not None
for account in portfolio_accounts:
    start = account.opened_date
    end = account.maturity_date or query_date
    duration_months = delta(end, start)
    # Color por sector: financiero=azul, real=verde, telecom=gris, cooperativo=amarillo
```
**Valor:** Ver qué cuentas siguen abiertas, la antigüedad del portafolio, concentración temporal de aperturas.

---

### G6 — Libranzas y descuentos automáticos
**Tipo:** Tabla enriquecida HTML (no Chart.js)
**Filtro:** `obligation_type == ObligationType.LIBRANZA` OR detectar por nombre de entidad ("LIBRANZA", "LIBRE INVERSION")
**Columnas:**
```
Entidad | Sector | Apertura | Saldo | Cuota/mes | Plazo restante | Estado
```
**Valor:** Los descuentos de nómina son obligaciones que el sujeto no puede dejar de pagar voluntariamente. Son el "piso de flujo de caja" del sujeto. Crítico para el motor de decisión.

**Lógica de cuota mensual total de libranzas:**
```python
libranzas = [pa for pa in portfolio_accounts
             if pa.characteristics.obligation_type == ObligationType.LIBRANZA
             and pa.is_open]
total_libranza_installment = sum(
    pa.values.installment_value for pa in libranzas
    if pa.values.installment_value and pa.values.installment_value > 0
)
```

---

### G7 — Evolución trimestral (Deuda + Score)
**Tipo:** Bar + Line combo chart
**Datos:**
```python
# AggregatedInfo.debt_evolution (lista de DebtEvolutionQuarter)
labels         = [q.date for q in debt_evolution]
balance_bars   = [q.balance for q in debt_evolution]
installment    = [q.installment for q in debt_evolution]
total_open     = [q.total_open for q in debt_evolution]
new_accounts   = [q.new_accounts for q in debt_evolution]
```
**Valor:** Tendencia de largo plazo (vs los 24 meses de G2). Ver si el sujeto abrió muchos créditos recientemente.

---

### G8 — Historial de consultas
**Tipo:** Tabla HTML cronológica + mini-timeline visual
**Columnas:**
```
Fecha | Entidad | Sector | Motivo
```
**Valor:** Muchas consultas recientes = el sujeto está buscando crédito activamente. Consultas de cobranza = señal de alerta.

---

## 3. Stack técnico recomendado

### 3.1 Decisión: Chart.js directo desde templates Django

**No usar React.** El usuario tiene experiencia con Chart.js — el API es idéntico en Django templates. El ahorro en setup es enorme.

**Flujo:**
```
Vista Django → dict Python → json_script filter → template HTML → Chart.js (CDN)
```

**Ejemplo concreto:**
```python
# views.py
def dashboard_report(request, document_id):
    xml_path = DATA_DIR / f"{document_id}.xml"
    report = FullReportBuilder().parse_file(str(xml_path))

    chart_data = {
        "monthly_labels": [...],
        "monthly_balance": [...],
        "monthly_past_due": [...],
        "sector_labels": [...],
        "sector_values": [...],
    }
    return render(request, "dashboard.html", {
        "report": serialize_full_report(report),
        "chart_data": chart_data,
        "basic": serialize_basic_report(report.basic_report),
    })
```

```html
<!-- dashboard.html -->
{% load json %}
{{ chart_data|json_script:"chart-data" }}

<canvas id="balance-chart"></canvas>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
  const data = JSON.parse(document.getElementById('chart-data').textContent);
  new Chart(document.getElementById('balance-chart'), {
    type: 'line',
    data: {
      labels: data.monthly_labels,
      datasets: [
        { label: 'Saldo', data: data.monthly_balance, borderColor: '#3b82f6' },
        { label: 'Mora',  data: data.monthly_past_due, borderColor: '#ef4444' },
      ]
    }
  });
</script>
```

**Ventajas sobre React:**
- Cero setup (no build, no npm, no compilación)
- No hay un SPA separado — una URL Django = una vista completa
- El JSON del backend llega como atributo del template, no como fetch async
- Mantenible: cualquier dev Python puede leerlo
- Suficiente para el propósito (visualización interna, no producto de usuario)

### 3.2 CSS: Tailwind CDN o Bootstrap CDN
Para el heatmap (G4) y las tarjetas de KPIs se necesita algo de styling. Tailwind CDN Play es suficiente (sin build):
```html
<script src="https://cdn.tailwindcss.com"></script>
```

### 3.3 Sin base de datos adicional
Los datos vienen del XML en tiempo de request. No hay que persistir nada nuevo.

---

## 4. Plan de implementación por fases

### Fase A — Vista básica + G1 + G2 (mínimo útil)
1. Nueva URL `GET /api/data-adapter/dashboard/<document_id>/`
2. Vista `dashboard_report` en `views.py`
3. Helper `_build_chart_data(report)` que extrae los dicts para Chart.js
4. Template `dashboard.html`:
   - Cabecera con KPIs (G1)
   - Gráfica de evolución mensual (G2) — Line chart

**Resultado:** Con 2-3 horas de trabajo, una página funcional que muestra la evolución de deuda del sujeto.

### Fase B — G3 + G4 + G6 (las más valiosas)
5. Añadir doughnut de sectores (G3) — 30 min
6. Añadir heatmap de payment_history (G4) — tabla HTML, sin Chart.js, 1h
7. Añadir tabla de libranzas activas (G6) — filtrar + renderizar tabla, 45 min

**Resultado:** La vista más útil para el motor de decisión. El heatmap (G4) es la visualización más densa y valiosa.

### Fase C — G5 + G7 + G8 (completitud)
8. Gantt de vigencia de obligaciones (G5) — requiere adaptar Chart.js horizontal bar
9. Evolución trimestral combo (G7)
10. Tabla de historial de consultas (G8) — HTML puro, 20 min

---

## 5. Estructura de archivos a crear

```
data_adapter/
  views.py               ← añadir dashboard_report() + _build_chart_data()
  urls.py                ← añadir URL dashboard/<id>/
  templates/
    data_adapter/
      dashboard.html     ← plantilla principal
      _kpi_cards.html    ← partial: cabecera de métricas
      _heatmap.html      ← partial: tabla payment_history
      _libranzas.html    ← partial: tabla de libranzas
      _queries.html      ← partial: historial de consultas
```

---

## 6. Notas sobre los datos

### Inversión de `payment_history`
El string viene de más reciente a más antiguo. Para el heatmap hay que invertirlo:
```python
payment_history_reversed = account.payment_history[::-1]
# Ahora índice 0 = mes más antiguo, índice -1 = mes más reciente
```

### Centinela `-1` en campos monetarios
`installment_value = -1` y `outstanding_balance = -1` significan "sin información", no valores monetarios. Filtrar antes de sumar o graficar:
```python
def safe_amount(value):
    return value if value is not None and value > 0 else None
```

### Unidades de `monthly_history`
`monthly_history.total_balance` está en **pesos** (no en miles). `AggregatedBalances.total_balance` también en pesos. Consistente con lo que extrae el serializer.

### Libranzas: cómo identificarlas
```python
from data_adapter.enums.financial_info.obligation_type import ObligationType
libranzas = [
    pa for pa in report.portfolio_accounts
    if pa.characteristics.obligation_type == ObligationType.LIBRANZA
    or (pa.lender and "LIBRANZA" in pa.lender.upper())
]
```

### Cuota mensual total para motor de decisión
```python
# Flujo de caja comprometido por descuentos automáticos (libranzas)
total_auto_debit = sum(
    pa.values.installment_value
    for pa in libranzas
    if pa.is_open
    and pa.values.installment_value is not None
    and pa.values.installment_value > 0
)
```

---

## 7. Gráfica prioritaria: el heatmap de comportamiento (G4)

Es la más valiosa y la más fácil de implementar (sin Chart.js). Ejemplo de HTML generado:

```html
<table class="text-xs font-mono">
  <thead>
    <tr>
      <th>Entidad</th>
      <!-- 24 columnas de meses, de más antiguo a más reciente -->
      <th>Ene'22</th><th>Feb'22</th> ...
    </tr>
  </thead>
  <tbody>
    {% for account in accounts_with_history %}
    <tr>
      <td>{{ account.lender }}</td>
      {% for char in account.payment_history_chars %}
        <td class="{{ char.css_class }}" title="{{ char.label }}">{{ char.symbol }}</td>
      {% endfor %}
    </tr>
    {% endfor %}
  </tbody>
</table>
```

Donde `payment_history_chars` es un helper que convierte el string en una lista de dicts con CSS class y label:

```python
def parse_payment_history(history_str, query_date):
    """Convierte el string de historial en lista de dicts para el template."""
    chars = []
    reversed_str = (history_str or "")[::-1]  # invertir: índice 0 = más antiguo
    for i, char in enumerate(reversed_str):
        month_date = query_date - relativedelta(months=len(reversed_str)-1-i)
        chars.append({
            "symbol": char,
            "label": BEHAVIOR_LABELS.get(char, char),
            "css_class": BEHAVIOR_CSS.get(char, "bg-gray-100"),
            "date": month_date.strftime("%b'%y"),
        })
    return chars

BEHAVIOR_CSS = {
    "N": "bg-green-200 text-green-800",
    "1": "bg-yellow-200 text-yellow-800",
    "2": "bg-orange-300 text-orange-800",
    "3": "bg-orange-500 text-white",
    "4": "bg-red-400 text-white",
    "5": "bg-red-600 text-white",
    "6": "bg-red-800 text-white",
    "C": "bg-red-950 text-white",
    "-": "bg-gray-100 text-gray-400",
}
```
