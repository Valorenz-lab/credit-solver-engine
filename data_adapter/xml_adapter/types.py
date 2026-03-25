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
    payment_status_label: Optional[str]
    payment_status_months: Optional[str]
    payment_status_date: Optional[str]
    


class SerializedPortfolioCharacteristics(TypedDict):
    account_type: Optional[str]
    obligation_type: Optional[ObligationType]
    contract_type: Optional[str]
    contract_execution: Optional[str]
    debtor_quality: Optional[DebtorQualityPortfolio]
    guarantee: Optional[str]
    guarantee_label: Optional[str]
    permanence_months: Optional[int]


class SerializedPortfolioAccount(TypedDict):
    lender: Optional[str]
    account_number: Optional[str]
    opening_date: Optional[str]
    maturity_date: Optional[str]

    payment_history: Optional[str]
    payment_history_parsed: Optional[list[str]]

    credit_rating: Optional[str]
    ownership_status: Optional[str]
    is_blocked: Optional[bool]
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
    dane_city_code: Optional[str]
    sector: Optional[str]
    sector_label: Optional[str]
    entity_id_type: Optional[str]
    entity_id: Optional[str]
    value: Optional[SerializedBankAccountValue]
    state: Optional[SerializedBankAccountState]


class SerializedCheckingAccountOverdraft(TypedDict):
    value: Optional[float]
    days: Optional[int]
    date: Optional[str]


class SerializedCheckingAccount(TypedDict):
    lender: str
    account_number: str
    account_class: Optional[str]
    opened_date: Optional[str]
    ownership_situation: Optional[str]
    ownership_situation_label: Optional[str]
    is_blocked: bool
    office: Optional[str]
    city: Optional[str]
    dane_city_code: Optional[str]
    sector: Optional[str]
    sector_label: Optional[str]
    subscriber_code: Optional[str]
    entity_id_type: Optional[str]
    entity_id: Optional[str]
    value: Optional[SerializedBankAccountValue]
    state: Optional[SerializedBankAccountState]
    overdraft: Optional[SerializedCheckingAccountOverdraft]


class SerializedCreditCardCharacteristics(TypedDict):
    franchise: Optional[str]
    franchise_label: Optional[str]
    card_class: Optional[str]
    card_class_label: Optional[str]
    brand: Optional[str]
    is_covered: bool
    covered_code: Optional[str]
    guarantee: Optional[str]
    guarantee_label: Optional[str]


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
    payment_history_parsed: Optional[list[str]]
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
    dane_city_code: Optional[str]
    sector: Optional[str]
    sector_label: Optional[str]
    entity_id_type: Optional[str]
    entity_id: Optional[str]
    hd_rating: Optional[bool]
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
    reason_label: Optional[str]
    count: Optional[int]
    subscriber_nit: Optional[str]
    sector: Optional[str]
    sector_label: Optional[str]


class SerializedGlobalDebtEntity(TypedDict):
    name: str
    nit: Optional[str]
    sector: Optional[str]
    sector_label: Optional[str]


class SerializedGlobalDebtGuarantee(TypedDict):
    guarantee_type: Optional[str]
    guarantee_type_label: Optional[str]
    value: Optional[float]
    date: Optional[str]


class SerializedGlobalDebt(TypedDict):
    rating: Optional[str]
    source: Optional[str]
    outstanding_balance: Optional[float]
    credit_type: Optional[str]
    credit_type_label: Optional[str]
    currency: Optional[str]
    credit_count: Optional[int]
    report_date: Optional[str]
    independent: Optional[str]
    entity: SerializedGlobalDebtEntity
    guarantee: Optional[SerializedGlobalDebtGuarantee]


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
    score: Optional[float]
    rating: Optional[str]
    new_accounts: Optional[int]
    closed_accounts: Optional[int]
    total_open: Optional[int]
    total_closed: Optional[int]
    max_delinquency: Optional[str]
    max_delinquency_months: Optional[int]


class SerializedDebtEvolutionAnalysis(TypedDict):
    installment_pct: Optional[float]
    total_credit_limit_pct: Optional[float]
    balance_pct: Optional[float]
    usage_percentage_pct: Optional[float]
    score: Optional[float]
    rating: Optional[str]
    new_accounts_pct: Optional[float]
    closed_accounts_pct: Optional[float]
    total_open_pct: Optional[float]
    total_closed_pct: Optional[float]
    max_delinquency: Optional[str]


class SerializedBalanceHistoryQuarter(TypedDict):
    date: str
    total_accounts: Optional[int]
    accounts_considered: Optional[int]
    balance: Optional[int]


class SerializedBalanceHistoryByType(TypedDict):
    account_type: str
    quarters: list[SerializedBalanceHistoryQuarter]


class SerializedQuarterlyDebtCartera(TypedDict):
    portfolio_type: str
    account_count: int
    value: float


class SerializedQuarterlyDebtSector(TypedDict):
    sector_name: str
    sector_code: Optional[str]
    admissible_guarantee: float
    other_guarantee: float
    portfolios: list[SerializedQuarterlyDebtCartera]


class SerializedQuarterlyDebtSummary(TypedDict):
    date: str
    sectors: list[SerializedQuarterlyDebtSector]


