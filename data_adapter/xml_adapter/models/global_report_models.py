from dataclasses import dataclass
from typing import Optional

# Account state codes (account_statement_code) that represent an open/active obligation.
# Source: Datacredito XSD Tabla 4 — vigente codes.
OPEN_ACCOUNT_CODES: frozenset[str] = frozenset({
    "01", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23",
    "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35",
    "36", "37", "38", "39", "40", "41", "45", "47",
})


@dataclass(frozen=True)
class PortfolioValues:
    """
    Financial status of a credit obligation.
    Reflects the <Valor> node within <Valores>.
    """
    date: Optional[str]
    currency_code: Optional[str]          # e.g., "1" for COP
    credit_rating: Optional[str]          # e.g., "A", "E", "-"
    outstanding_balance: Optional[float]  # Saldo vigente
    past_due_amount: Optional[float]      # Saldo en mora
    available_limit: Optional[float]      # Cupo disponible
    installment_value: Optional[float]    # Valor de la cuota
    missed_payments: Optional[int]        # Número de cuotas en mora
    days_past_due: Optional[int]          # Días de mora (DPD)
    total_installments: Optional[int]     # Plazo total
    installments_paid: Optional[int]      # Cuotas pagadas
    principal_amount: Optional[float]     # Valor inicial del crédito
    due_date: Optional[str]               # Fecha límite de pago
    payment_frequency: Optional[str]      # e.g., "1" for Monthly
    last_payment_date: Optional[str]      # Fecha del último pago de cuota


@dataclass(frozen=True)
class PortfolioStates:
    """
    Groups the three state sub-nodes within <Estados> of CuentaCartera:
    EstadoCuenta, EstadoOrigen, EstadoPago.
    """
    account_statement_code: Optional[str]
    account_statement_date: Optional[str]

    origin_state_code: Optional[str]
    origin_statement_date: Optional[str]

    payment_status_code: Optional[str]    # "20" = mora, "01" = al día, "45" = castigada
    payment_status_months: Optional[str]
    payment_status_date: Optional[str]


@dataclass(frozen=True)
class PortfolioCharacteristics:
    """
    Nodo <Caracteristicas>.
    debtor_quality: "00"=Principal, "01"=Codeudor (see codetables.py)
    """
    account_type: Optional[str]           # código crudo ej: "LBZ"=libranza, "EDU"=educativo
    obligation_type: Optional[str]       # código crudo
    contract_type: Optional[str]
    contract_execution: Optional[str]
    debtor_quality: Optional[str]        # "00"=Principal, "01"=Codeudor
    guarantee: Optional[str]
    permanence_months: Optional[int]     # mesesPermanencia


@dataclass(frozen=True)
class PortfolioAccount:
    """
    Represents a credit obligation node <CuentaCartera>.
    An individual may have multiple accounts within the XML report.
    """
    lender: str                          # Entidad (Banco, Cooperativa, etc.)
    account_number: str                  # Número de la obligación
    opened_date: Optional[str]           # Fecha de apertura
    maturity_date: Optional[str]         # Fecha de vencimiento del contrato
    
    # Historical monthly status (e.g., 'N'=Current, '1-6'=Past Due, 'C'=Charged-off)
    payment_history: Optional[str]       
    
    credit_rating: Optional[str]         # Calificación (usa el mismo nombre que en PortfolioValues)
    ownership_status: Optional[str]      # Situación del titular (Principal, Joint, etc.)
    is_blocked: bool                     # Indica si la cuenta está bloqueada
    city: Optional[str]
    dane_city_code: Optional[str]        # codigoDaneCiudad — DANE municipal code
    industry_sector: Optional[str]       # "1"=Financial, "3"=Real Sector
    default_probability: Optional[float] # PD (Probability of Default)
    subscriber_code: Optional[str]       # codSuscriptor — Datacredito internal subscriber code
    entity_id_type: Optional[str]        # tipoIdentificacion of the lending entity
    entity_id: Optional[str]             # identificacion (NIT) of the lending entity
    hd_rating: Optional[bool]            # calificacionHD flag

    # Relationships with other nodes
    characteristics: PortfolioCharacteristics
    values: PortfolioValues
    states: PortfolioStates

    @property
    def is_open(self) -> bool:
        """Return True if the account state code indicates an active obligation."""
        code = self.states.account_statement_code
        if code is None:
            return False
        return code in OPEN_ACCOUNT_CODES


@dataclass(frozen=True)
class GlobalReport:
    portfolio_account: tuple[PortfolioAccount, ...]