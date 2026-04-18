
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Optional
from models import Account, AccountType, TransactionType
from storage import StorageManager
from ledger import LedgerManager


class LedgerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("记账本")
        self.root.geometry("1000x700")

        self.storage = StorageManager()
        self.ledger = LedgerManager(self.storage)

        self.current_account_id: Optional[str] = None

        self._create_widgets()
        self._refresh_data()

    def _create_widgets(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tab_accounts = ttk.Frame(notebook)
        self.tab_transactions = ttk.Frame(notebook)
        self.tab_ledger = ttk.Frame(notebook)

        notebook.add(self.tab_accounts, text="账户管理")
        notebook.add(self.tab_ledger, text="动账记录")
        notebook.add(self.tab_transactions, text="交易历史")

        self._create_accounts_tab()
        self._create_ledger_tab()
        self._create_transactions_tab()

    def _create_accounts_tab(self):
        frame_input = ttk.LabelFrame(self.tab_accounts, text="添加/编辑账户", padding=10)
        frame_input.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(frame_input, text="账户名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_account_name = ttk.Entry(frame_input, width=30)
        self.entry_account_name.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_input, text="账户类型:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.combo_account_type = ttk.Combobox(frame_input, values=[t.value for t in AccountType], state="readonly", width=27)
        self.combo_account_type.current(0)
        self.combo_account_type.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame_input, text="初始余额:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entry_account_balance = ttk.Entry(frame_input, width=30)
        self.entry_account_balance.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(frame_input, text="银行/机构:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.entry_bank_name = ttk.Entry(frame_input, width=30)
        self.entry_bank_name.grid(row=3, column=1, padx=5, pady=5)

        frame_buttons = ttk.Frame(frame_input)
        frame_buttons.grid(row=4, column=0, columnspan=2, pady=10)
        self.btn_add_account = ttk.Button(frame_buttons, text="添加账户", command=self._add_account)
        self.btn_add_account.pack(side=tk.LEFT, padx=5)
        self.btn_clear_account = ttk.Button(frame_buttons, text="清空", command=self._clear_account_form)
        self.btn_clear_account.pack(side=tk.LEFT, padx=5)

        frame_list = ttk.LabelFrame(self.tab_accounts, text="账户列表", padding=10)
        frame_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ("name", "type", "balance", "bank", "created")
        self.tree_accounts = ttk.Treeview(frame_list, columns=columns, show="headings", selectmode="browse")
        self.tree_accounts.heading("name", text="账户名称")
        self.tree_accounts.heading("type", text="账户类型")
        self.tree_accounts.heading("balance", text="当前余额")
        self.tree_accounts.heading("bank", text="银行/机构")
        self.tree_accounts.heading("created", text="创建时间")

        self.tree_accounts.column("name", width=150)
        self.tree_accounts.column("type", width=120)
        self.tree_accounts.column("balance", width=120)
        self.tree_accounts.column("bank", width=150)
        self.tree_accounts.column("created", width=180)

        scrollbar = ttk.Scrollbar(frame_list, orient=tk.VERTICAL, command=self.tree_accounts.yview)
        self.tree_accounts.configure(yscrollcommand=scrollbar.set)

        self.tree_accounts.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        frame_actions = ttk.Frame(frame_list)
        frame_actions.pack(fill=tk.X, pady=10)
        ttk.Button(frame_actions, text="删除选中账户", command=self._delete_account).pack(side=tk.RIGHT)

    def _create_ledger_tab(self):
        frame_select = ttk.LabelFrame(self.tab_ledger, text="选择账户", padding=10)
        frame_select.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(frame_select, text="当前账户:").pack(side=tk.LEFT, padx=5)
        self.combo_select_account = ttk.Combobox(frame_select, state="readonly", width=40)
        self.combo_select_account.pack(side=tk.LEFT, padx=5)
        self.combo_select_account.bind("<<ComboboxSelected>>", self._on_account_selected)

        self.label_balance = ttk.Label(frame_select, text="余额: --", font=("Arial", 12, "bold"))
        self.label_balance.pack(side=tk.LEFT, padx=20)

        notebook_ledger = ttk.Notebook(self.tab_ledger)
        notebook_ledger.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tab_income = ttk.Frame(notebook_ledger)
        self.tab_expense = ttk.Frame(notebook_ledger)
        self.tab_transfer = ttk.Frame(notebook_ledger)

        notebook_ledger.add(self.tab_income, text="收入")
        notebook_ledger.add(self.tab_expense, text="支出")
        notebook_ledger.add(self.tab_transfer, text="转账")

        self._create_income_widgets()
        self._create_expense_widgets()
        self._create_transfer_widgets()

    def _create_income_widgets(self):
        frame = ttk.Frame(self.tab_income, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="金额:").grid(row=0, column=0, sticky=tk.W, pady=10)
        self.entry_income_amount = ttk.Entry(frame, width=30)
        self.entry_income_amount.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(frame, text="类别:").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.entry_income_category = ttk.Entry(frame, width=30)
        self.entry_income_category.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(frame, text="备注:").grid(row=2, column=0, sticky=tk.W, pady=10)
        self.entry_income_desc = ttk.Entry(frame, width=30)
        self.entry_income_desc.grid(row=2, column=1, padx=10, pady=10)

        ttk.Button(frame, text="记录收入", command=self._add_income).grid(row=3, column=0, columnspan=2, pady=20)

    def _create_expense_widgets(self):
        frame = ttk.Frame(self.tab_expense, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="金额:").grid(row=0, column=0, sticky=tk.W, pady=10)
        self.entry_expense_amount = ttk.Entry(frame, width=30)
        self.entry_expense_amount.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(frame, text="类别:").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.entry_expense_category = ttk.Entry(frame, width=30)
        self.entry_expense_category.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(frame, text="备注:").grid(row=2, column=0, sticky=tk.W, pady=10)
        self.entry_expense_desc = ttk.Entry(frame, width=30)
        self.entry_expense_desc.grid(row=2, column=1, padx=10, pady=10)

        ttk.Button(frame, text="记录支出", command=self._add_expense).grid(row=3, column=0, columnspan=2, pady=20)

    def _create_transfer_widgets(self):
        frame = ttk.Frame(self.tab_transfer, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="金额:").grid(row=0, column=0, sticky=tk.W, pady=10)
        self.entry_transfer_amount = ttk.Entry(frame, width=30)
        self.entry_transfer_amount.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(frame, text="转入账户:").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.combo_transfer_to = ttk.Combobox(frame, state="readonly", width=27)
        self.combo_transfer_to.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(frame, text="备注:").grid(row=2, column=0, sticky=tk.W, pady=10)
        self.entry_transfer_desc = ttk.Entry(frame, width=30)
        self.entry_transfer_desc.grid(row=2, column=1, padx=10, pady=10)

        ttk.Button(frame, text="执行转账", command=self._transfer).grid(row=3, column=0, columnspan=2, pady=20)

    def _create_transactions_tab(self):
        frame_filter = ttk.Frame(self.tab_transactions, padding=10)
        frame_filter.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(frame_filter, text="刷新", command=self._refresh_transactions).pack(side=tk.RIGHT)

        frame_list = ttk.LabelFrame(self.tab_transactions, text="交易历史", padding=10)
        frame_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ("type", "amount", "category", "description", "account", "date")
        self.tree_transactions = ttk.Treeview(frame_list, columns=columns, show="headings", selectmode="browse")
        self.tree_transactions.heading("type", text="类型")
        self.tree_transactions.heading("amount", text="金额")
        self.tree_transactions.heading("category", text="类别")
        self.tree_transactions.heading("description", text="备注")
        self.tree_transactions.heading("account", text="账户")
        self.tree_transactions.heading("date", text="时间")

        self.tree_transactions.column("type", width=80)
        self.tree_transactions.column("amount", width=100)
        self.tree_transactions.column("category", width=100)
        self.tree_transactions.column("description", width=200)
        self.tree_transactions.column("account", width=150)
        self.tree_transactions.column("date", width=160)

        scrollbar = ttk.Scrollbar(frame_list, orient=tk.VERTICAL, command=self.tree_transactions.yview)
        self.tree_transactions.configure(yscrollcommand=scrollbar.set)

        self.tree_transactions.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        frame_actions = ttk.Frame(frame_list)
        frame_actions.pack(fill=tk.X, pady=10)
        ttk.Button(frame_actions, text="撤销选中交易", command=self._revert_transaction).pack(side=tk.RIGHT)

    def _refresh_data(self):
        self._refresh_accounts()
        self._refresh_transactions()
        self._refresh_account_combos()

    def _refresh_accounts(self):
        for item in self.tree_accounts.get_children():
            self.tree_accounts.delete(item)
        for account in self.storage.get_all_accounts():
            self.tree_accounts.insert("", tk.END, values=(
                account.name,
                account.account_type.value,
                f"{account.balance:.2f}",
                account.bank_name or "-",
                account.created_at.strftime("%Y-%m-%d %H:%M:%S")
            ), tags=(account.id,))

    def _refresh_transactions(self):
        for item in self.tree_transactions.get_children():
            self.tree_transactions.delete(item)
        transactions = sorted(self.storage.get_all_transactions(), key=lambda x: x.created_at, reverse=True)
        for t in transactions:
            account = self.storage.get_account(t.account_id)
            account_name = account.name if account else "-"
            if t.transaction_type == TransactionType.TRANSFER and t.target_account_id:
                target_account = self.storage.get_account(t.target_account_id)
                target_name = target_account.name if target_account else "-"
                account_name = f"{account_name} -> {target_name}"
            self.tree_transactions.insert("", tk.END, values=(
                t.transaction_type.value,
                f"{t.amount:.2f}",
                t.category,
                t.description,
                account_name,
                t.created_at.strftime("%Y-%m-%d %H:%M:%S")
            ), tags=(t.id,))

    def _refresh_account_combos(self):
        accounts = self.storage.get_all_accounts()
        account_list = [(acc.id, acc.name) for acc in accounts]
        values = [f"{name} ({acc_id[:8]})" for acc_id, name in account_list]
        self.combo_select_account["values"] = values
        self.combo_transfer_to["values"] = values

        if accounts and self.combo_select_account.current() == -1:
            self.combo_select_account.current(0)
            self._on_account_selected(None)

    def _on_account_selected(self, event):
        current = self.combo_select_account.current()
        if current == -1:
            self.current_account_id = None
            self.label_balance.config(text="余额: --")
            return
        accounts = self.storage.get_all_accounts()
        if 0 <= current < len(accounts):
            self.current_account_id = accounts[current].id
            balance = accounts[current].balance
            self.label_balance.config(text=f"余额: {balance:.2f}")

    def _add_account(self):
        name = self.entry_account_name.get().strip()
        type_str = self.combo_account_type.get()
        balance_str = self.entry_account_balance.get().strip()
        bank_name = self.entry_bank_name.get().strip() or None

        if not name:
            messagebox.showwarning("提示", "请输入账户名称")
            return
        if not type_str:
            messagebox.showwarning("提示", "请选择账户类型")
            return
        try:
            balance = float(balance_str) if balance_str else 0.0
        except ValueError:
            messagebox.showwarning("提示", "余额格式不正确")
            return

        account_type = None
        for t in AccountType:
            if t.value == type_str:
                account_type = t
                break

        account = Account(
            name=name,
            account_type=account_type,
            balance=balance,
            bank_name=bank_name
        )
        self.storage.add_account(account)
        messagebox.showinfo("成功", "账户添加成功")
        self._clear_account_form()
        self._refresh_data()

    def _clear_account_form(self):
        self.entry_account_name.delete(0, tk.END)
        self.combo_account_type.current(0)
        self.entry_account_balance.delete(0, tk.END)
        self.entry_bank_name.delete(0, tk.END)

    def _delete_account(self):
        selected = self.tree_accounts.selection()
        if not selected:
            messagebox.showwarning("提示", "请选择要删除的账户")
            return
        item = self.tree_accounts.item(selected[0])
        account_id = item["tags"][0]

        if messagebox.askyesno("确认", "确定要删除此账户吗？相关交易记录也会受到影响。"):
            self.storage.delete_account(account_id)
            self._refresh_data()

    def _add_income(self):
        if not self.current_account_id:
            messagebox.showwarning("提示", "请先选择账户")
            return

        amount_str = self.entry_income_amount.get().strip()
        category = self.entry_income_category.get().strip()
        description = self.entry_income_desc.get().strip()

        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showwarning("提示", "金额格式不正确")
            return

        if not category:
            category = "其他"

        transaction = self.ledger.add_income(self.current_account_id, amount, category, description)
        if transaction:
            messagebox.showinfo("成功", "收入记录成功")
            self.entry_income_amount.delete(0, tk.END)
            self.entry_income_category.delete(0, tk.END)
            self.entry_income_desc.delete(0, tk.END)
            self._refresh_data()
        else:
            messagebox.showerror("错误", "记录失败")

    def _add_expense(self):
        if not self.current_account_id:
            messagebox.showwarning("提示", "请先选择账户")
            return

        amount_str = self.entry_expense_amount.get().strip()
        category = self.entry_expense_category.get().strip()
        description = self.entry_expense_desc.get().strip()

        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showwarning("提示", "金额格式不正确")
            return

        if not category:
            category = "其他"

        transaction = self.ledger.add_expense(self.current_account_id, amount, category, description)
        if transaction:
            messagebox.showinfo("成功", "支出记录成功")
            self.entry_expense_amount.delete(0, tk.END)
            self.entry_expense_category.delete(0, tk.END)
            self.entry_expense_desc.delete(0, tk.END)
            self._refresh_data()
        else:
            messagebox.showerror("错误", "记录失败，请检查余额是否足够")

    def _transfer(self):
        if not self.current_account_id:
            messagebox.showwarning("提示", "请先选择转出账户")
            return

        to_index = self.combo_transfer_to.current()
        if to_index == -1:
            messagebox.showwarning("提示", "请选择转入账户")
            return

        amount_str = self.entry_transfer_amount.get().strip()
        description = self.entry_transfer_desc.get().strip()

        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showwarning("提示", "金额格式不正确")
            return

        accounts = self.storage.get_all_accounts()
        if to_index >= len(accounts):
            return
        to_account_id = accounts[to_index].id

        transaction = self.ledger.transfer(self.current_account_id, to_account_id, amount, "转账", description)
        if transaction:
            messagebox.showinfo("成功", "转账成功")
            self.entry_transfer_amount.delete(0, tk.END)
            self.entry_transfer_desc.delete(0, tk.END)
            self._refresh_data()
        else:
            messagebox.showerror("错误", "转账失败，请检查余额是否足够")

    def _revert_transaction(self):
        selected = self.tree_transactions.selection()
        if not selected:
            messagebox.showwarning("提示", "请选择要撤销的交易")
            return
        item = self.tree_transactions.item(selected[0])
        transaction_id = item["tags"][0]

        if messagebox.askyesno("确认", "确定要撤销此交易吗？"):
            if self.ledger.revert_transaction(transaction_id):
                messagebox.showinfo("成功", "交易已撤销")
                self._refresh_data()
            else:
                messagebox.showerror("错误", "撤销失败")
