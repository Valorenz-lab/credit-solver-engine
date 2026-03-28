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

## 4. Inventario: tablas XSD → enums

Mapa completo de tablas de códigos del XSD v1.6 a sus enums Python actuales.

| Tabla XSD | Atributo XML | Nodo(s) | Enum actual | Nombre correcto | Archivo | Estado |
|---|---|---|---|---|---|---|
| Tabla 1 | `tipoIdentificacion` | múltiples | `IdentificationDocumentType` | `IdentificationDocumentType` | `basic_info/identification_document_type.py` | ✅ |
| Tabla 2 | `Identificacion.estado` | `NaturalNacional` | `IdentificationStatus` | `IdentificationStatus` | `basic_info/identification_status.py` | ✅ |
| — | `sexo` | `NaturalNacional` | `Gender` | `Gender` | `basic_info/gender.py` | ✅ |
| Tabla 3 | `tipoCuenta` | `CuentaCartera/Caracteristicas` | `AccountType` | `AccountType` | `financial_info/account_type.py` | ✅ |
| Tabla 4 | `EstadoCuenta.codigo` | `CuentaCartera/Estados`, `TarjetaCredito/Estados` | `AccountCondition` | `AccountCondition` | `financial_info/account_condition.py` | ✅ |
| Tabla 4 | `EstadoPago.codigo` | `CuentaCartera/Estados`, `TarjetaCredito/Estados` | `PaymentStatus` | `PaymentStatus` | `financial_info/payment_status.py` | ✅ |
| Tabla 5 | `comportamiento` (por carácter) | `CuentaCartera`, `TarjetaCredito` | `PaymentBehavior` | `PaymentBehavior` | `financial_info/payment_behavior.py` | ✅ |
| Tabla 6 | `calidadDeudor` | `CuentaCartera/Caracteristicas` | `DebtorRole` | `DebtorRole` | `financial_info/debtor_role.py` | ✅ |
| Tabla 6 | `amparada` / `codigoAmparada` | `TarjetaCredito/Caracteristicas` | `CardholderRole` | `CardholderRole` | `financial_info/cardholder_role.py` | ✅ |
| Tabla 9 | `tipoObligacion` | `CuentaCartera/Caracteristicas` | `ObligationType` | `ObligationType` | `financial_info/obligation_type.py` | ✅ |
| Tabla 10 | `moneda` | múltiples | `Currency` | `Currency` | `financial_info/currency.py` | ✅ |
| Tabla 11 | `garantia` | `CuentaCartera`, `TarjetaCredito`, `EndeudamientoGlobal` | `GuaranteeType` | `GuaranteeType` | `financial_info/guarantee_type.py` | ✅ |
| Tabla 14 | `calificacion` | `CuentaCartera`, `TarjetaCredito`, `EndeudamientoGlobal` | `CreditRating` | `CreditRating` | `financial_info/credit_rating.py` | ✅ |
| Tabla 16 | `Estado.codigo` | `CuentaAhorro`, `CuentaCorriente` | `SavingsAccountStatus` | `SavingsAccountStatus` | `financial_info/savings_account_status.py` | ✅ |
| Tabla 18 | `formaPago` | `CuentaCartera`, `TarjetaCredito` | `PaymentMethod` | `PaymentMethod` | `financial_info/payment_method.py` | ✅ |
| Tabla 23 | `Consulta.razon` | `Consulta` | `QueryReason` | `QueryReason` | `financial_info/query_reason.py` | ✅ |
| Tabla 29 | `situacionTitular` | `CuentaCartera`, `CuentaAhorro`, `TarjetaCredito` | `OwnershipSituation` | `OwnershipSituation` | `financial_info/ownership_situation.py` | ✅ |
| Tabla 36 | `clase` | `CuentaAhorro/Caracteristicas`, `CuentaCorriente/Caracteristicas` | *(sin enum)* | `AccountClass` | *(pendiente crear)* | ❌ Pendiente |
| Tabla 39 | `franquicia` | `TarjetaCredito/Caracteristicas` | `CreditCardFranchise` | `CreditCardFranchise` | `financial_info/credit_card_franchise.py` | ✅ |
| Tabla 40 | `clase` (tarjeta) | `TarjetaCredito/Caracteristicas` | `CreditCardClass` | `CreditCardClass` | `financial_info/credit_card_class.py` | ✅ |
| Tabla 41 | `tipoContrato` | `CuentaCartera/Caracteristicas` | `ContractType` | `ContractType` | `financial_info/contract_type.py` | ✅ |
| Tabla 42 | `EstadoPlastico.codigo` | `TarjetaCredito/Estados` | `PlasticStatus` | `PlasticStatus` | `financial_info/plastic_status.py` | ✅ |
| Tabla 44 | `EstadoOrigen.codigo` | `CuentaCartera/Estados`, `TarjetaCredito/Estados` | `OriginState` | `OriginState` | `financial_info/origin_state.py` | ✅ |
| — | `periodicidad` | `CuentaCartera/Valores/Valor` | `PaymentFrequency` | `PaymentFrequency` | `financial_info/payment_frequency.py` | ✅ |
| — | `sector` | múltiples | `IndustrySector` | `IndustrySector` | `financial_info/industry_sector.py` | ✅ |
| — | `EndeudamientoGlobal.tipoCuenta` | `EndeudamientoGlobal` | `GlobalDebtCreditType` | `GlobalDebtCreditType` | `financial_info/global_debt_credit_type.py` | ✅ (aceptable) |
| — | `currentState` (texto libre) | `EndeudamientoActual/Cuenta` | `CurrentDebtStatus` | `CurrentDebtStatus` | `financial_info/current_debt_status.py` | ✅ |

