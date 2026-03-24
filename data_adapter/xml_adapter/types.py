from typing import Any, Optional, TypedDict

from data_adapter.enums.financial_info.account_status import AccountStatus
from data_adapter.enums.financial_info.debtor_quality_portfolio import DebtorQualityPortfolio
from data_adapter.enums.financial_info.obligation_type import ObligationType
from data_adapter.enums.financial_info.payment_frequency import PaymentFrequency


class SerializedMetadata(TypedDict):
    query_date: str          
    answer: str
    cod_security: str
    type_id_entered: str
    id_typed: str
    last_name_typed: str


class SerializedCustomerIdentification(TypedDict):
    number: str
    state: str
    issue_date: Optional[str]
    city: Optional[str]
    department: Optional[str]
    gender: Optional[str]


class SerializedAge(TypedDict):
    min: Optional[int]
    max: Optional[int]


class SerializedPerson(TypedDict):
    names: str
    first_name: str
    last_name: Optional[str]
    full_name: str
    gender: Optional[str]
    validated: bool
    rut: bool
    # Sub-nodos
    customer_identification: SerializedCustomerIdentification
    age: SerializedAge


class SerializedReport(TypedDict):
    metadata: SerializedMetadata
    persona: SerializedPerson


###
#   Types for the internal representation of the XML report, used within the engine.
##

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

class SerializedAccountStatus(TypedDict):
    account_statement_code: Optional[AccountStatus]
    account_statement_date: Optional[str]

    origin_state_code: Optional[str]
    origin_statement_date: Optional[str]

    payment_status_code: Optional[str]   
    payment_status_months: Optional[str]
    payment_status_date: Optional[str]
    


class SerializedPortfolioCharacteristics(TypedDict):
    account_type: Optional[str]           
    obligation_type: Optional[ObligationType]       
    contract_type: Optional[str]
    contract_execution: Optional[str]
    debtor_quality: Optional[DebtorQualityPortfolio]     
    guarantee: Optional[str]


class SerializedPortfolioAccount(TypedDict):
    lender: Optional[str]
    account_number: Optional[str]
    opening_date: Optional[str]
    maturity_date: Optional[str]

    payment_history: Optional[str]
    
    credit_rating: Optional[str]
    ownership_status: Optional[str]
    is_blocked: Optional[bool]
    city: Optional[str]
    industry_sector: Optional[str]
    default_probability: Optional[float]

    characteristics: Optional[SerializedPortfolioCharacteristics]
    values: Optional[SerializedPortfolioValues]
    account_status: Optional[SerializedAccountStatus]


class SerializedGlobalReport(TypedDict):
    """
    Internal representation of the global report, with the data already extracted and organized.
    """
    portfolio_accounts: list[SerializedPortfolioAccount]


class SerializedBankAccountValue(TypedDict):
    currency_code: Optional[str]
    currency_label: Optional[str]
    date: Optional[str]
    rating: Optional[str]
    rating_label: Optional[str]


class SerializedBankAccountState(TypedDict):
    code: Optional[str]
    label: Optional[str]
    date: Optional[str]


class SerializedBankAccount(TypedDict):
    lender: str
    account_number: str
    account_class: Optional[str]
    opened_date: Optional[str]
    rating: Optional[str]
    rating_label: Optional[str]
    ownership_situation: Optional[str]
    ownership_situation_label: Optional[str]
    is_blocked: bool
    office: Optional[str]
    city: Optional[str]
    sector: Optional[str]
    sector_label: Optional[str]
    value: Optional[SerializedBankAccountValue]
    state: Optional[SerializedBankAccountState]


class SerializedCreditCardCharacteristics(TypedDict):
    franchise: Optional[str]
    franchise_label: Optional[str]
    card_class: Optional[str]
    card_class_label: Optional[str]
    brand: Optional[str]
    is_covered: bool
    covered_code: Optional[str]
    guarantee: Optional[str]


class SerializedCreditCardValues(TypedDict):
    currency_code: Optional[str]
    currency_label: Optional[str]
    date: Optional[str]
    rating: Optional[str]
    rating_label: Optional[str]
    outstanding_balance: Optional[float]
    past_due_amount: Optional[float]
    available_limit: Optional[float]
    installment_value: Optional[float]
    missed_payments: Optional[int]
    days_past_due: Optional[int]
    last_payment_date: Optional[str]
    due_date: Optional[str]
    total_credit_limit: Optional[float]


class SerializedCreditCardStates(TypedDict):
    plastic_state_code: Optional[str]
    plastic_state_label: Optional[str]
    plastic_state_date: Optional[str]
    account_state_code: Optional[str]
    account_state_date: Optional[str]
    origin_state_code: Optional[str]
    origin_state_label: Optional[str]
    origin_state_date: Optional[str]
    payment_status_code: Optional[str]
    payment_status_label: Optional[str]
    payment_status_months: Optional[str]
    payment_status_date: Optional[str]


