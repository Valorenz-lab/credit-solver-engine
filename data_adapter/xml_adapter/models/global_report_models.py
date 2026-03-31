from dataclasses import dataclass
from typing import Optional

from data_adapter.enums.financial_info.account_condition import AccountCondition
from data_adapter.enums.financial_info.account_type import AccountType
from data_adapter.enums.financial_info.contract_type import ContractType
from data_adapter.enums.financial_info.credit_rating import CreditRating
from data_adapter.enums.financial_info.currency import Currency
from data_adapter.enums.financial_info.debtor_role import DebtorRole
from data_adapter.enums.financial_info.guarantee_type import GuaranteeType
from data_adapter.enums.financial_info.industry_sector import IndustrySector
from data_adapter.enums.financial_info.obligation_type import ObligationType
from data_adapter.enums.financial_info.origin_state import OriginState
from data_adapter.enums.financial_info.ownership_situation import OwnershipSituation
from data_adapter.enums.financial_info.payment_frequency import PaymentFrequency
from data_adapter.enums.financial_info.payment_status import PaymentStatus

# AccountCondition values that represent an open/active obligation (Tabla 4 — vigente).
OPEN_ACCOUNT_CONDITIONS: frozenset[AccountCondition] = frozenset(
    {
        AccountCondition.ON_TIME,
        AccountCondition.OVERDUE_DEBT,
        AccountCondition.WRITTEN_OFF,
        AccountCondition.DOUBTFUL_COLLECTION,
        AccountCondition.CLAIM_IN_PROGRESS,  # código 60 — En reclamación (Vigente, Tabla 4)
    }
)


@dataclass(frozen=True)
class PortfolioValues:
    """
    Financial status of a credit obligation.
    Reflects the <Valor> node within <Valores>.
    """

    date: Optional[str]
    currency_code: Optional[Currency]
    credit_rating: Optional[CreditRating]
    outstanding_balance: Optional[float]
    past_due_amount: Optional[float]
    available_limit: Optional[float]
    installment_value: Optional[float]
    missed_payments: Optional[int]
    days_past_due: Optional[int]
    total_installments: Optional[int]
    installments_paid: Optional[int]
    principal_amount: Optional[float]
    due_date: Optional[str]
    payment_frequency: Optional[PaymentFrequency]
    last_payment_date: Optional[str]


@dataclass(frozen=True)
class PortfolioStates:
    """
    Groups the three state sub-nodes within <Estados> of CuentaCartera:
    EstadoCuenta, EstadoOrigen, EstadoPago.
    """

    account_statement_code: Optional[AccountCondition]
    account_statement_date: Optional[str]

    origin_state_code: Optional[OriginState]
    origin_statement_date: Optional[str]

    payment_status_code: Optional[PaymentStatus]
    payment_status_months: Optional[str]
    payment_status_date: Optional[str]


@dataclass(frozen=True)
class PortfolioCharacteristics:
    """Nodo <Caracteristicas>."""

    account_type: Optional[AccountType]
    obligation_type: Optional[ObligationType]
    contract_type: Optional[ContractType]
    contract_execution: Optional[str]
    debtor_quality: Optional[DebtorRole]
    guarantee: Optional[GuaranteeType]
    permanence_months: Optional[int]


@dataclass(frozen=True)
class PortfolioAccount:
    """
    Represents a credit obligation node <CuentaCartera>.
    An individual may have multiple accounts within the XML report.
    """

    lender: str  # Entidad (Banco, Cooperativa, etc.)
    account_number: str  # Número de la obligación
    opened_date: Optional[str]  # Fecha de apertura
    maturity_date: Optional[str]  # Fecha de vencimiento del contrato

    # Historical monthly status (e.g., 'N'=Current, '1-6'=Past Due, 'C'=Charged-off)
    payment_history: Optional[str]

    credit_rating: Optional[CreditRating]
    ownership_status: Optional[OwnershipSituation]
    is_blocked: bool
    city: Optional[str]
    dane_city_code: Optional[str]
    industry_sector: Optional[IndustrySector]
    default_probability: Optional[float]  # PD (Probability of Default)
    subscriber_code: Optional[
        str
    ]  # codSuscriptor — Datacredito internal subscriber code
    entity_id_type: Optional[str]  # tipoIdentificacion of the lending entity
    entity_id: Optional[str]  # identificacion (NIT) of the lending entity
    hd_rating: Optional[bool]  # calificacionHD flag

    # Relationships with other nodes
    characteristics: PortfolioCharacteristics
    values: PortfolioValues
    states: PortfolioStates

    @property
    def is_open(self) -> bool:
        """Return True if the account condition indicates an active obligation."""
        condition = self.states.account_statement_code
        if condition is None:
            return False
        return condition in OPEN_ACCOUNT_CONDITIONS


@dataclass(frozen=True)
class GlobalReport:
    portfolio_account: tuple[PortfolioAccount, ...]
