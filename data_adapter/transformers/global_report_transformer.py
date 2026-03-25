

from typing import Optional

from data_adapter.enums.financial_info.account_status import AccountStatus
from data_adapter.enums.financial_info.account_type import AccountType
from data_adapter.enums.financial_info.debtor_quality_portfolio import DebtorQualityPortfolio
from data_adapter.enums.financial_info.obligation_type import ObligationType
from data_adapter.enums.financial_info.payment_frequency import PaymentFrequency

def transform_account_type(value: Optional[str])->AccountType:
    if not value or value.strip() == "":
        return AccountType.UNKNOWN
    try:
        return AccountType[value]
    except KeyError:
        return AccountType.UNKNOWN


def transform_debtor_quality(value: Optional[str])->DebtorQualityPortfolio:
    if not value or value.strip() == "":
        return DebtorQualityPortfolio.UNKNOWN
    try:
        number_value = int(value)
        mapping = {
            0: DebtorQualityPortfolio.DEBTOR,
            1: DebtorQualityPortfolio.CO_DEBTOR,
            2: DebtorQualityPortfolio.CO_DEBTOR,
            3: DebtorQualityPortfolio.CO_DEBTOR,
            4: DebtorQualityPortfolio.CO_SINGER,
            5: DebtorQualityPortfolio.SOLIDARY_DEBTOR,
            6: DebtorQualityPortfolio.CO_TENANT,
            7: DebtorQualityPortfolio.OTHER_GUARANTORS,
            8: DebtorQualityPortfolio.GUARANTOR,
            9: DebtorQualityPortfolio.NOT_APPLICABLE,
            96: DebtorQualityPortfolio.CO_HOLDER,
            97: DebtorQualityPortfolio.COMMUNAL,
            99: DebtorQualityPortfolio.NOT_APPLICABLE
        }

        if number_value in mapping:
            return mapping[number_value]
        return DebtorQualityPortfolio.UNKNOWN
    except ValueError:
        return DebtorQualityPortfolio.UNKNOWN

def transform_payment_frequency(value: Optional[str])->PaymentFrequency:
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
            7: PaymentFrequency.OTHER
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
            8: ObligationType.PUBLIC
        }
        if number_value in mapping:
            return mapping[number_value]
        return ObligationType.UNKNOWN
    except ValueError:
        return ObligationType.UNKNOWN
    


def transform_status_account(value: Optional[str]) -> AccountStatus:
    if not value or value.strip() == "":
        return AccountStatus.UNKNOWN
    try:
        number_value = int(value)
        mapping = {
            0: AccountStatus.ENTITY_NO_REPORT,
            1: AccountStatus.ON_TIME,
            2: AccountStatus.OVERDUE_DEBT,
            3: AccountStatus.FULL_PAYMENT,
            4: AccountStatus.JUDICIAL_PAYMENT,
            5: AccountStatus.DOUBTFUL_COLLECTION,
            6: AccountStatus.WRITTEN_OFF,
            7: AccountStatus.DATION_IN_PAYMENT,
            8: AccountStatus.VOLUNTARY_CANCELLED,
            9: AccountStatus.CANCELLED_DUE_TO_MISMANAGEMENT,
            10: AccountStatus.CANCELLED_DUE_TO_STATUTE_OF_LIMITATIONS,
            11: AccountStatus.CANCELLED_BY_INSTITUTION,
        }
        if number_value in mapping:
            return mapping[number_value]
        return AccountStatus.UNKNOWN
    except ValueError:
        return AccountStatus.UNKNOWN