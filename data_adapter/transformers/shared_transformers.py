from typing import Optional

from data_adapter.enums.financial_info.account_state_savings import AccountStateSavings
from data_adapter.enums.financial_info.credit_rating import CreditRating
from data_adapter.enums.financial_info.currency import Currency
from data_adapter.enums.financial_info.current_debt_state import CurrentDebtState
from data_adapter.enums.financial_info.guarantee_type import GuaranteeType
from data_adapter.enums.financial_info.origin_state import OriginState
from data_adapter.enums.financial_info.ownership_situation import OwnershipSituation
from data_adapter.enums.financial_info.payment_behavior import PaymentBehavior
from data_adapter.enums.financial_info.payment_method import PaymentMethod
from data_adapter.enums.financial_info.payment_status import PaymentStatus
from data_adapter.enums.financial_info.query_reason import QueryReason
from data_adapter.enums.financial_info.sector import Sector


def transform_sector(value: Optional[str]) -> Sector:
    if not value or value.strip() == "":
        return Sector.UNKNOWN
    mapping = {
        "1": Sector.FINANCIAL,
        "2": Sector.COOPERATIVE,
        "3": Sector.REAL,
        "4": Sector.TELECOM,
        "0": Sector.UNKNOWN,
    }
    return mapping.get(value.strip(), Sector.UNKNOWN)


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


def transform_account_state_savings(value: Optional[str]) -> AccountStateSavings:
    if not value or value.strip() == "":
        return AccountStateSavings.UNKNOWN
    mapping = {
        "01": AccountStateSavings.ACTIVE,
        "02": AccountStateSavings.CANCELLED_BAD_USE,
        "05": AccountStateSavings.PAID_OFF,
        "06": AccountStateSavings.SEIZED,
        "07": AccountStateSavings.SEIZED_ACTIVE,
        "09": AccountStateSavings.INACTIVE,
        "00": AccountStateSavings.UNKNOWN,
    }
    return mapping.get(value.strip(), AccountStateSavings.UNKNOWN)


def transform_ownership_situation(value: Optional[str]) -> OwnershipSituation:
    if not value or value.strip() == "":
        return OwnershipSituation.UNKNOWN
    mapping = {
        "0": OwnershipSituation.NORMAL,
        "1": OwnershipSituation.CONCORDATO,
        "2": OwnershipSituation.FORCED_LIQUIDATION,
        "3": OwnershipSituation.VOLUNTARY_LIQUIDATION,
        "4": OwnershipSituation.REORGANIZATION,
        "5": OwnershipSituation.LAW_550,
        "6": OwnershipSituation.LAW_1116,
        "7": OwnershipSituation.OTHER,
        "99": OwnershipSituation.UNKNOWN,
    }
    return mapping.get(value.strip(), OwnershipSituation.UNKNOWN)


def transform_origin_state(value: Optional[str]) -> OriginState:
    if not value or value.strip() == "":
        return OriginState.UNKNOWN
    mapping = {
        "0": OriginState.NORMAL,
        "1": OriginState.RESTRUCTURED,
        "2": OriginState.REFINANCED,
        "3": OriginState.TRANSFERRED,
        "4": OriginState.PURCHASED,
        "99": OriginState.UNKNOWN,
    }
    return mapping.get(value.strip(), OriginState.UNKNOWN)


def transform_payment_method(value: Optional[str]) -> PaymentMethod:
    if not value or value.strip() == "":
        return PaymentMethod.UNKNOWN
    mapping = {
        "0": PaymentMethod.CURRENT,
        "1": PaymentMethod.VOLUNTARY,
        "2": PaymentMethod.EXECUTIVE,
        "3": PaymentMethod.PAYMENT_ORDER,
        "4": PaymentMethod.RESTRUCTURING,
        "5": PaymentMethod.DACION,
        "6": PaymentMethod.CESSION,
        "7": PaymentMethod.DONATION,
        "99": PaymentMethod.UNKNOWN,
    }
    return mapping.get(value.strip(), PaymentMethod.UNKNOWN)


def transform_currency(value: Optional[str]) -> Currency:
    if not value or value.strip() == "":
        return Currency.UNKNOWN
    mapping = {
        "1": Currency.LEGAL,
        "2": Currency.FOREIGN,
        "0": Currency.UNKNOWN,
    }
    return mapping.get(value.strip(), Currency.UNKNOWN)