class SerializedAggregatedSummary(TypedDict):
    summary: SerializedAggregatedSummaryInner
    account_totals: list[SerializedAccountTypeTotals]
    grand_totals: list[SerializedGrandTotal]
    portfolio_composition: list[SerializedPortfolioCompositionItem]
    debt_evolution: list[SerializedDebtEvolutionQuarter]
    debt_evolution_analysis: Optional[SerializedDebtEvolutionAnalysis]
    balance_history_by_type: list[SerializedBalanceHistoryByType]
    quarterly_debt_summary: list[SerializedQuarterlyDebtSummary]


# ── MicroCredit TypedDicts ────────────────────────────────────────────────────

class SerializedSectorCreditCount(TypedDict):
    financial: int
    cooperative: int
    real: int
    telecom: int
    total_as_principal: int
    total_as_cosigner: int


class SerializedSectorAntiguedad(TypedDict):
    financial: Optional[str]
    cooperative: Optional[str]
    real: Optional[str]
    telecom: Optional[str]


class SerializedPerfilGeneral(TypedDict):
    active_credits: SerializedSectorCreditCount
    closed_credits: SerializedSectorCreditCount
    restructured_credits: SerializedSectorCreditCount
    refinanced_credits: SerializedSectorCreditCount
    queries_last_6m: SerializedSectorCreditCount
    disputes: SerializedSectorCreditCount
    oldest_account: SerializedSectorAntiguedad


class SerializedMonthlySaldosYMoras(TypedDict):
    date: str
    total_accounts_past_due: int
    past_due_balance: float
    total_balance: float
    max_delinquency_financial: Optional[str]
    max_delinquency_cooperative: Optional[str]
    max_delinquency_real: Optional[str]
    max_delinquency_telecom: Optional[str]
    max_delinquency_overall: Optional[str]
    accounts_past_due_30: Optional[int]
    accounts_past_due_60_plus: Optional[int]


class SerializedVectorSaldosYMoras(TypedDict):
    has_financial: bool
    has_cooperative: bool
    has_real: bool
    has_telecom: bool
    monthly_data: list[SerializedMonthlySaldosYMoras]


class SerializedCurrentDebtAccount(TypedDict):
    current_state: Optional[str]
    current_state_label: Optional[str]
    rating: Optional[str]
    initial_value: Optional[float]
    current_balance: Optional[float]
    past_due_balance: Optional[float]
    monthly_installment: Optional[float]
    has_negative_behavior: Optional[bool]
    total_portfolio_debt: Optional[float]


class SerializedCurrentDebtByUser(TypedDict):
    user_type: str
    accounts: list[SerializedCurrentDebtAccount]


class SerializedCurrentDebtByType(TypedDict):
    account_type: str
    by_user: list[SerializedCurrentDebtByUser]


class SerializedCurrentDebtBySector(TypedDict):
    sector_code: str
    by_type: list[SerializedCurrentDebtByType]


class SerializedBehaviorMonthlyChar(TypedDict):
    date: str
    behavior: Optional[str]
    behavior_label: Optional[str]


class SerializedAccountBehaviorVector(TypedDict):
    entity: str
    account_number: str
    account_type: str
    state: Optional[str]
    contains_data: bool
    monthly_chars: list[SerializedBehaviorMonthlyChar]
    max_delinquency_chars: list[SerializedBehaviorMonthlyChar]


class SerializedSectorBehaviorVector(TypedDict):
    sector_name: str
    accounts: list[SerializedAccountBehaviorVector]


class SerializedTrendDataPoint(TypedDict):
    value: float
    date: str


class SerializedTrendSeries(TypedDict):
    series_name: str
    data_points: list[SerializedTrendDataPoint]


class SerializedMicroCreditAggregatedInfo(TypedDict):
    general_profile: Optional[SerializedPerfilGeneral]
    vector_saldos_moras: Optional[SerializedVectorSaldosYMoras]
    current_debt_by_sector: list[SerializedCurrentDebtBySector]
    sector_behavior_vectors: list[SerializedSectorBehaviorVector]
    trend_series: list[SerializedTrendSeries]
    debt_evolution: list[SerializedDebtEvolutionQuarter]
    debt_evolution_analysis: Optional[SerializedDebtEvolutionAnalysis]


class SerializedScoreReason(TypedDict):
    code: str


class SerializedScoreRecord(TypedDict):
    score_type: str
    score_value: float
    classification: Optional[str]
    population_pct: Optional[int]
    date: str
    reasons: list[SerializedScoreReason]


class SerializedAlertSource(TypedDict):
    code: str
    name: Optional[str]


class SerializedAlertRecord(TypedDict):
    placed_date: str
    expiry_date: str
    cancelled_date: Optional[str]
    code: str
    text: Optional[str]
    source: Optional[SerializedAlertSource]


class SerializedFullReport(TypedDict):
    basic_info: SerializedReport
    general_profile: Optional[SerializedAggregatedSummary]
    global_summary: list[SerializedPortfolioAccount]
    open_bank_accounts: list[SerializedBankAccount]
    closed_bank_accounts: list[SerializedBankAccount]
    checking_accounts: list[SerializedCheckingAccount]
    active_obligations: list[dict[str, Any]]
    payment_habits_open: dict[str, Any]
    payment_habits_closed: dict[str, Any]
    query_history: list[SerializedQueryRecord]
    global_debt_records: list[SerializedGlobalDebt]
    debt_evolution: list[SerializedDebtEvolutionQuarter]
    micro_credit_info: Optional[SerializedMicroCreditAggregatedInfo]
    score_records: list[SerializedScoreRecord]
    alert_records: list[SerializedAlertRecord]