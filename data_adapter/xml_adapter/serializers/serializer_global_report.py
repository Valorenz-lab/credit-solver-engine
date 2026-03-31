"""
"""


from data_adapter.transformers.shared_transformers import transform_payment_behavior_char
from data_adapter.xml_adapter.models.global_report_models import GlobalReport, PortfolioAccount, PortfolioCharacteristics, PortfolioStates, PortfolioValues
from data_adapter.xml_adapter.types import SerializedGlobalReport, SerializedPortfolioAccount, SerializedPortfolioCharacteristics, SerializedPortfolioStates, SerializedPortfolioValues


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
        "payment_history_parsed": (
            [transform_payment_behavior_char(ch).value for ch in c.payment_history]
            if c.payment_history is not None
            else None
        ),

        "credit_rating": c.credit_rating.value if c.credit_rating else None,
        "ownership_status": c.ownership_status.value if c.ownership_status else None,
        "is_blocked": c.is_blocked,
        "city": c.city,
        "dane_city_code": c.dane_city_code,
        "industry_sector": c.industry_sector.value if c.industry_sector else None,
        "default_probability": c.default_probability,
        "subscriber_code": c.subscriber_code,
        "entity_id_type": c.entity_id_type,
        "entity_id": c.entity_id,
        "hd_rating": c.hd_rating,

        "characteristics": _serialize_characteristics(c.characteristics) if c.characteristics else None,
        "values": _serialize_value(c.values) if c.values else None,
        "states": _serialize_portfolio_states(c.states) if c.states else None,
    }


def _serialize_characteristics(c: PortfolioCharacteristics) -> SerializedPortfolioCharacteristics:
    return {
        "account_type": c.account_type.value if c.account_type else None,
        "obligation_type": c.obligation_type,
        "contract_type": c.contract_type.value if c.contract_type else None,
        "contract_execution": c.contract_execution,
        "debtor_quality": c.debtor_quality,
        "guarantee": c.guarantee.value if c.guarantee else None,
        "guarantee_label": c.guarantee.value if c.guarantee else None,
        "permanence_months": c.permanence_months,
    }

def _serialize_value(v: PortfolioValues) -> SerializedPortfolioValues:
    return {
        "date": v.date,
        "currency": v.currency_code.value if v.currency_code else None,
        "credit_rating": v.credit_rating.value if v.credit_rating else None,
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
        "payment_frequency": v.payment_frequency,
        "last_payment_date": v.last_payment_date,
    }


def _serialize_portfolio_states(e: PortfolioStates) -> SerializedPortfolioStates:
    return {
        "account_statement_code": e.account_statement_code,
        "account_statement_date": e.account_statement_date,

        "origin_state_code": e.origin_state_code.value if e.origin_state_code else None,
        "origin_statement_date": e.origin_statement_date,

        # Ambos campos emiten el label del enum. El código crudo XML (ej. "20") se descarta
        # en el builder al transformar a PaymentStatus. Si el engine necesita el código
        # crudo en el futuro, agregar payment_status_raw_code al modelo y al TypedDict.
        "payment_status_code": e.payment_status_code.value if e.payment_status_code else None,
        "payment_status_label": e.payment_status_code.value if e.payment_status_code else None,
        "payment_status_months": e.payment_status_months,
        "payment_status_date": e.payment_status_date,
    }