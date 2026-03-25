from dataclasses import dataclass
from typing import Optional

from data_adapter.xml_adapter.models.aggregated_info_models import AggregatedInfo, MicroCreditAggregatedInfo
from data_adapter.xml_adapter.models.bank_account_models import BankAccount
from data_adapter.xml_adapter.models.basic_data_models import BasicReport
from data_adapter.xml_adapter.models.checking_account_models import CheckingAccount
from data_adapter.xml_adapter.models.credit_card_models import CreditCard
from data_adapter.xml_adapter.models.global_debt_models import GlobalDebtRecord
from data_adapter.xml_adapter.models.global_report_models import PortfolioAccount
from data_adapter.xml_adapter.models.query_models import QueryRecord
from data_adapter.xml_adapter.models.score_alert_models import AlertRecord, ScoreRecord


@dataclass(frozen=True)
class FullReport:
    basic_data: BasicReport
    portfolio_accounts: tuple[PortfolioAccount, ...]
    bank_accounts: tuple[BankAccount, ...]
    checking_accounts: tuple[CheckingAccount, ...]
    credit_cards: tuple[CreditCard, ...]
    query_records: tuple[QueryRecord, ...]
    global_debt_records: tuple[GlobalDebtRecord, ...]
    aggregated_info: Optional[AggregatedInfo]
    micro_credit_info: Optional[MicroCreditAggregatedInfo]
    score_records: tuple[ScoreRecord, ...]
    alert_records: tuple[AlertRecord, ...]
