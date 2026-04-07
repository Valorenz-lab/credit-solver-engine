from typing import Optional

from data_adapter.debug_tracer import record_unknown
from data_adapter.enums.financial_info.credit_rating import CreditRating
from data_adapter.enums.financial_info.currency import Currency
from data_adapter.enums.financial_info.current_debt_status import CurrentDebtStatus
from data_adapter.enums.financial_info.guarantee_type import GuaranteeType
from data_adapter.enums.financial_info.industry_sector import IndustrySector
from data_adapter.enums.financial_info.origin_state import OriginState
from data_adapter.enums.financial_info.ownership_situation import OwnershipSituation
from data_adapter.enums.financial_info.payment_behavior import PaymentBehavior
from data_adapter.enums.financial_info.payment_method import PaymentMethod
from data_adapter.enums.financial_info.payment_status import PaymentStatus
from data_adapter.enums.financial_info.query_reason import QueryReason
from data_adapter.enums.financial_info.savings_account_status import (
    SavingsAccountStatus,
)


def transform_industry_sector(
    value: Optional[str],
    *,
    xml_node: str = "",
    xml_attribute: str = "sector",
    record_type: str = "",
    record_context: Optional[dict[str, str]] = None,
) -> IndustrySector:
    if not value or value.strip() == "":
        record_unknown(
            "transform_industry_sector",
            value,
            xml_node,
            xml_attribute,
            record_type,
            record_context or {},
        )
        return IndustrySector.UNKNOWN
    mapping: dict[str, IndustrySector] = {
        "1": IndustrySector.FINANCIAL,
        "2": IndustrySector.COOPERATIVE,
        "3": IndustrySector.REAL,
        "4": IndustrySector.TELECOM,
        "0": IndustrySector.UNKNOWN,
    }
    result = mapping.get(value.strip())
    if result is None:
        record_unknown(
            "transform_industry_sector",
            value,
            xml_node,
            xml_attribute,
            record_type,
            record_context or {},
        )
        return IndustrySector.UNKNOWN
    return result


def transform_credit_rating(value: Optional[str]) -> CreditRating:
    if not value or value.strip() == "":
        return CreditRating.UNKNOWN
    mapping = {
        "1": CreditRating.A,
        "2": CreditRating.B,
        "3": CreditRating.C,
        "4": CreditRating.D,
        "5": CreditRating.E,
        "6": CreditRating.AA,
        "7": CreditRating.BB,
        "8": CreditRating.CC,
        "9": CreditRating.K,
        "0": CreditRating.UNKNOWN,
    }
    return mapping.get(value.strip(), CreditRating.UNKNOWN)


def transform_savings_account_status(
    value: Optional[str],
    *,
    xml_node: str = "",
    xml_attribute: str = "codigo",
    record_type: str = "",
    record_context: Optional[dict[str, str]] = None,
) -> SavingsAccountStatus:
    if not value or value.strip() == "":
        record_unknown(
            "transform_savings_account_status",
            value,
            xml_node,
            xml_attribute,
            record_type,
            record_context or {},
        )
        return SavingsAccountStatus.UNKNOWN
    mapping: dict[str, SavingsAccountStatus] = {
        "01": SavingsAccountStatus.ACTIVE,
        "02": SavingsAccountStatus.CANCELLED_BAD_USE,
        "05": SavingsAccountStatus.PAID_OFF,
        "06": SavingsAccountStatus.SEIZED,
        "07": SavingsAccountStatus.SEIZED_ACTIVE,
        "09": SavingsAccountStatus.INACTIVE,
        "00": SavingsAccountStatus.UNKNOWN,
    }
    result = mapping.get(value.strip())
    if result is None:
        record_unknown(
            "transform_savings_account_status",
            value,
            xml_node,
            xml_attribute,
            record_type,
            record_context or {},
        )
        return SavingsAccountStatus.UNKNOWN
    return result


