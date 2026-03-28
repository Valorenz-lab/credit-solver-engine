# Naming Guide — Credit Solver Engine

> Fuente de verdad para nombres de construcciones Python en este proyecto.
> Aplica a: enums, dataclasses, TypedDicts, builders, serializers, transformers y archivos.
> Tanto Claude como el desarrollador deben consultar este documento antes de crear o renombrar cualquier cosa.

---

## Índice

1. [Principio rector](#1-principio-rector)
2. [Reglas por tipo de construcción](#2-reglas-por-tipo-de-construcción)
3. [Inventario: nodos XML → dataclasses](#3-inventario-nodos-xml--dataclasses)
4. [Inventario: tablas XSD → enums](#4-inventario-tablas-xsd--enums)
5. [Cambios pendientes](#5-cambios-pendientes)

---

## 1. Principio rector

**Un nombre debe responder estas tres preguntas sin necesidad de leer el cuerpo:**

1. ¿Qué representa? (`PortfolioAccount`, `PaymentStatus`)
2. ¿Qué tipo de construcción Python es? (enum → termina en clasificador; dataclass → sustantivo limpio)
3. ¿A qué dominio pertenece? (`CreditCard*`, `BankAccount*`, `Portfolio*`)

Si el nombre requiere un comentario para entenderse, el nombre está mal.

**Idioma:** inglés en todo el código. Excepción única: los strings literales que identifican nodos XML (`"CuentaCartera"`, `"Caracteristicas"`) y los `.value` de los enums que son etiquetas visibles al usuario.

---

## 2. Reglas por tipo de construcción

### 2.1 Enums (`StrEnum`)

**Regla:** el nombre debe incluir un **clasificador semántico** que indique qué dimensión se está clasificando. El clasificador hace las veces de "sufijo enum" sin requerir el sufijo `Enum`.

| Clasificador | Cuándo usarlo | Ejemplo |
|---|---|---|
| `Status` | Condición actual de un objeto (puede cambiar con el tiempo) | `AccountStatus`, `PaymentStatus`, `PlasticStatus` |
| `Type` | Categoría estructural fija de un objeto | `AccountType`, `ObligationType`, `ContractType` |
| `Role` | Papel que cumple un actor en una relación | `DebtorRole`, `CardholderRole` |
| `Reason` | Causa o motivo de un evento | `QueryReason` |
| `Frequency` | Periodicidad | `PaymentFrequency` |
| `Behavior` | Patrón de comportamiento observado en el tiempo | `PaymentBehavior` |
| `Method` | Modo de ejecución de una acción | `PaymentMethod` |
| `Rating` | Escala de calificación | `CreditRating` |
| `Sector` (como parte del nombre) | Segmento de industria | `IndustrySector` |
| `State` | Estado de un proceso de origen (restructurado, refinanciado) | `OriginState` |

**Cuando ningún clasificador encaja:** añadir sufijo `Enum`.
Por ejemplo, si existiera un enum de monedas sin clasificador natural → `CurrencyEnum`. Pero `Currency` por sí solo ya es suficientemente claro en este dominio.

**Colisión con dataclass:** si un nombre natural colisiona con un dataclass existente, el enum tiene prioridad sobre ese nombre y el dataclass se renombra (ver §5).

**Ejemplos correctos:**
```
AccountCondition   ✓   (condición del estado de cuenta — Tabla 4)
PaymentStatus      ✓   (estado acumulado de pago — Tabla 4)
DebtorRole         ✓   (rol del deudor — Tabla 6)
IndustrySector     ✓   (sector de la economía)
SavingsAccountStatus ✓ (estado de CuentaAhorro — Tabla 16)
```

**Ejemplos incorrectos:**
```
Sector             ✗   (sustantivo sin clasificador — podría ser cualquier cosa)
DebtorQualityPortfolio ✗  (mezcla dominio "calidad" con contexto "Portfolio" — verboso)
AccountStateSavings    ✗  (orden invertido, "State" + sustantivo en lugar de sustantivo + "Status")
TypesId                ✗  (plural + abreviación — no comunica nada)
```

---

### 2.2 Dataclasses (modelos)

**Regla:** sustantivo limpio en PascalCase, sin sufijo. Si el modelo agrupa sub-nodos relacionados (un `<Estados>` con tres hijos), el nombre es plural.

| Patrón | Cuándo usarlo | Ejemplo |
|---|---|---|
| `NounPhrase` | Un registro/entidad principal del XML | `PortfolioAccount`, `BankAccount`, `CreditCard` |
| `NounPhraseCharacteristics` | Sub-nodo `<Caracteristicas>` de una entidad | `PortfolioCharacteristics`, `CreditCardCharacteristics` |
| `NounPhraseValues` | Sub-nodo `<Valores>/<Valor>` de una entidad | `PortfolioValues`, `CreditCardValues` |
| `NounPhraseStates` | Sub-nodo `<Estados>` que agrupa varios estados | `PortfolioStates`, `CreditCardStates` |
| `NounPhraseState` | Sub-nodo singular de estado (`<Estado>`) | `BankAccountState` |
| `NounPhraseRecord` | Un registro de historial/auditoría | `QueryRecord`, `GlobalDebtRecord`, `ScoreRecord` |
| `NounPhraseReport` | Resultado completo de un builder | `BasicReport`, `GlobalReport`, `FullReport` |

**Nunca usar:** sufijos `Model`, `Data`, `Info`, `Obj`, `Entity`, ni el nombre del archivo como prefijo. El nombre del modelo debe ser independiente del archivo donde vive.

**Colisión con enum:** si el nombre natural de un dataclass ya está tomado por un enum, el dataclass se renombra para ser más específico sobre qué agrupa (ver §5).

---

### 2.3 TypedDicts

**Regla:** prefijo `Serialized` + el nombre del dataclass correspondiente.

```
PortfolioAccount     →   SerializedPortfolioAccount
BankAccount          →   SerializedBankAccount
PortfolioStates      →   SerializedPortfolioStates
```

Viven en `xml_adapter/types.py` (y en el futuro en archivos `types_*.py` por dominio).

---

### 2.4 Builders

**Regla:** `<DomainNoun>Builder` — sustantivo del dominio que construye + sufijo `Builder`.

```
GlobalReportBuilder        ✓
BankAccountReportBuilder   ✓   (especifica que construye el report de BankAccount)
FullReportBuilder          ✓
QueryBuilder               ✓
```

El método público principal es siempre `.build() -> ReturnType` o `.parse(input) -> ReturnType`.

---

### 2.5 Funciones de serialización

**Regla:** `serialize_<snake_case_del_modelo>(model: Model) -> Serialized<Model>`

```python
serialize_portfolio_account(account: PortfolioAccount) -> SerializedPortfolioAccount
serialize_bank_account(account: BankAccount) -> SerializedBankAccount
```

Funciones privadas del módulo: prefijo `_serialize_`.

---

### 2.6 Funciones de transformación

**Regla:** `transform_<snake_case_del_campo>(value: Optional[str]) -> SomeEnum`

El nombre del campo es el nombre en Python del campo del modelo (no el nombre del atributo XML).

```python
transform_obligation_type(value)   →  ObligationType
transform_payment_status(value)    →  PaymentStatus
transform_debtor_role(value)       →  DebtorRole
```

Nunca lanzar excepción: retornar `UNKNOWN` como fallback.

---

### 2.7 Archivos

**Regla:** `snake_case` del nombre principal que contiene el archivo.

| Tipo | Patrón | Ejemplo |
|---|---|---|
| Enum | `<snake_case_del_enum>.py` | `account_condition.py`, `payment_status.py` |
| Modelo | `<dominio>_models.py` | `global_report_models.py`, `bank_account_models.py` |
| Builder | `<dominio>_builder.py` | `query_builder.py`, `global_report_report_builder.py` |
| Serializer | `serializer_<dominio>.py` | `serializer_global_report.py` |
| Transformer | `<dominio>_transformer.py` o `shared_transformers.py` | `global_report_transformer.py` |

---

## 3. Inventario: nodos XML → dataclasses

Mapa completo de nodos del XSD v1.6 a sus dataclasses Python actuales.

| Nodo XML | XSD Type | Dataclass Python | Archivo | Estado |
|---|---|---|---|---|
| `Informes/Informe` | `InformeType` | *(sin modelo, es contenedor raíz)* | — | — |
| `NaturalNacional` | — | `BasicDataPerson` | `basic_data_models.py` | ✅ |
| `NaturalNacional/Identificacion` | — | `CustomerIdentification` | `basic_data_models.py` | ✅ |
| `Reporte` (atributos raíz) | — | `QueryMetadata` | `basic_data_models.py` | ✅ |
| *(reporte completo básico)* | — | `BasicReport` | `basic_data_models.py` | ✅ |
| `CuentaCartera` | `CuentaCarteraType` | `PortfolioAccount` | `global_report_models.py` | ✅ |
| `CuentaCartera/Caracteristicas` | — | `PortfolioCharacteristics` | `global_report_models.py` | ✅ |
| `CuentaCartera/Valores/Valor` | — | `PortfolioValues` | `global_report_models.py` | ✅ |
| `CuentaCartera/Estados` | — | `PortfolioStates` | `global_report_models.py` | ✅ |
| *(colección)* | — | `GlobalReport` | `global_report_models.py` | ✅ |
| `CuentaAhorro` | `CuentaAhorroType` | `BankAccount` | `bank_account_models.py` | ✅ |
| `CuentaAhorro/Estado` | — | `BankAccountState` | `bank_account_models.py` | ✅ |
| `CuentaAhorro/Valores/Valor` | — | `BankAccountValue` | `bank_account_models.py` | ✅ |
| `CuentaCorriente` | `CuentaCorrienteType` | `CheckingAccount` | `checking_account_models.py` | ✅ |
| `TarjetaCredito` | `TarjetaCreditoType` | `CreditCard` | `credit_card_models.py` | ✅ |
| `TarjetaCredito/Caracteristicas` | — | `CreditCardCharacteristics` | `credit_card_models.py` | ✅ |
| `TarjetaCredito/Valores/Valor` | — | `CreditCardValues` | `credit_card_models.py` | ✅ |
| `TarjetaCredito/Estados` | — | `CreditCardStates` | `credit_card_models.py` | ✅ |
| `Consulta` | — | `QueryRecord` | `query_models.py` | ✅ |
| `EndeudamientoGlobal` | — | `GlobalDebtRecord` | `global_debt_models.py` | ✅ |
| `Score` | `ScoreType` | `ScoreRecord` | `score_alert_models.py` | ✅ |
| `Alerta` | `AlertaType` | `AlertRecord` | `score_alert_models.py` | ✅ |
| `InfoAgregada` | — | `AggregatedInfo` | `aggregated_info_models.py` | ✅ |
| `InfoAgregadaMicrocredito` | — | `MicroCreditAggregatedInfo` | `aggregated_info_models.py` | ✅ (pendiente split) |
| `FullReport` | *(resultado orquestado)* | `FullReport` | `full_report_models.py` | ✅ |

---

## Apéndice: Palabras reservadas y su uso exclusivo

Para evitar sobrecargar términos con múltiples significados en el proyecto:

| Palabra | Uso exclusivo en este proyecto |
|---|---|
| `Status` | Condición actual observable de un objeto (enum) |
| `State` | Grupo de campos de estado como sub-nodo XML (dataclass plural: `*States`) |
| `Type` | Categoría estructural de un objeto (enum o dataclass) |
| `Role` | Papel de un actor en una relación contractual (enum) |
| `Record` | Un registro de historial o auditoría (dataclass) |
| `Report` | Resultado completo de un builder (dataclass) |
| `Builder` | Clase que parsea XML y produce un dataclass (builder) |
| `Serialized` | Prefijo de TypedDicts (representación JSON-safe) |

