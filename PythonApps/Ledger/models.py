
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import uuid4


class AccountType(Enum):
    SAVINGS = "储蓄账户"
    NETWORK_PAYMENT = "网络支付账户"
    LOAN = "贷款账户"
    PROVIDENT_FUND = "公积金账户"


class TransactionType(Enum):
    INCOME = "收入"
    EXPENSE = "支出"
    TRANSFER = "转账"


@dataclass
class Account:
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    account_type: AccountType = AccountType.SAVINGS
    balance: float = 0.0
    bank_name: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Transaction:
    id: str = field(default_factory=lambda: str(uuid4()))
    transaction_type: TransactionType = TransactionType.EXPENSE
    amount: float = 0.0
    category: str = ""
    description: str = ""
    account_id: str = ""
    target_account_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