def transform_ownership_situation(
    value: Optional[str],
    *,
    xml_node: str = "",
    xml_attribute: str = "situacionTitular",
    record_type: str = "",
    record_context: Optional[dict[str, str]] = None,
) -> OwnershipSituation:
    if not value or value.strip() == "":
        record_unknown(
            "transform_ownership_situation",
            value,
            xml_node,
            xml_attribute,
            record_type,
            record_context or {},
        )
        return OwnershipSituation.UNKNOWN
    mapping: dict[str, OwnershipSituation] = {
        "0": OwnershipSituation.NORMAL,
        "1": OwnershipSituation.CONCORDAT,
        "2": OwnershipSituation.FORCED_LIQUIDATION,
        "3": OwnershipSituation.VOLUNTARY_LIQUIDATION,
        "4": OwnershipSituation.REORGANIZATION,
        "5": OwnershipSituation.LAW_550,
        "6": OwnershipSituation.LAW_1116,
        "7": OwnershipSituation.OTHER,
        "99": OwnershipSituation.UNKNOWN,
    }
    result = mapping.get(value.strip())
    if result is None:
        record_unknown(
            "transform_ownership_situation",
            value,
            xml_node,
            xml_attribute,
            record_type,
            record_context or {},
        )
        return OwnershipSituation.UNKNOWN
    return result


def transform_origin_state(
    value: Optional[str],
    *,
    xml_node: str = "EstadoOrigen",
    xml_attribute: str = "codigo",
    record_type: str = "",
    record_context: Optional[dict[str, str]] = None,
) -> OriginState:
    if not value or value.strip() == "":
        record_unknown(
            "transform_origin_state",
            value,
            xml_node,
            xml_attribute,
            record_type,
            record_context or {},
        )
        return OriginState.UNKNOWN
    mapping: dict[str, OriginState] = {
        "0": OriginState.NORMAL,
        "1": OriginState.RESTRUCTURED,
        "2": OriginState.REFINANCED,
        "3": OriginState.TRANSFERRED,
        "4": OriginState.PURCHASED,
        "99": OriginState.UNKNOWN,
        # Valores inferidos — pendientes de verificación con Tabla 44 (HDC 1.6.4)
        "5": OriginState.SPECIAL_REGIME,   # Banco Bogotá CAV vivienda — inferido
        "6": OriginState.PUBLIC_SERVICE,   # GASCARIBE servicio público — inferido
    }
    result = mapping.get(value.strip())
    if result is None:
        record_unknown(
            "transform_origin_state",
            value,
            xml_node,
            xml_attribute,
            record_type,
            record_context or {},
        )
        return OriginState.UNKNOWN
    return result


def transform_payment_method(
    value: Optional[str],
    *,
    xml_node: str = "TarjetaCredito",
    xml_attribute: str = "formaPago",
    record_type: str = "",
    record_context: Optional[dict[str, str]] = None,
) -> PaymentMethod:
    if not value or value.strip() == "":
        record_unknown(
            "transform_payment_method",
            value,
            xml_node,
            xml_attribute,
            record_type,
            record_context or {},
        )
        return PaymentMethod.UNKNOWN
    mapping = {
        "0": PaymentMethod.CURRENT,
        "1": PaymentMethod.VOLUNTARY,
        "2": PaymentMethod.EXECUTIVE,
        "3": PaymentMethod.PAYMENT_ORDER,
        "4": PaymentMethod.RESTRUCTURING,
        "5": PaymentMethod.DATION_IN_PAYMENT,
        "6": PaymentMethod.CESSION,
        "7": PaymentMethod.DONATION,
        "99": PaymentMethod.UNKNOWN,
    }
    result = mapping.get(value.strip())
    if result is None:
        record_unknown(
            "transform_payment_method",
            value,
            xml_node,
            xml_attribute,
            record_type,
            record_context or {},
        )
        return PaymentMethod.UNKNOWN
    return result


def transform_currency(value: Optional[str]) -> Currency:
    if not value or value.strip() == "":
        return Currency.UNKNOWN
    mapping = {
        "1": Currency.LEGAL,
        "2": Currency.FOREIGN,
        "0": Currency.UNKNOWN,
    }
    return mapping.get(value.strip(), Currency.UNKNOWN)


