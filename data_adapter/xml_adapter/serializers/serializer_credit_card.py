from typing import Optional

from data_adapter.transformers.credit_card_transformer import (
    transform_credit_card_class,
    transform_franchise,
    transform_plastic_state,
)
from data_adapter.transformers.shared_transformers import (
    transform_credit_rating,
    transform_guarantee,
    transform_origin_state,
    transform_ownership_situation,
    transform_payment_behavior_char,
    transform_payment_method,
    transform_payment_status,
    transform_sector,
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
        "payment_method": card.payment_method,
        "payment_method_label": transform_payment_method(card.payment_method).value,
        "default_probability": card.default_probability,
        "credit_rating": card.credit_rating,
        "credit_rating_label": transform_credit_rating(card.credit_rating).value,
        "ownership_situation": card.ownership_situation,
        "ownership_situation_label": transform_ownership_situation(card.ownership_situation).value,
        "is_blocked": card.is_blocked,
        "office": card.office,
        "city": card.city,
        "dane_city_code": card.dane_city_code,
        "sector": card.sector,
        "sector_label": transform_sector(card.sector).value,
        "entity_id_type": card.entity_id_type,
        "entity_id": card.entity_id,
        "hd_rating": card.hd_rating,
        "characteristics": _serialize_characteristics(card.characteristics),
        "values": _serialize_values(card.values) if card.values is not None else None,
        "states": _serialize_states(card.states),
    }


def _serialize_characteristics(c: CreditCardCharacteristics) -> SerializedCreditCardCharacteristics:
    return {
        "franchise": c.franchise,
        "franchise_label": transform_franchise(c.franchise).value,
        "card_class": c.card_class,
        "card_class_label": transform_credit_card_class(c.card_class).value,
        "brand": c.brand,
        "is_covered": c.is_covered,
        "covered_code": c.covered_code,
        "guarantee": c.guarantee,
        "guarantee_label": transform_guarantee(c.guarantee).value,
    }


def _serialize_values(v: CreditCardValues) -> SerializedCreditCardValues:
    return {
        "currency_code": v.currency_code,
        "currency_label": None,
        "date": v.date,
        "rating": v.rating,
        "rating_label": transform_credit_rating(v.rating).value,
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
        "plastic_state_code": s.plastic_state_code,
        "plastic_state_label": transform_plastic_state(s.plastic_state_code).value,
        "plastic_state_date": s.plastic_state_date,
        "account_state_code": s.account_state_code,
        "account_state_date": s.account_state_date,
        "origin_state_code": s.origin_state_code,
        "origin_state_label": transform_origin_state(s.origin_state_code).value,
        "origin_state_date": s.origin_state_date,
        "payment_status_code": s.payment_status_code,
        "payment_status_label": transform_payment_status(s.payment_status_code).value,
        "payment_status_months": s.payment_status_months,
        "payment_status_date": s.payment_status_date,
    }
