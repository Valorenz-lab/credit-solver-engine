from typing import Optional, TypedDict

from data_adapter.enums.financial_info.debtor_quality_portfolio import DebtorQualityPortfolio
from data_adapter.enums.financial_info.obligation_type import ObligationType
from data_adapter.enums.financial_info.payment_frequency import PaymentFrequency
from data_adapter.xml_adapter.models.global_report_models import AccountStatus


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