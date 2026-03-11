from dataclasses import dataclass
from typing import Optional


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
class AccountStatus:
    """
    Nodos within <Estados>.
   account_statement_code "06" = charged-off portfolio, "01" = up to date, "02" = delinquent
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
    industry_sector: Optional[str]       # "1"=Financial, "3"=Real Sector
    default_probability: Optional[float] # PD (Probability of Default)

    # Relationships with other nodes
    characteristics: PortfolioCharacteristics
    values: PortfolioValues
    account_status: AccountStatus

@dataclass(frozen=True)
class GlobalReport:
    portfolio_account: tuple[PortfolioAccount, ...]