def transform_guarantee(
    value: Optional[str],
    *,
    xml_node: str = "Garantia",
    xml_attribute: str = "tipo",
    record_type: str = "",
    record_context: Optional[dict[str, str]] = None,
) -> GuaranteeType:
    """Transform guarantee code (Tabla 11) to GuaranteeType enum."""
    if not value or value.strip() == "":
        record_unknown(
            "transform_guarantee",
            value,
            xml_node,
            xml_attribute,
            record_type,
            record_context or {},
        )
        return GuaranteeType.UNKNOWN
    mapping: dict[str, GuaranteeType] = {
        "0": GuaranteeType.NO_GUARANTEE,
        "1": GuaranteeType.ADMISSIBLE,
        "2": GuaranteeType.OTHER_SUITABLE,
        "A": GuaranteeType.NOT_SUITABLE,
        "B": GuaranteeType.REAL_ESTATE,
        "C": GuaranteeType.OTHER_COLLATERAL,
        "D": GuaranteeType.REVENUE_PLEDGE,
        "E": GuaranteeType.SOVEREIGN_GUARANTEE,
        "F": GuaranteeType.TRUST_CONTRACT,
        "G": GuaranteeType.FNG,
        "H": GuaranteeType.LETTER_OF_CREDIT,
        "I": GuaranteeType.FAG,
        "J": GuaranteeType.PERSONAL,
        "K": GuaranteeType.NON_REAL_ESTATE_LEASING,
        "L": GuaranteeType.REAL_ESTATE_LEASING,
        "M": GuaranteeType.SECURITIES_PLEDGE,
        "N": GuaranteeType.CASH_DEPOSITS,
        "O": GuaranteeType.CREDIT_INSURANCE,
    }
    result = mapping.get(value.strip().upper())
    if result is None:
        record_unknown(
            "transform_guarantee",
            value,
            xml_node,
            xml_attribute,
            record_type,
            record_context or {},
        )
        return GuaranteeType.UNKNOWN
    return result


def transform_query_reason(
    value: Optional[str],
    *,
    xml_node: str = "Consulta",
    xml_attribute: str = "razon",
    record_type: str = "",
    record_context: Optional[dict[str, str]] = None,
) -> QueryReason:
    """Transform query reason code (Tabla 23) to QueryReason enum."""
    if not value or value.strip() == "":
        record_unknown(
            "transform_query_reason",
            value,
            xml_node,
            xml_attribute,
            record_type,
            record_context or {},
        )
        return QueryReason.UNKNOWN
    mapping: dict[str, QueryReason] = {
        "00": QueryReason.UNKNOWN_REASON,
        "01": QueryReason.PRODUCT_REQUEST_01,
        "02": QueryReason.ENTITY_PORTFOLIO_REVIEW,
        "03": QueryReason.CITIZEN_PORTFOLIO_REVIEW,
        "04": QueryReason.PRODUCT_REQUEST_04,
        "05": QueryReason.CITIZEN_INTERNET_QUERY,
        "06": QueryReason.CITIZEN_CAS_QUERY,
        "07": QueryReason.UNDEFINED_07,
        "08": QueryReason.UNDEFINED_08,
    }
    result = mapping.get(value.strip())
    if result is None:
        record_unknown(
            "transform_query_reason",
            value,
            xml_node,
            xml_attribute,
            record_type,
            record_context or {},
        )
        return QueryReason.UNKNOWN
    return result


def transform_payment_status(
    value: Optional[str],
    *,
    xml_node: str = "EstadoPago",
    xml_attribute: str = "codigo",
    record_type: str = "",
    record_context: Optional[dict[str, str]] = None,
) -> PaymentStatus:
    """Transform EstadoPago.codigo (Tabla 4) to PaymentStatus enum."""
    if not value or value.strip() == "":
        record_unknown(
            "transform_payment_status",
            value,
            xml_node,
            xml_attribute,
            record_type,
            record_context or {},
        )
        return PaymentStatus.UNKNOWN
    mapping: dict[str, PaymentStatus] = {
        "01": PaymentStatus.NORMAL,
        "04": PaymentStatus.PAST_DUE_60,
        "05": PaymentStatus.PAST_DUE_90,
        "06": PaymentStatus.PAST_DUE_120_PLUS,
        "08": PaymentStatus.WRITTEN_OFF,
        "12": PaymentStatus.DOUBTFUL_COLLECTION,
        "16": PaymentStatus.PAYMENT_AGREEMENT,
        "20": PaymentStatus.PAST_DUE_30,
        "45": PaymentStatus.RESTRUCTURED,
        "47": PaymentStatus.CREDIT_BALANCE,
        # Valores inferidos — pendientes de verificación con Tabla 4 (HDC 1.6.4)
        "14": PaymentStatus.CURRENT_NO_BALANCE,    # CLARO SERV MOV, EC=01, sin saldo — inferido
        "17": PaymentStatus.CLOSED_IN_ARREARS,     # CLARO TEC MOV, EC=02, mora $129k — inferido
        "19": PaymentStatus.EXTERNAL_COLLECTION,   # CREDIEXPRESS, EC=02, 100% mora — inferido
        "37": PaymentStatus.SEVERE_COLLECTION,     # BBVA tarjeta, EC=02, mora > saldo — inferido
        "41": PaymentStatus.JUDICIAL_COLLECTION,   # Bancolombia/CRJA/Coobolarqui, EC=02, 100% mora — inferido
    }
    result = mapping.get(value.strip(), PaymentStatus.UNKNOWN)
    if result is PaymentStatus.UNKNOWN:
        record_unknown(
            "transform_payment_status",
            value,
            xml_node,
            xml_attribute,
            record_type,
            record_context or {},
        )
    return result


