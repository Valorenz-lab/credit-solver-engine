from typing import Optional

from data_adapter.debug_tracer import record_unknown
from data_adapter.enums.financial_info.account_condition import AccountCondition
from data_adapter.enums.financial_info.account_type import AccountType
from data_adapter.enums.financial_info.contract_type import ContractType
from data_adapter.enums.financial_info.debtor_role import DebtorRole
from data_adapter.enums.financial_info.obligation_type import ObligationType
from data_adapter.enums.financial_info.payment_frequency import PaymentFrequency


def transform_account_type(
    value: Optional[str],
    *,
    xml_node: str = "",
    xml_attribute: str = "tipoCuenta",
    record_type: str = "",
    record_context: Optional[dict[str, str]] = None,
) -> AccountType:
    if not value or value.strip() == "":
        record_unknown(
            "transform_account_type",
            value,
            xml_node,
            xml_attribute,
            record_type,
            record_context or {},
        )
        return AccountType.UNKNOWN
    try:
        return AccountType[value]
    except KeyError:
        record_unknown(
            "transform_account_type",
            value,
            xml_node,
            xml_attribute,
            record_type,
            record_context or {},
        )
        return AccountType.UNKNOWN


def transform_debtor_role(value: Optional[str]) -> DebtorRole:
    if not value or value.strip() == "":
        return DebtorRole.UNKNOWN
    try:
        number_value = int(value)
        mapping = {
            0: DebtorRole.DEBTOR,
            1: DebtorRole.CO_DEBTOR,
            2: DebtorRole.CO_DEBTOR,
            3: DebtorRole.CO_DEBTOR,
            4: DebtorRole.CO_SINGER,
            5: DebtorRole.SOLIDARY_DEBTOR,
            6: DebtorRole.CO_TENANT,
            7: DebtorRole.OTHER_GUARANTORS,
            8: DebtorRole.GUARANTOR,
            9: DebtorRole.NOT_APPLICABLE,
            96: DebtorRole.CO_HOLDER,
            97: DebtorRole.COMMUNAL,
            99: DebtorRole.NOT_APPLICABLE,
        }

        if number_value in mapping:
            return mapping[number_value]
        return DebtorRole.UNKNOWN
    except ValueError:
        return DebtorRole.UNKNOWN


def transform_payment_frequency(value: Optional[str]) -> PaymentFrequency:
    if not value or value.strip() == "":
        return PaymentFrequency.UNKNOWN
    try:
        number_value = int(value)
        mapping = {
            0: PaymentFrequency.NO_INFORMED,
            1: PaymentFrequency.MONTHLY,
            2: PaymentFrequency.BIMONTHLY,
            3: PaymentFrequency.QUARTERLY,
            4: PaymentFrequency.BI_ANNUALLY,
            5: PaymentFrequency.ANNUALLY,
            6: PaymentFrequency.AT_EXPIRATION,
            7: PaymentFrequency.OTHER,
        }
        if number_value in mapping:
            return mapping[number_value]
        return PaymentFrequency.UNKNOWN
    except ValueError:
        return PaymentFrequency.UNKNOWN


def transform_obligation_type(value: Optional[str]) -> ObligationType:
    if not value or value.strip() == "":
        return ObligationType.UNKNOWN
    try:
        number_value = int(value)
        mapping = {
            0: ObligationType.NO_INFORMATION,
            1: ObligationType.COMMERCIAL,
            2: ObligationType.CONSUMPTION,
            3: ObligationType.MORTGAGE,
            4: ObligationType.OTHER,
            5: ObligationType.MICRO_CREDIT,
            6: ObligationType.PAYROLL_LOAN,
            7: ObligationType.INSURANCE,
            8: ObligationType.PUBLIC,
        }
        if number_value in mapping:
            return mapping[number_value]
        return ObligationType.UNKNOWN
    except ValueError:
        return ObligationType.UNKNOWN


