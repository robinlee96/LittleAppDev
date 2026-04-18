
import json
import os
from datetime import datetime
from typing import List, Optional, Dict
from models import Account, Transaction, AccountType, TransactionType, Category


def get_default_categories() -> List[Category]:
    categories = []
    
    expense_categories = [
        ("餐饮美食", ["早餐", "午餐", "晚餐", "零食", "外卖"]),
        ("交通出行", ["公交地铁", "出租车", "网约车", "加油", "停车"]),
        ("购物消费", ["服饰", "电子产品", "日用品", "家居用品"]),
        ("居住住房", ["房租", "水电燃气", "物业费"]),
        ("休闲娱乐", ["电影", "游戏", "旅游", "运动健身"]),
        ("医疗健康", ["药品", "体检", "医疗服务"]),
        ("教育培训", ["课程", "书籍", "考试"]),
        ("其他支出", [])
    ]
    
    for parent_name, children in expense_categories:
        parent = Category(name=parent_name, transaction_type=TransactionType.EXPENSE)
        categories.append(parent)
        for child_name in children:
            categories.append(Category(name=child_name, transaction_type=TransactionType.EXPENSE, parent_id=parent.id))
    
    income_categories = [
        ("工资薪金", ["基本工资", "奖金", "补贴"]),
        ("投资收益", ["利息", "股票", "基金"]),
        ("兼职收入", []),
        ("其他收入", [])
    ]
    
    for parent_name, children in income_categories:
        parent = Category(name=parent_name, transaction_type=TransactionType.INCOME)
        categories.append(parent)
        for child_name in children:
            categories.append(Category(name=child_name, transaction_type=TransactionType.INCOME, parent_id=parent.id))
    
    return categories


class StorageManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.accounts_file = os.path.join(data_dir, "accounts.json")
        self.transactions_file = os.path.join(data_dir, "transactions.json")
        self.categories_file = os.path.join(data_dir, "categories.json")
        self.accounts: List[Account] = []
        self.transactions: List[Transaction] = []
        self.categories: List[Category] = []
        self._ensure_data_dir()
        self._load_data()

    def _ensure_data_dir(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def _load_data(self):
        self.accounts = []
        if os.path.exists(self.accounts_file):
            with open(self.accounts_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    account = Account(
                        id=item["id"],
                        name=item["name"],
                        account_type=AccountType(item["account_type"]),
                        balance=item["balance"],
                        bank_name=item.get("bank_name"),
                        created_at=datetime.fromisoformat(item["created_at"]),
                        updated_at=datetime.fromisoformat(item["updated_at"])
                    )
                    self.accounts.append(account)

        self.transactions = []
        if os.path.exists(self.transactions_file):
            with open(self.transactions_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    transaction = Transaction(
                        id=item["id"],
                        transaction_type=TransactionType(item["transaction_type"]),
                        amount=item["amount"],
                        category_id=item.get("category_id"),
                        category=item["category"],
                        description=item["description"],
                        account_id=item["account_id"],
                        target_account_id=item.get("target_account_id"),
                        created_at=datetime.fromisoformat(item["created_at"])
                    )
                    self.transactions.append(transaction)

        self.categories = []
        if os.path.exists(self.categories_file):
            with open(self.categories_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    category = Category(
                        id=item["id"],
                        name=item["name"],
                        transaction_type=TransactionType(item["transaction_type"]),
                        parent_id=item.get("parent_id"),
                        created_at=datetime.fromisoformat(item["created_at"])
                    )
                    self.categories.append(category)
        else:
            self.categories = get_default_categories()
            self._save_data()

    def _save_data(self):
        accounts_data = []
        for account in self.accounts:
            accounts_data.append({
                "id": account.id,
                "name": account.name,
                "account_type": account.account_type.value,
                "balance": account.balance,
                "bank_name": account.bank_name,
                "created_at": account.created_at.isoformat(),
                "updated_at": account.updated_at.isoformat()
            })
        with open(self.accounts_file, "w", encoding="utf-8") as f:
            json.dump(accounts_data, f, ensure_ascii=False, indent=2)

        transactions_data = []
        for transaction in self.transactions:
            transactions_data.append({
                "id": transaction.id,
                "transaction_type": transaction.transaction_type.value,
                "amount": transaction.amount,
                "category_id": transaction.category_id,
                "category": transaction.category,
                "description": transaction.description,
                "account_id": transaction.account_id,
                "target_account_id": transaction.target_account_id,
                "created_at": transaction.created_at.isoformat()
            })
        with open(self.transactions_file, "w", encoding="utf-8") as f:
            json.dump(transactions_data, f, ensure_ascii=False, indent=2)

        categories_data = []
        for category in self.categories:
            categories_data.append({
                "id": category.id,
                "name": category.name,
                "transaction_type": category.transaction_type.value,
                "parent_id": category.parent_id,
                "created_at": category.created_at.isoformat()
            })
        with open(self.categories_file, "w", encoding="utf-8") as f:
            json.dump(categories_data, f, ensure_ascii=False, indent=2)

    def add_account(self, account: Account) -> Account:
        self.accounts.append(account)
        self._save_data()
        return account

    def update_account(self, account_id: str, **kwargs) -> Optional[Account]:
        for account in self.accounts:
            if account.id == account_id:
                for key, value in kwargs.items():
                    if hasattr(account, key):
                        setattr(account, key, value)
                account.updated_at = datetime.now()
                self._save_data()
                return account
        return None

    def delete_account(self, account_id: str) -> bool:
        for i, account in enumerate(self.accounts):
            if account.id == account_id:
                self.accounts.pop(i)
                self._save_data()
                return True
        return False

    def get_account(self, account_id: str) -> Optional[Account]:
        for account in self.accounts:
            if account.id == account_id:
                return account
        return None

    def get_all_accounts(self) -> List[Account]:
        return self.accounts.copy()

    def get_total_balance(self) -> float:
        return sum(account.balance for account in self.accounts)

    def add_transaction(self, transaction: Transaction) -> Transaction:
        self.transactions.append(transaction)
        self._save_data()
        return transaction

    def delete_transaction(self, transaction_id: str) -> bool:
        for i, transaction in enumerate(self.transactions):
            if transaction.id == transaction_id:
                self.transactions.pop(i)
                self._save_data()
                return True
        return False

    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        for transaction in self.transactions:
            if transaction.id == transaction_id:
                return transaction
        return None

    def get_all_transactions(self) -> List[Transaction]:
        return self.transactions.copy()

    def get_transactions_by_account(self, account_id: str) -> List[Transaction]:
        return [t for t in self.transactions if t.account_id == account_id or t.target_account_id == account_id]

    def add_category(self, category: Category) -> Category:
        self.categories.append(category)
        self._save_data()
        return category

    def delete_category(self, category_id: str) -> bool:
        for i, category in enumerate(self.categories):
            if category.id == category_id:
                self.categories.pop(i)
                self._save_data()
                return True
        return False

    def get_category(self, category_id: str) -> Optional[Category]:
        for category in self.categories:
            if category.id == category_id:
                return category
        return None

    def get_all_categories(self) -> List[Category]:
        return self.categories.copy()

    def get_categories_by_type(self, transaction_type: TransactionType) -> List[Category]:
        return [c for c in self.categories if c.transaction_type == transaction_type]

    def get_root_categories(self, transaction_type: TransactionType) -> List[Category]:
        return [c for c in self.categories if c.transaction_type == transaction_type and c.parent_id is None]

    def get_sub_categories(self, parent_id: str) -> List[Category]:
        return [c for c in self.categories if c.parent_id == parent_id]