def transform_guarantee(value: Optional[str]) -> GuaranteeType:
    """Transform guarantee code (Tabla 11) to GuaranteeType enum."""
    if not value or value.strip() == "":
        return GuaranteeType.UNKNOWN
    mapping: dict[str, GuaranteeType] = {
        "0": GuaranteeType.SIN_GARANTIA,
        "1": GuaranteeType.ADMISIBLE,
        "2": GuaranteeType.OTRAS_IDONEAS,
        "A": GuaranteeType.NO_IDONEA,
        "B": GuaranteeType.BIENES_RAICES,
        "C": GuaranteeType.OTRAS_PRENDAS,
        "D": GuaranteeType.PIGNORACION_RENTAS,
        "E": GuaranteeType.GARANTIA_SOBERANA,
        "F": GuaranteeType.CONTRATO_FIDUCIA,
        "G": GuaranteeType.FNG,
        "H": GuaranteeType.CARTA_CREDITO,
        "I": GuaranteeType.FAG,
        "J": GuaranteeType.PERSONAL,
        "K": GuaranteeType.LEASING_NO_INMOBILIARIO,
        "L": GuaranteeType.LEASING_INMOBILIARIO,
        "M": GuaranteeType.PRENDA_TITULO,
        "N": GuaranteeType.DEPOSITOS,
        "O": GuaranteeType.SEGURO_CREDITO,
    }
    return mapping.get(value.strip().upper(), GuaranteeType.UNKNOWN)


def transform_query_reason(value: Optional[str]) -> QueryReason:
    """Transform query reason code (Tabla 23) to QueryReason enum."""
    if not value or value.strip() == "":
        return QueryReason.UNKNOWN
    mapping: dict[str, QueryReason] = {
        "00": QueryReason.RAZON_DESCONOCIDA,
        "01": QueryReason.SOLICITUD_PRODUCTO,
        "02": QueryReason.REVISION_PORTAFOLIO_ENTIDAD,
        "03": QueryReason.REVISION_PORTAFOLIO_CIUDADANO,
        "04": QueryReason.SOLICITUD_PRODUCTO_B,
        "05": QueryReason.CONSULTA_INTERNET,
        "06": QueryReason.CONSULTA_CAS_VIRTUAL,
        "07": QueryReason.POR_DEFINIR_07,
        "08": QueryReason.POR_DEFINIR_08,
    }
    return mapping.get(value.strip(), QueryReason.UNKNOWN)


def transform_payment_status(value: Optional[str]) -> PaymentStatus:
    """Transform EstadoPago.codigo (Tabla 4) to PaymentStatus enum."""
    if not value or value.strip() == "":
        return PaymentStatus.UNKNOWN
    mapping: dict[str, PaymentStatus] = {
        "01": PaymentStatus.NORMAL,
        "04": PaymentStatus.MORA_60,
        "05": PaymentStatus.MORA_90,
        "06": PaymentStatus.MORA_120_MAS,
        "08": PaymentStatus.CASTIGADA,
        "12": PaymentStatus.DUDOSO_RECAUDO,
        "16": PaymentStatus.ACUERDO_PAGO,
        "20": PaymentStatus.MORA_30,
        "45": PaymentStatus.REESTRUCTURADA,
        "47": PaymentStatus.SALDO_A_FAVOR,
    }
    return mapping.get(value.strip(), PaymentStatus.UNKNOWN)


def transform_current_debt_state(value: Optional[str]) -> CurrentDebtState:
    """Transform free-text current_state from EndeudamientoActual to CurrentDebtState enum."""
    if not value or value.strip() == "":
        return CurrentDebtState.UNKNOWN
    v = value.strip().lower()
    if v == "al día" or v.startswith("al día") and "mora" not in v:
        return CurrentDebtState.AL_DIA
    if "castigada" in v or "castig" in v:
        return CurrentDebtState.CASTIGADA
    if "dudoso" in v:
        return CurrentDebtState.DUDOSO_RECAUDO
    if "mora 30" in v or "m 30" in v:
        return CurrentDebtState.MORA_30
    if "mora 60" in v or "m 60" in v:
        return CurrentDebtState.MORA_60
    if "mora 90" in v or "m 90" in v or "rm 90" in v:
        return CurrentDebtState.MORA_90
    if "mora 120" in v or "m 120" in v or "rm 120" in v:
        return CurrentDebtState.MORA_120
    return CurrentDebtState.UNKNOWN


def transform_payment_behavior_char(char: str) -> PaymentBehavior:
    """Transform a single behavior character (Tabla 5) to PaymentBehavior enum."""
    mapping: dict[str, PaymentBehavior] = {
        "N": PaymentBehavior.AL_DIA,
        "1": PaymentBehavior.MORA_30,
        "2": PaymentBehavior.MORA_60,
        "3": PaymentBehavior.MORA_90,
        "4": PaymentBehavior.MORA_120,
        "5": PaymentBehavior.MORA_150,
        "6": PaymentBehavior.MORA_180,
        "D": PaymentBehavior.DUDOSO_RECAUDO,
        "C": PaymentBehavior.CASTIGADA,
        "-": PaymentBehavior.SIN_INFORMACION,
        " ": PaymentBehavior.SIN_INFORMACION,
    }
    return mapping.get(char.upper(), PaymentBehavior.SIN_INFORMACION)