def transform_account_condition(
    value: Optional[str],
    *,
    xml_node: str = "EstadoCuenta",
    xml_attribute: str = "codigo",
    record_type: str = "",
    record_context: Optional[dict[str, str]] = None,
) -> AccountCondition:
    """Transform EstadoCuenta.codigo (Tabla 4) to AccountCondition.

    Vigente codes: 01, 13-41, 45, 47
    Cerrada codes: 02-12, 46, 49
    """
    if not value or value.strip() == "":
        record_unknown(
            "transform_account_condition",
            value,
            xml_node,
            xml_attribute,
            record_type,
            record_context or {},
        )
        return AccountCondition.UNKNOWN
    mapping: dict[str, AccountCondition] = {
        # Vigente — Al día
        "01": AccountCondition.ON_TIME,
        "13": AccountCondition.ON_TIME,  # Al día, mora máx 30 días histórica
        "14": AccountCondition.ON_TIME,  # Al día, mora máx 60 días histórica
        "15": AccountCondition.ON_TIME,  # Al día, mora máx 90 días histórica
        "16": AccountCondition.ON_TIME,  # Al día, mora máx 120 días histórica
        # Vigente — En mora actual
        "17": AccountCondition.OVERDUE_DEBT,  # En mora 30 días
        "18": AccountCondition.OVERDUE_DEBT,  # En mora 60 días
        "19": AccountCondition.OVERDUE_DEBT,  # En mora 90 días
        "20": AccountCondition.OVERDUE_DEBT,  # En mora 120+ días
        # Vigente — Fue mora, está en mora (FM)
        "21": AccountCondition.OVERDUE_DEBT,
        "22": AccountCondition.OVERDUE_DEBT,
        "23": AccountCondition.OVERDUE_DEBT,
        "24": AccountCondition.OVERDUE_DEBT,
        "25": AccountCondition.OVERDUE_DEBT,
        "26": AccountCondition.OVERDUE_DEBT,
        # Vigente — Reincidencia en mora (RM)
        "27": AccountCondition.OVERDUE_DEBT,
        "28": AccountCondition.OVERDUE_DEBT,
        "29": AccountCondition.OVERDUE_DEBT,
        "30": AccountCondition.OVERDUE_DEBT,
        "31": AccountCondition.OVERDUE_DEBT,
        "32": AccountCondition.OVERDUE_DEBT,
        "33": AccountCondition.OVERDUE_DEBT,
        "34": AccountCondition.OVERDUE_DEBT,
        "35": AccountCondition.OVERDUE_DEBT,
        "36": AccountCondition.OVERDUE_DEBT,
        "37": AccountCondition.OVERDUE_DEBT,
        "38": AccountCondition.OVERDUE_DEBT,
        "39": AccountCondition.OVERDUE_DEBT,
        "40": AccountCondition.OVERDUE_DEBT,
        "41": AccountCondition.OVERDUE_DEBT,
        # Vigente — Estado especial
        "45": AccountCondition.WRITTEN_OFF,  # Cartera castigada
        "47": AccountCondition.DOUBTFUL_COLLECTION,  # Dudoso recaudo
        # Cerrada — Tarjeta
        "02": AccountCondition.CARD_NOT_DELIVERED,
        "04": AccountCondition.CARD_STOLEN,
        "07": AccountCondition.CARD_LOST,
        "49": AccountCondition.CARD_NOT_RENEWED,
        # Cerrada — Cancelación
        "03": AccountCondition.CANCELLED_DUE_TO_MISMANAGEMENT,
        "05": AccountCondition.VOLUNTARY_CANCELLED,
        "06": AccountCondition.CANCELLED_BY_INSTITUTION,
        # Cerrada — Pago total (variantes por mora máxima histórica)
        "08": AccountCondition.FULL_PAYMENT,
        "09": AccountCondition.FULL_PAYMENT,
        # EC=10 → Prescrita: documentado en sección Generalidades del Manual Insumos XML v1.6.4.
        # "Se declara probada la prescripción sobre una obligación dentro de un proceso judicial."
        # No es pago voluntario — es extinción judicial por prescripción (≤4 años impaga).
        # Se usa la Tabla 43 cuando EC=10 (ver sección 7.1.1 del manual).
        "10": AccountCondition.CANCELLED_DUE_TO_STATUTE_OF_LIMITATIONS,
        "11": AccountCondition.FULL_PAYMENT,
        "12": AccountCondition.FULL_PAYMENT,
        # Cerrada — Recuperación anormal (cobro judicial, embargo, arreglo)
        "46": AccountCondition.JUDICIAL_PAYMENT,
        # Vigente — En reclamación
        "60": AccountCondition.CLAIM_IN_PROGRESS,
        # Legacy — código pre-Tabla 4, presente en obligaciones cerradas anteriores a 2009
        "00": AccountCondition.LEGACY_CLOSED,
    }
    result = mapping.get(value.strip(), AccountCondition.UNKNOWN)
    if result is AccountCondition.UNKNOWN:
        record_unknown(
            "transform_account_condition",
            value,
            xml_node,
            xml_attribute,
            record_type,
            record_context or {},
        )
    return result


def transform_contract_type(value: Optional[str]) -> ContractType:
    """Transform tipoContrato code (Tabla 41) to ContractType.

    0 = No reportado, 1 = Definido (término fijo), 2 = Indefinido
    """
    if not value or value.strip() == "":
        return ContractType.UNKNOWN
    mapping: dict[str, ContractType] = {
        "0": ContractType.NOT_REPORTED,
        "1": ContractType.FIXED_TERM,
        "2": ContractType.INDEFINITE,
    }
    return mapping.get(value.strip(), ContractType.UNKNOWN)