def transform_current_debt_status(value: Optional[str]) -> CurrentDebtStatus:
    """Transform free-text estadoActual from EndeudamientoActual/Cuenta to CurrentDebtStatus.

    The XSD (InformeCliente-v1.6.xsd) define estadoActual como xs:string sin restricción
    de enumeración ni código numérico separado. El matching es heurístico sobre el texto
    normalizado (.strip().lower()).

    Valores observados en datos reales de Datacredito:
      "Al día"              → ON_TIME
      "Al día Mora 60"      → PAST_DUE_60  (al día pero con historial de mora 60)
      "Al día Mora 120"     → PAST_DUE_120
      "Esta en mora 30"     → PAST_DUE_30
      "Esta en mora 90"     → PAST_DUE_90
      "Esta en mora 120"    → PAST_DUE_120
      "Esta M 120 RM 90"    → PAST_DUE_90  (mora 120, referencia mora 90)
      "Esta M 120 RM 120"   → PAST_DUE_120
      "Dudoso recaudo"      → DOUBTFUL_COLLECTION
      "Cart. castigada"     → WRITTEN_OFF
      cualquier otro valor  → UNKNOWN
    """
    if not value or value.strip() == "":
        return CurrentDebtStatus.UNKNOWN
    v = value.strip().lower()
    if v.startswith("al día") and "mora" not in v:
        return CurrentDebtStatus.ON_TIME
    if "castigada" in v or "castig" in v:
        return CurrentDebtStatus.WRITTEN_OFF
    if "dudoso" in v:
        return CurrentDebtStatus.DOUBTFUL_COLLECTION
    if "mora 30" in v or "m 30" in v:
        return CurrentDebtStatus.PAST_DUE_30
    if "mora 60" in v or "m 60" in v:
        return CurrentDebtStatus.PAST_DUE_60
    if "mora 90" in v or "m 90" in v or "rm 90" in v:
        return CurrentDebtStatus.PAST_DUE_90
    if "mora 120" in v or "m 120" in v or "rm 120" in v:
        return CurrentDebtStatus.PAST_DUE_120
    return CurrentDebtStatus.UNKNOWN


def transform_payment_behavior_char(char: str) -> PaymentBehavior:
    """Transform a single behavior character (Tabla 5) to PaymentBehavior enum."""
    mapping: dict[str, PaymentBehavior] = {
        "N": PaymentBehavior.ON_TIME,
        "1": PaymentBehavior.PAST_DUE_30,
        "2": PaymentBehavior.PAST_DUE_60,
        "3": PaymentBehavior.PAST_DUE_90,
        "4": PaymentBehavior.PAST_DUE_120,
        "5": PaymentBehavior.PAST_DUE_150,
        "6": PaymentBehavior.PAST_DUE_180,
        "D": PaymentBehavior.DOUBTFUL_COLLECTION,
        "C": PaymentBehavior.WRITTEN_OFF,
        "-": PaymentBehavior.NO_INFORMATION,
        " ": PaymentBehavior.NO_INFORMATION,
    }
    return mapping.get(char.upper(), PaymentBehavior.NO_INFORMATION)
