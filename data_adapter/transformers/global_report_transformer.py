

from typing import Optional

from data_adapter.enums.financial_info.account_type import AccountType
from data_adapter.enums.financial_info.debtor_quality_portfolio import DebtorQualityPortfolio
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
            96: DebtorQualityPortfolio.CO_TITULAR,
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