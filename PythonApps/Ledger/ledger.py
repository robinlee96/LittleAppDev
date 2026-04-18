
from datetime import datetime
from typing import Optional, Tuple
from models import Account, Transaction, TransactionType
from storage import StorageManager


class LedgerManager:
    def __init__(self, storage: StorageManager):
        self.storage = storage

    def add_income(self, account_id: str, amount: float, category: str, description: str = "") -> Optional[Transaction]:
        account = self.storage.get_account(account_id)
        if not account:
            return None
        if amount <= 0:
            return None

        transaction = Transaction(
            transaction_type=TransactionType.INCOME,
            amount=amount,
            category=category,
            description=description,
            account_id=account_id,
            created_at=datetime.now()
        )
        self.storage.add_transaction(transaction)

        new_balance = account.balance + amount
        self.storage.update_account(account_id, balance=new_balance)

        return transaction

    def add_expense(self, account_id: str, amount: float, category: str, description: str = "") -> Optional[Transaction]:
        account = self.storage.get_account(account_id)
        if not account:
            return None
        if amount <= 0:
            return None
        if account.balance < amount:
            return None

        transaction = Transaction(
            transaction_type=TransactionType.EXPENSE,
            amount=amount,
            category=category,
            description=description,
            account_id=account_id,
            created_at=datetime.now()
        )
        self.storage.add_transaction(transaction)

        new_balance = account.balance - amount
        self.storage.update_account(account_id, balance=new_balance)

        return transaction

    def transfer(self, from_account_id: str, to_account_id: str, amount: float, category: str = "转账", description: str = "") -> Optional[Transaction]:
        from_account = self.storage.get_account(from_account_id)
        to_account = self.storage.get_account(to_account_id)
        if not from_account or not to_account:
            return None
        if from_account_id == to_account_id:
            return None
        if amount <= 0:
            return None
        if from_account.balance < amount:
            return None

        transaction = Transaction(
            transaction_type=TransactionType.TRANSFER,
            amount=amount,
            category=category,
            description=description,
            account_id=from_account_id,
            target_account_id=to_account_id,
            created_at=datetime.now()
        )
        self.storage.add_transaction(transaction)

        new_from_balance = from_account.balance - amount
        self.storage.update_account(from_account_id, balance=new_from_balance)

        new_to_balance = to_account.balance + amount
        self.storage.update_account(to_account_id, balance=new_to_balance)

        return transaction

    def revert_transaction(self, transaction_id: str) -> bool:
        transaction = self.storage.get_transaction(transaction_id)
        if not transaction:
            return False

        if transaction.transaction_type == TransactionType.INCOME:
            account = self.storage.get_account(transaction.account_id)
            if account:
                new_balance = account.balance - transaction.amount
                self.storage.update_account(transaction.account_id, balance=new_balance)
        elif transaction.transaction_type == TransactionType.EXPENSE:
            account = self.storage.get_account(transaction.account_id)
            if account:
                new_balance = account.balance + transaction.amount
                self.storage.update_account(transaction.account_id, balance=new_balance)
        elif transaction.transaction_type == TransactionType.TRANSFER:
            from_account = self.storage.get_account(transaction.account_id)
            to_account = self.storage.get_account(transaction.target_account_id)
            if from_account and to_account:
                new_from_balance = from_account.balance + transaction.amount
                self.storage.update_account(transaction.account_id, balance=new_from_balance)
                new_to_balance = to_account.balance - transaction.amount
                self.storage.update_account(transaction.target_account_id, balance=new_to_balance)

        self.storage.delete_transaction(transaction_id)
        return True

    def get_account_balance(self, account_id: str) -> Optional[float]:
        account = self.storage.get_account(account_id)
        if account:
            return account.balance
        return None
