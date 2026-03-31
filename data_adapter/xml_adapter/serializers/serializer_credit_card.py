from data_adapter.transformers.shared_transformers import (
    transform_payment_behavior_char,
)
from data_adapter.xml_adapter.models.credit_card_models import (
    CreditCard,
    CreditCardCharacteristics,
    CreditCardStates,
    CreditCardValues,
)
from data_adapter.xml_adapter.types import (
    SerializedCreditCard,
    SerializedCreditCardCharacteristics,
    SerializedCreditCardStates,
    SerializedCreditCardValues,
)


def serialize_credit_card(card: CreditCard) -> SerializedCreditCard:
    return {
        "lender": card.lender,
        "account_number": card.account_number,
        "opened_date": card.opened_date,
        "maturity_date": card.maturity_date,
        "payment_history": card.payment_history,
        "payment_history_parsed": (
            [transform_payment_behavior_char(ch).value for ch in card.payment_history]
            if card.payment_history is not None
            else None
        ),
        "payment_method": card.payment_method.value if card.payment_method else None,
        "payment_method_label": (
            card.payment_method.value if card.payment_method else None
        ),
        "default_probability": card.default_probability,
        "credit_rating": card.credit_rating.value if card.credit_rating else None,
        "credit_rating_label": card.credit_rating.value if card.credit_rating else None,
        "ownership_situation": (
            card.ownership_situation.value if card.ownership_situation else None
        ),
        "ownership_situation_label": (
            card.ownership_situation.value if card.ownership_situation else None
        ),
        "is_blocked": card.is_blocked,
        "office": card.office,
        "city": card.city,
        "dane_city_code": card.dane_city_code,
        "sector": card.sector.value if card.sector else None,
        "sector_label": card.sector.value if card.sector else None,
        "entity_id_type": card.entity_id_type,
        "entity_id": card.entity_id,
        "hd_rating": card.hd_rating,
        "characteristics": _serialize_characteristics(card.characteristics),
        "values": _serialize_values(card.values) if card.values is not None else None,
        "states": _serialize_states(card.states),
    }


def _serialize_characteristics(
    c: CreditCardCharacteristics,
) -> SerializedCreditCardCharacteristics:
    return {
        "franchise": c.franchise.value if c.franchise else None,
        "franchise_label": c.franchise.value if c.franchise else None,
        "card_class": c.card_class.value if c.card_class else None,
        "card_class_label": c.card_class.value if c.card_class else None,
        "brand": c.brand,
        "is_covered": c.is_covered,
        "covered_code": c.covered_code,
        "guarantee": c.guarantee.value if c.guarantee else None,
        "guarantee_label": c.guarantee.value if c.guarantee else None,
    }


def _serialize_values(v: CreditCardValues) -> SerializedCreditCardValues:
    return {
        "currency_code": v.currency_code.value if v.currency_code else None,
        "currency_label": v.currency_code.value if v.currency_code else None,
        "date": v.date,
        "rating": v.rating.value if v.rating else None,
        "rating_label": v.rating.value if v.rating else None,
        "outstanding_balance": v.outstanding_balance,
        "past_due_amount": v.past_due_amount,
        "available_limit": v.available_limit,
        "installment_value": v.installment_value,
        "missed_payments": v.missed_payments,
        "days_past_due": v.days_past_due,
        "last_payment_date": v.last_payment_date,
        "due_date": v.due_date,
        "total_credit_limit": v.total_credit_limit,
    }


def _serialize_states(s: CreditCardStates) -> SerializedCreditCardStates:
    return {
        "plastic_state_code": (
            s.plastic_state_code.value if s.plastic_state_code else None
        ),
        "plastic_state_label": (
            s.plastic_state_code.value if s.plastic_state_code else None
        ),
        "plastic_state_date": s.plastic_state_date,
        "account_state_code": (
            s.account_state_code.value if s.account_state_code else None
        ),
        "account_state_date": s.account_state_date,
        "origin_state_code": s.origin_state_code.value if s.origin_state_code else None,
        "origin_state_label": (
            s.origin_state_code.value if s.origin_state_code else None
        ),
        "origin_state_date": s.origin_state_date,
        "payment_status_code": (
            s.payment_status_code.value if s.payment_status_code else None
        ),
        "payment_status_label": (
            s.payment_status_code.value if s.payment_status_code else None
        ),
        "payment_status_months": s.payment_status_months,
        "payment_status_date": s.payment_status_date,
    }