class SerializedCreditCard(TypedDict):
    lender: str
    account_number: str
    opened_date: Optional[str]
    maturity_date: Optional[str]
    payment_history: Optional[str]
    payment_method: Optional[str]
    payment_method_label: Optional[str]
    default_probability: Optional[float]
    credit_rating: Optional[str]
    credit_rating_label: Optional[str]
    ownership_situation: Optional[str]
    ownership_situation_label: Optional[str]
    is_blocked: bool
    office: Optional[str]
    city: Optional[str]
    sector: Optional[str]
    sector_label: Optional[str]
    characteristics: SerializedCreditCardCharacteristics
    values: Optional[SerializedCreditCardValues]
    states: SerializedCreditCardStates


class SerializedQueryRecord(TypedDict):
    date: str
    account_type: Optional[str]
    entity: str
    office: Optional[str]
    city: Optional[str]
    reason: Optional[str]
    count: Optional[int]
    subscriber_nit: Optional[str]
    sector: Optional[str]
    sector_label: Optional[str]


class SerializedGlobalDebtEntity(TypedDict):
    name: str
    nit: Optional[str]
    sector: Optional[str]
    sector_label: Optional[str]


class SerializedGlobalDebt(TypedDict):
    rating: Optional[str]
    source: Optional[str]
    outstanding_balance: Optional[float]
    credit_type: Optional[str]
    credit_type_label: Optional[str]
    currency: Optional[str]
    credit_count: Optional[int]
    report_date: Optional[str]
    entity: SerializedGlobalDebtEntity


class SerializedAggregatedPrincipals(TypedDict):
    active_credits: int
    closed_credits: int
    current_negative: int
    negative_last_12m: int
    open_savings_checking: int
    closed_savings_checking: int
    queries_last_6m: int
    disputes_current: int
    oldest_account_date: Optional[str]
    active_claims: int


class SerializedSectorBalance(TypedDict):
    sector: str
    balance: float
    participation: float


class SerializedMonthlyBalance(TypedDict):
    date: str
    total_past_due: float
    total_balance: float


class SerializedMonthlyBehavior(TypedDict):
    date: str
    behavior: str
    count: int


class SerializedAggregatedBalances(TypedDict):
    total_past_due: float
    past_due_30: float
    past_due_60: float
    past_due_90: float
    monthly_installment: float
    highest_credit_balance: float
    total_balance: float
    by_sector: list[SerializedSectorBalance]
    monthly_history: list[SerializedMonthlyBalance]


class SerializedAggregatedSummaryInner(TypedDict):
    principals: SerializedAggregatedPrincipals
    balances: SerializedAggregatedBalances
    behavior_history: list[SerializedMonthlyBehavior]


class SerializedAccountTypeTotals(TypedDict):
    account_type_code: str
    account_type_label: str
    debtor_quality: str
    credit_limit: float
    balance: float
    past_due: float
    installment: float


class SerializedGrandTotal(TypedDict):
    debtor_quality: str
    participation: float
    credit_limit: float
    balance: float
    past_due: float
    installment: float


class SerializedPortfolioStateCount(TypedDict):
    state_code: str
    count: int


class SerializedPortfolioCompositionItem(TypedDict):
    account_type: str
    debtor_quality: str
    percentage: float
    count: int
    states: list[SerializedPortfolioStateCount]


class SerializedDebtEvolutionQuarter(TypedDict):
    date: str
    installment: Optional[int]
    total_credit_limit: Optional[int]
    balance: Optional[int]
    usage_percentage: Optional[float]
    rating: Optional[str]
    new_accounts: Optional[int]
    closed_accounts: Optional[int]
    total_open: Optional[int]
    total_closed: Optional[int]
    max_delinquency: Optional[str]
    max_delinquency_months: Optional[int]


class SerializedAggregatedSummary(TypedDict):
    summary: SerializedAggregatedSummaryInner
    account_totals: list[SerializedAccountTypeTotals]
    grand_totals: list[SerializedGrandTotal]
    portfolio_composition: list[SerializedPortfolioCompositionItem]
    debt_evolution: list[SerializedDebtEvolutionQuarter]


class SerializedFullReport(TypedDict):
    basic_info: SerializedReport
    general_profile: Optional[SerializedAggregatedSummary]
    global_summary: list[SerializedPortfolioAccount]
    open_bank_accounts: list[SerializedBankAccount]
    closed_bank_accounts: list[SerializedBankAccount]
    active_obligations: list[dict[str, Any]]
    payment_habits_open: dict[str, Any]
    payment_habits_closed: dict[str, Any]
    query_history: list[SerializedQueryRecord]
    global_debt_records: list[SerializedGlobalDebt]
    debt_evolution: list[SerializedDebtEvolutionQuarter]