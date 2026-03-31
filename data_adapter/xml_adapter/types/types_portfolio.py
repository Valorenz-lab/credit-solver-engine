from typing import Optional, TypedDict

from data_adapter.enums.financial_info.account_condition import AccountCondition
from data_adapter.enums.financial_info.debtor_role import DebtorRole
from data_adapter.enums.financial_info.obligation_type import ObligationType
from data_adapter.enums.financial_info.payment_frequency import PaymentFrequency


class SerializedPortfolioValues(TypedDict):
    date: Optional[str]
    currency: Optional[str]
    credit_rating: Optional[str]
    outstanding_balance: Optional[float]
    past_due_balance: Optional[float]
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


class SerializedPortfolioStates(TypedDict):
    account_statement_code: Optional[AccountCondition]
    account_statement_date: Optional[str]
    origin_state_code: Optional[str]
    origin_statement_date: Optional[str]
    payment_status_code: Optional[str]
    payment_status_label: Optional[str]
    payment_status_months: Optional[str]
    payment_status_date: Optional[str]


class SerializedPortfolioCharacteristics(TypedDict):
    account_type: Optional[str]
    obligation_type: Optional[ObligationType]
    contract_type: Optional[str]
    contract_execution: Optional[str]
    debtor_quality: Optional[DebtorRole]
    guarantee: Optional[str]
    guarantee_label: Optional[str]
    permanence_months: Optional[int]


class SerializedPortfolioAccount(TypedDict):
    lender: str
    account_number: str
    opening_date: Optional[str]
    maturity_date: Optional[str]
    payment_history: Optional[str]
    payment_history_parsed: Optional[list[str]]
    credit_rating: Optional[str]
    ownership_status: Optional[str]
    is_blocked: bool
    city: Optional[str]
    dane_city_code: Optional[str]
    industry_sector: Optional[str]
    default_probability: Optional[float]
    subscriber_code: Optional[str]
    entity_id_type: Optional[str]
    entity_id: Optional[str]
    hd_rating: Optional[bool]
    characteristics: Optional[SerializedPortfolioCharacteristics]
    values: Optional[SerializedPortfolioValues]
    states: Optional[SerializedPortfolioStates]


class SerializedGlobalReport(TypedDict):
    portfolio_accounts: list[SerializedPortfolioAccount]
