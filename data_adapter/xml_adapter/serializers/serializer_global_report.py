"""
"""


from data_adapter.transformers.global_report_transformer import transform_account_type, transform_debtor_quality, transform_obligation_type, transform_payment_frequency, transform_status_account
from data_adapter.xml_adapter.models.global_report_models import AccountStatus as AccountStatusModel, GlobalReport, PortfolioAccount, PortfolioCharacteristics, PortfolioValues
from data_adapter.xml_adapter.types import SerializedAccountStatus, SerializedGlobalReport, SerializedPortfolioAccount, SerializedPortfolioCharacteristics, SerializedPortfolioValues


def serialize_global_report(report: GlobalReport) -> SerializedGlobalReport:
    return {
        "portfolio_accounts": [_serialize_account(c) for c in report.portfolio_account],
    }

def _serialize_account(c: PortfolioAccount) -> SerializedPortfolioAccount:
    return {
        "lender": c.lender,
        "account_number": c.account_number,
        "opening_date": c.opened_date,
        "maturity_date": c.maturity_date,
        "payment_history": c.payment_history,
        
        "credit_rating": c.credit_rating,
        "ownership_status": c.ownership_status,
        "is_blocked": c.is_blocked,
        "city": c.city,
        "industry_sector": c.industry_sector,
        "default_probability": c.default_probability,
    
        "characteristics": _serialize_characteristics(c.characteristics) if c.characteristics else None,
        "values": _serialize_value(c.values) if c.values else None,
        "account_status": _serialize_account_status(c.account_status) if c.account_status else None,
    }


def _serialize_characteristics(c: PortfolioCharacteristics) -> SerializedPortfolioCharacteristics:
    return {
        "account_type": transform_account_type(c.account_type).value,           # ej: "LBZ", "EDU", "SFI"
        "obligation_type": transform_obligation_type(c.obligation_type),
        "contract_type": c.contract_type,
        "contract_execution": c.contract_execution,
        "debtor_quality": transform_debtor_quality(c.debtor_quality),     # "00"=Principal, "01"=Codeudor
        "guarantee": c.guarantee,
    }

def _serialize_value(v: PortfolioValues) -> SerializedPortfolioValues:
    return {
        "date": v.date,
        "currency": v.currency_code,
        "credit_rating": v.credit_rating,
        "outstanding_balance": v.outstanding_balance,
        "past_due_balance": v.past_due_amount,
        "available_limit": v.available_limit,
        "installment_value": v.installment_value,
        "missed_payments": v.missed_payments,
        "days_past_due": v.days_past_due,
        "total_installments": v.total_installments,
        "installments_paid": v.installments_paid,
        "principal_amount": v.principal_amount,
        "due_date": v.due_date,
        "payment_frequency": transform_payment_frequency(v.payment_frequency),
        "last_payment_date": v.last_payment_date,
    }


def _serialize_account_status(e: AccountStatusModel) -> SerializedAccountStatus:
    return {
       
        "account_statement_code": transform_status_account(e.account_statement_code),
        "account_statement_date": e.account_statement_date,

        "origin_state_code": e.origin_state_code,
        "origin_statement_date": e.origin_statement_date,

        "payment_status_code": e.payment_status_code,
        "payment_status_months": e.payment_status_months,
        "payment_status_date": e.payment_status_date,
    }