---

## 5. Cambios pendientes

Ordenados por impacto. Los marcados ⚠️ **BLOQUEANTE** deben resolverse antes del refactor de builders.

### 5.1 ~~Colisión crítica — `AccountStatus`~~ ✅ Resuelto

| Construcción | Nombre anterior | Nombre actual |
|---|---|---|
| Enum `StrEnum` | `AccountStatus` (`account_status.py`) | `AccountCondition` (`account_condition.py`) |
| Dataclass | `AccountStatus` en `global_report_models.py` | `PortfolioStates` |
| Campo en `PortfolioAccount` | `account_status: AccountStatus` | `states: PortfolioStates` |
| TypedDict | `SerializedAccountStatus` | `SerializedPortfolioStates` |
| Transformer | `transform_status_account` | `transform_account_condition` |

---

### 5.2 ~~Enums con nombre incorrecto~~ ✅ Resuelto

| Enum anterior | Enum actual | Archivo |
|---|---|---|
| `DebtorQualityPortfolio` | `DebtorRole` | `financial_info/debtor_role.py` |
| `CardHolder` | `CardholderRole` | `financial_info/cardholder_role.py` |
| `AccountStateSavings` | `SavingsAccountStatus` | `financial_info/savings_account_status.py` |
| `Sector` | `IndustrySector` | `financial_info/industry_sector.py` |
| `PlasticState` | `PlasticStatus` | `financial_info/plastic_status.py` |
| `CurrentDebtState` | `CurrentDebtStatus` | `financial_info/current_debt_status.py` |

---

### 5.3 Enum pendiente de crear

| Tabla XSD | Atributo XML | Nombre a crear | Nodos afectados |
|---|---|---|---|
| Tabla 36 | `clase` | `AccountClass` | `CuentaAhorro/Caracteristicas`, `CuentaCorriente/Caracteristicas` |

---

### 5.4 ~~Funciones de transformer con nombre incorrecto~~ ✅ Resuelto

| Función anterior | Función actual | Archivo |
|---|---|---|
| `transform_debtor_quality` | `transform_debtor_role` | `global_report_transformer.py` |
| `transform_account_state_savings` | `transform_savings_account_status` | `shared_transformers.py` |
| `transform_sector` | `transform_industry_sector` | `shared_transformers.py` |
| `transform_plastic_state` | `transform_plastic_status` | `credit_card_transformer.py` |
| `transform_current_debt_state` | `transform_current_debt_status` | `shared_transformers.py` |

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

