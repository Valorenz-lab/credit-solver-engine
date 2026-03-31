from dataclasses import dataclass
from typing import Optional

from data_adapter.enums.financial_info.account_condition import AccountCondition
from data_adapter.enums.financial_info.credit_card_class import CreditCardClass
from data_adapter.enums.financial_info.credit_card_franchise import CreditCardFranchise
from data_adapter.enums.financial_info.credit_rating import CreditRating
from data_adapter.enums.financial_info.currency import Currency
from data_adapter.enums.financial_info.guarantee_type import GuaranteeType
from data_adapter.enums.financial_info.industry_sector import IndustrySector
from data_adapter.enums.financial_info.origin_state import OriginState
from data_adapter.enums.financial_info.ownership_situation import OwnershipSituation
from data_adapter.enums.financial_info.payment_method import PaymentMethod
from data_adapter.enums.financial_info.payment_status import PaymentStatus
from data_adapter.enums.financial_info.plastic_status import PlasticStatus

_OPEN_CARD_CONDITIONS: frozenset[AccountCondition] = frozenset(
    {
        AccountCondition.ON_TIME,
        AccountCondition.OVERDUE_DEBT,
        AccountCondition.WRITTEN_OFF,
        AccountCondition.DOUBTFUL_COLLECTION,
    }
)


@dataclass(frozen=True)
class CreditCardCharacteristics:
    franchise: Optional[CreditCardFranchise]
    card_class: Optional[CreditCardClass]
    brand: Optional[str]
    is_covered: bool
    covered_code: Optional[str]
    guarantee: Optional[GuaranteeType]


@dataclass(frozen=True)
class CreditCardValues:
    currency_code: Optional[Currency]
    date: Optional[str]
    rating: Optional[CreditRating]
    outstanding_balance: Optional[float]
    past_due_amount: Optional[float]
    available_limit: Optional[float]
    installment_value: Optional[float]
    missed_payments: Optional[int]
    days_past_due: Optional[int]
    last_payment_date: Optional[str]
    due_date: Optional[str]
    total_credit_limit: Optional[float]


@dataclass(frozen=True)
class CreditCardStates:
    plastic_state_code: Optional[PlasticStatus]
    plastic_state_date: Optional[str]
    account_state_code: Optional[AccountCondition]
    account_state_date: Optional[str]
    origin_state_code: Optional[OriginState]
    origin_state_date: Optional[str]
    payment_status_code: Optional[PaymentStatus]
    payment_status_months: Optional[str]
    payment_status_date: Optional[str]


@dataclass(frozen=True)
class CreditCard:
    lender: str
    account_number: str
    opened_date: Optional[str]
    maturity_date: Optional[str]
    payment_history: Optional[str]
    payment_method: Optional[PaymentMethod]
    default_probability: Optional[float]
    credit_rating: Optional[CreditRating]
    ownership_situation: Optional[OwnershipSituation]
    is_blocked: bool
    office: Optional[str]
    city: Optional[str]
    dane_city_code: Optional[str]  # codigoDaneCiudad
    sector: Optional[IndustrySector]
    entity_id_type: Optional[str]  # tipoIdentificacion of the lending entity
    entity_id: Optional[str]  # identificacion (NIT) of the lending entity
    hd_rating: Optional[bool]  # calificacionHD flag
    characteristics: CreditCardCharacteristics
    values: Optional[CreditCardValues]
    states: CreditCardStates

    @property
    def is_open(self) -> bool:
        """Return True if the account state code indicates an active card."""
        condition = self.states.account_state_code
        if condition is None:
            return False
        return condition in _OPEN_CARD_CONDITIONS
