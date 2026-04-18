
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Toplevel
from datetime import datetime
from typing import Optional
from models import Account, AccountType, TransactionType, Category
from storage import StorageManager
from ledger import LedgerManager


class LedgerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("记账本")
        self.root.geometry("1200x800")

        self.storage = StorageManager()
        self.ledger = LedgerManager(self.storage)

        self.current_account_id: Optional[str] = None
        self.current_category_root_id: Optional[str] = None
        self.editing_account_id: Optional[str] = None
        self.editing_transaction_id: Optional[str] = None

        self._create_widgets()
        self._refresh_data()

    def _create_widgets(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tab_accounts = ttk.Frame(notebook)
        self.tab_ledger = ttk.Frame(notebook)
        self.tab_transactions = ttk.Frame(notebook)
        self.tab_statistics = ttk.Frame(notebook)
        self.tab_categories = ttk.Frame(notebook)

        notebook.add(self.tab_accounts, text="账户管理")
        notebook.add(self.tab_ledger, text="动账记录")
        notebook.add(self.tab_transactions, text="交易历史")
        notebook.add(self.tab_statistics, text="统计报表")
        notebook.add(self.tab_categories, text="类型管理")

        self._create_accounts_tab()
        self._create_ledger_tab()
        self._create_transactions_tab()
        self._create_statistics_tab()
        self._create_categories_tab()

    def _create_accounts_tab(self):
        frame_total = ttk.LabelFrame(self.tab_accounts, text="总览", padding=10)
        frame_total.pack(fill=tk.X, padx=10, pady=10)
        self.label_total_balance = ttk.Label(frame_total, text="总余额: 0.00", font=("Arial", 14, "bold"))
        self.label_total_balance.pack(anchor=tk.W)

        frame_input = ttk.LabelFrame(self.tab_accounts, text="添加/编辑账户", padding=10)
        frame_input.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(frame_input, text="账户名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_account_name = ttk.Entry(frame_input, width=30)
        self.entry_account_name.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_input, text="账户类型:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.combo_account_type = ttk.Combobox(frame_input, values=[t.value for t in AccountType], state="readonly", width=27)
        self.combo_account_type.current(0)
        self.combo_account_type.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame_input, text="当前余额:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entry_account_balance = ttk.Entry(frame_input, width=30)
        self.entry_account_balance.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(frame_input, text="银行/机构:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.entry_bank_name = ttk.Entry(frame_input, width=30)
        self.entry_bank_name.grid(row=3, column=1, padx=5, pady=5)

        frame_buttons = ttk.Frame(frame_input)
        frame_buttons.grid(row=4, column=0, columnspan=2, pady=10)
        self.btn_add_account = ttk.Button(frame_buttons, text="添加账户", command=self._add_or_update_account)
        self.btn_add_account.pack(side=tk.LEFT, padx=5)
        self.btn_clear_account = ttk.Button(frame_buttons, text="清空/取消编辑", command=self._clear_account_form)
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
        ttk.Button(frame_actions, text="编辑选中账户", command=self._edit_account).pack(side=tk.LEFT, padx=5)
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

        ttk.Label(frame, text="发生时间:").grid(row=0, column=0, sticky=tk.W, pady=10)
        frame_time_income = ttk.Frame(frame)
        frame_time_income.grid(row=0, column=1, sticky=tk.W, pady=10)
        
        now = datetime.now()
        self.entry_income_date = ttk.Entry(frame_time_income, width=12)
        self.entry_income_date.insert(0, now.strftime("%Y-%m-%d"))
        self.entry_income_date.pack(side=tk.LEFT, padx=2)
        ttk.Label(frame_time_income, text=" ").pack(side=tk.LEFT)
        self.entry_income_time = ttk.Entry(frame_time_income, width=10)
        self.entry_income_time.insert(0, now.strftime("%H:%M:%S"))
        self.entry_income_time.pack(side=tk.LEFT, padx=2)

        ttk.Label(frame, text="金额:").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.entry_income_amount = ttk.Entry(frame, width=30)
        self.entry_income_amount.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(frame, text="主类别:").grid(row=2, column=0, sticky=tk.W, pady=10)
        self.combo_income_parent = ttk.Combobox(frame, state="readonly", width=27)
        self.combo_income_parent.grid(row=2, column=1, padx=10, pady=10)
        self.combo_income_parent.bind("<<ComboboxSelected>>", self._on_income_parent_changed)

        ttk.Label(frame, text="子类别:").grid(row=3, column=0, sticky=tk.W, pady=10)
        self.combo_income_child = ttk.Combobox(frame, state="readonly", width=27)
        self.combo_income_child.grid(row=3, column=1, padx=10, pady=10)

        ttk.Label(frame, text="备注:").grid(row=4, column=0, sticky=tk.W, pady=10)
        self.entry_income_desc = ttk.Entry(frame, width=30)
        self.entry_income_desc.grid(row=4, column=1, padx=10, pady=10)

        ttk.Button(frame, text="记录收入", command=self._add_income).grid(row=5, column=0, columnspan=2, pady=20)

    def _create_expense_widgets(self):
        frame = ttk.Frame(self.tab_expense, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="发生时间:").grid(row=0, column=0, sticky=tk.W, pady=10)
        frame_time_expense = ttk.Frame(frame)
        frame_time_expense.grid(row=0, column=1, sticky=tk.W, pady=10)
        
        now = datetime.now()
        self.entry_expense_date = ttk.Entry(frame_time_expense, width=12)
        self.entry_expense_date.insert(0, now.strftime("%Y-%m-%d"))
        self.entry_expense_date.pack(side=tk.LEFT, padx=2)
        ttk.Label(frame_time_expense, text=" ").pack(side=tk.LEFT)
        self.entry_expense_time = ttk.Entry(frame_time_expense, width=10)
        self.entry_expense_time.insert(0, now.strftime("%H:%M:%S"))
        self.entry_expense_time.pack(side=tk.LEFT, padx=2)

        ttk.Label(frame, text="金额:").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.entry_expense_amount = ttk.Entry(frame, width=30)
        self.entry_expense_amount.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(frame, text="主类别:").grid(row=2, column=0, sticky=tk.W, pady=10)
        self.combo_expense_parent = ttk.Combobox(frame, state="readonly", width=27)
        self.combo_expense_parent.grid(row=2, column=1, padx=10, pady=10)
        self.combo_expense_parent.bind("<<ComboboxSelected>>", self._on_expense_parent_changed)

        ttk.Label(frame, text="子类别:").grid(row=3, column=0, sticky=tk.W, pady=10)
        self.combo_expense_child = ttk.Combobox(frame, state="readonly", width=27)
        self.combo_expense_child.grid(row=3, column=1, padx=10, pady=10)

        ttk.Label(frame, text="备注:").grid(row=4, column=0, sticky=tk.W, pady=10)
        self.entry_expense_desc = ttk.Entry(frame, width=30)
        self.entry_expense_desc.grid(row=4, column=1, padx=10, pady=10)

        ttk.Button(frame, text="记录支出", command=self._add_expense).grid(row=5, column=0, columnspan=2, pady=20)

    def _create_transfer_widgets(self):
        frame = ttk.Frame(self.tab_transfer, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="发生时间:").grid(row=0, column=0, sticky=tk.W, pady=10)
        frame_time_transfer = ttk.Frame(frame)
        frame_time_transfer.grid(row=0, column=1, sticky=tk.W, pady=10)
        
        now = datetime.now()
        self.entry_transfer_date = ttk.Entry(frame_time_transfer, width=12)
        self.entry_transfer_date.insert(0, now.strftime("%Y-%m-%d"))
        self.entry_transfer_date.pack(side=tk.LEFT, padx=2)
        ttk.Label(frame_time_transfer, text=" ").pack(side=tk.LEFT)
        self.entry_transfer_time = ttk.Entry(frame_time_transfer, width=10)
        self.entry_transfer_time.insert(0, now.strftime("%H:%M:%S"))
        self.entry_transfer_time.pack(side=tk.LEFT, padx=2)

        ttk.Label(frame, text="金额:").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.entry_transfer_amount = ttk.Entry(frame, width=30)
        self.entry_transfer_amount.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(frame, text="转入账户:").grid(row=2, column=0, sticky=tk.W, pady=10)
        self.combo_transfer_to = ttk.Combobox(frame, state="readonly", width=27)
        self.combo_transfer_to.grid(row=2, column=1, padx=10, pady=10)

        ttk.Label(frame, text="备注:").grid(row=3, column=0, sticky=tk.W, pady=10)
        self.entry_transfer_desc = ttk.Entry(frame, width=30)
        self.entry_transfer_desc.grid(row=3, column=1, padx=10, pady=10)

        ttk.Button(frame, text="执行转账", command=self._transfer).grid(row=4, column=0, columnspan=2, pady=20)

    def _create_transactions_tab(self):
        frame_filter = ttk.Frame(self.tab_transactions, padding=10)
        frame_filter.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(frame_filter, text="年份:").pack(side=tk.LEFT, padx=5)
        self.combo_export_year = ttk.Combobox(frame_filter, state="readonly", width=10)
        self.combo_export_year.pack(side=tk.LEFT, padx=5)
        self.combo_export_year.bind("<<ComboboxSelected>>", self._on_trans_filter_changed)

        ttk.Label(frame_filter, text="月份:").pack(side=tk.LEFT, padx=5)
        months = ["全部"] + [str(i) for i in range(1, 13)]
        self.combo_export_month = ttk.Combobox(frame_filter, values=months, state="readonly", width=8)
        self.combo_export_month.current(0)
        self.combo_export_month.pack(side=tk.LEFT, padx=5)
        self.combo_export_month.bind("<<ComboboxSelected>>", self._on_trans_filter_changed)

        ttk.Button(frame_filter, text="导出Excel", command=self._export_excel).pack(side=tk.LEFT, padx=20)
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
        ttk.Button(frame_actions, text="编辑选中交易", command=self._edit_transaction).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_actions, text="撤销选中交易", command=self._revert_transaction).pack(side=tk.RIGHT)

    def _create_statistics_tab(self):
        frame_control = ttk.LabelFrame(self.tab_statistics, text="统计范围", padding=10)
        frame_control.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(frame_control, text="统计周期:").pack(side=tk.LEFT, padx=5)
        self.combo_stat_period = ttk.Combobox(frame_control, values=["全部时间", "本年", "本月", "本周", "今日"], state="readonly", width=15)
        self.combo_stat_period.current(0)
        self.combo_stat_period.pack(side=tk.LEFT, padx=5)
        self.combo_stat_period.bind("<<ComboboxSelected>>", self._on_stat_period_changed)

        ttk.Label(frame_control, text="年份:").pack(side=tk.LEFT, padx=5)
        self.combo_stat_year = ttk.Combobox(frame_control, state="readonly", width=10)
        self.combo_stat_year.pack(side=tk.LEFT, padx=5)
        self.combo_stat_year.bind("<<ComboboxSelected>>", self._on_stat_year_changed)

        ttk.Label(frame_control, text="月份:").pack(side=tk.LEFT, padx=5)
        months = [str(i) for i in range(1, 13)]
        self.combo_stat_month = ttk.Combobox(frame_control, values=months, state="readonly", width=8)
        self.combo_stat_month.pack(side=tk.LEFT, padx=5)
        self.combo_stat_month.bind("<<ComboboxSelected>>", self._on_stat_month_changed)

        ttk.Button(frame_control, text="刷新统计", command=self._refresh_statistics).pack(side=tk.LEFT, padx=20)

        frame_stats = ttk.LabelFrame(self.tab_statistics, text="统计结果", padding=20)
        frame_stats.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        frame_income = ttk.Frame(frame_stats)
        frame_income.pack(fill=tk.X, pady=10)
        ttk.Label(frame_income, text="总收入: ", font=("Arial", 12)).pack(side=tk.LEFT)
        self.label_stat_income = ttk.Label(frame_income, text="0.00", font=("Arial", 14, "bold"), foreground="green")
        self.label_stat_income.pack(side=tk.LEFT)

        frame_expense = ttk.Frame(frame_stats)
        frame_expense.pack(fill=tk.X, pady=10)
        ttk.Label(frame_expense, text="总支出: ", font=("Arial", 12)).pack(side=tk.LEFT)
        self.label_stat_expense = ttk.Label(frame_expense, text="0.00", font=("Arial", 14, "bold"), foreground="red")
        self.label_stat_expense.pack(side=tk.LEFT)

        frame_balance = ttk.Frame(frame_stats)
        frame_balance.pack(fill=tk.X, pady=10)
        ttk.Label(frame_balance, text="结余: ", font=("Arial", 12)).pack(side=tk.LEFT)
        self.label_stat_balance = ttk.Label(frame_balance, text="0.00", font=("Arial", 14, "bold"))
        self.label_stat_balance.pack(side=tk.LEFT)

    def _create_categories_tab(self):
        notebook_cats = ttk.Notebook(self.tab_categories)
        notebook_cats.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tab_cats_expense = ttk.Frame(notebook_cats)
        self.tab_cats_income = ttk.Frame(notebook_cats)
        notebook_cats.add(self.tab_cats_expense, text="支出类型")
        notebook_cats.add(self.tab_cats_income, text="收入类型")

        self._create_category_management(self.tab_cats_expense, TransactionType.EXPENSE)
        self._create_category_management(self.tab_cats_income, TransactionType.INCOME)

    def _create_category_management(self, parent, trans_type):
        frame = ttk.Frame(parent, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        frame_add = ttk.LabelFrame(frame, text="添加类型", padding=10)
        frame_add.pack(fill=tk.X, pady=5)

        ttk.Label(frame_add, text="类型名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        entry_cat_name = ttk.Entry(frame_add, width=25)
        entry_cat_name.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_add, text="父类型 (可选):").grid(row=0, column=2, sticky=tk.W, pady=5)
        combo_parent = ttk.Combobox(frame_add, state="readonly", width=20)
        combo_parent.grid(row=0, column=3, padx=5, pady=5)

        def add_cat():
            name = entry_cat_name.get().strip()
            if not name:
                messagebox.showwarning("提示", "请输入类型名称")
                return
            parent_id = None
            parent_idx = combo_parent.current()
            if parent_idx != -1:
                parent_list = self.storage.get_root_categories(trans_type)
                if 0 <= parent_idx < len(parent_list):
                    parent_id = parent_list[parent_idx].id
            category = Category(name=name, transaction_type=trans_type, parent_id=parent_id)
            self.storage.add_category(category)
            messagebox.showinfo("成功", "类型添加成功")
            entry_cat_name.delete(0, tk.END)
            self._refresh_category_combos()

        ttk.Button(frame_add, text="添加", command=add_cat).grid(row=0, column=4, padx=10)

        frame_list = ttk.LabelFrame(frame, text="类型列表", padding=10)
        frame_list.pack(fill=tk.BOTH, expand=True, pady=5)

        columns = ("name", "level")
        tree = ttk.Treeview(frame_list, columns=columns, show="headings", selectmode="browse")
        tree.heading("name", text="类型名称")
        tree.heading("level", text="层级")
        tree.column("name", width=300)
        tree.column("level", width=100)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        setattr(self, f"tree_cats_{trans_type.value}", tree)
        setattr(self, f"combo_parent_{trans_type.value}", combo_parent)

    def _refresh_data(self):
        self._refresh_accounts()
        self._refresh_transactions()
        self._refresh_account_combos()
        self._refresh_category_combos()
        self._refresh_total_balance()
        self._refresh_statistics()
        self._refresh_year_combos()

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
        
        year_str = self.combo_export_year.get()
        month_str = self.combo_export_month.get()
        
        if year_str and year_str != "全部":
            year = int(year_str)
            transactions = [t for t in transactions if t.created_at.year == year]
            if month_str and month_str != "全部":
                month = int(month_str)
                transactions = [t for t in transactions if t.created_at.month == month]
        
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

    def _refresh_category_combos(self):
        income_parents = self.storage.get_root_categories(TransactionType.INCOME)
        self.combo_income_parent["values"] = [c.name for c in income_parents]
        self.combo_income_parent.current(0) if income_parents else None
        self._on_income_parent_changed(None)

        expense_parents = self.storage.get_root_categories(TransactionType.EXPENSE)
        self.combo_expense_parent["values"] = [c.name for c in expense_parents]
        self.combo_expense_parent.current(0) if expense_parents else None
        self._on_expense_parent_changed(None)

        for trans_type in [TransactionType.EXPENSE, TransactionType.INCOME]:
            combo = getattr(self, f"combo_parent_{trans_type.value}", None)
            tree = getattr(self, f"tree_cats_{trans_type.value}", None)
            if combo and tree:
                parents = self.storage.get_root_categories(trans_type)
                combo["values"] = [c.name for c in parents]
                for item in tree.get_children():
                    tree.delete(item)
                for parent in parents:
                    tree.insert("", tk.END, values=(parent.name, "主类型"), tags=(parent.id,))
                    for child in self.storage.get_sub_categories(parent.id):
                        tree.insert("", tk.END, values=(f"  └ {child.name}", "子类型"), tags=(child.id,))

    def _refresh_total_balance(self):
        total = self.ledger.get_total_balance()
        self.label_total_balance.config(text=f"总余额: {total:.2f}")

    def _refresh_year_combos(self):
        transactions = self.storage.get_all_transactions()
        years = sorted(list({t.created_at.year for t in transactions}), reverse=True)
        years = ["全部"] + [str(y) for y in years]
        self.combo_export_year["values"] = years
        self.combo_export_year.current(0)
        self.combo_stat_year["values"] = [str(y) for y in sorted(list({t.created_at.year for t in transactions}), reverse=True)]
        if self.combo_stat_year["values"]:
            self.combo_stat_year.current(0)

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

    def _on_income_parent_changed(self, event):
        parent_idx = self.combo_income_parent.current()
        if parent_idx == -1:
            self.combo_income_child["values"] = []
            return
        parents = self.storage.get_root_categories(TransactionType.INCOME)
        if 0 <= parent_idx < len(parents):
            children = self.storage.get_sub_categories(parents[parent_idx].id)
            self.combo_income_child["values"] = ["不选子类型"] + [c.name for c in children]
            self.combo_income_child.current(0)

    def _on_expense_parent_changed(self, event):
        parent_idx = self.combo_expense_parent.current()
        if parent_idx == -1:
            self.combo_expense_child["values"] = []
            return
        parents = self.storage.get_root_categories(TransactionType.EXPENSE)
        if 0 <= parent_idx < len(parents):
            children = self.storage.get_sub_categories(parents[parent_idx].id)
            self.combo_expense_child["values"] = ["不选子类型"] + [c.name for c in children]
            self.combo_expense_child.current(0)

    def _on_stat_period_changed(self, event):
        self._refresh_statistics()

    def _on_stat_year_changed(self, event):
        self._refresh_statistics()

    def _on_stat_month_changed(self, event):
        self._refresh_statistics()

    def _on_trans_filter_changed(self, event):
        self._refresh_transactions()

    def _add_or_update_account(self):
        if self.editing_account_id:
            self._update_account()
        else:
            self._add_account()

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

    def _update_account(self):
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

        account_type = None
        for t in AccountType:
            if t.value == type_str:
                account_type = t
                break

        account = self.storage.get_account(self.editing_account_id)
        if not account:
            return

        try:
            new_balance = float(balance_str)
        except ValueError:
            messagebox.showwarning("提示", "余额格式不正确")
            return

        if abs(new_balance - account.balance) > 0.001:
            if not messagebox.askyesno("确认", f"余额从 {account.balance:.2f} 变为 {new_balance:.2f}，是否创建余额校正交易？"):
                new_balance = account.balance
            else:
                self.ledger.update_account_balance(self.editing_account_id, new_balance, "余额校正")

        self.storage.update_account(self.editing_account_id, name=name, account_type=account_type, bank_name=bank_name)
        messagebox.showinfo("成功", "账户更新成功")
        self._clear_account_form()
        self._refresh_data()

    def _edit_account(self):
        selected = self.tree_accounts.selection()
        if not selected:
            messagebox.showwarning("提示", "请选择要编辑的账户")
            return
        item = self.tree_accounts.item(selected[0])
        account_id = item["tags"][0]
        account = self.storage.get_account(account_id)
        if not account:
            return

        self.editing_account_id = account_id
        self.entry_account_name.delete(0, tk.END)
        self.entry_account_name.insert(0, account.name)
        
        for i, t in enumerate(AccountType):
            if t == account.account_type:
                self.combo_account_type.current(i)
                break

        self.entry_account_balance.delete(0, tk.END)
        self.entry_account_balance.insert(0, f"{account.balance:.2f}")
        
        self.entry_bank_name.delete(0, tk.END)
        if account.bank_name:
            self.entry_bank_name.insert(0, account.bank_name)
        
        self.btn_add_account.config(text="更新账户")

    def _clear_account_form(self):
        self.editing_account_id = None
        self.entry_account_name.delete(0, tk.END)
        self.combo_account_type.current(0)
        self.entry_account_balance.delete(0, tk.END)
        self.entry_bank_name.delete(0, tk.END)
        self.btn_add_account.config(text="添加账户")

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

    def _parse_datetime(self, date_str: str, time_str: str) -> Optional[datetime]:
        try:
            return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
        except:
            try:
                return datetime.strptime(date_str, "%Y-%m-%d")
            except:
                return None

    def _add_income(self):
        if not self.current_account_id:
            messagebox.showwarning("提示", "请先选择账户")
            return

        amount_str = self.entry_income_amount.get().strip()
        parent_idx = self.combo_income_parent.current()
        child_idx = self.combo_income_child.current()
        description = self.entry_income_desc.get().strip()
        date_str = self.entry_income_date.get().strip()
        time_str = self.entry_income_time.get().strip()
        
        created_at = self._parse_datetime(date_str, time_str)
        if not created_at:
            messagebox.showwarning("提示", "时间格式不正确，使用当前时间")
            created_at = datetime.now()

        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showwarning("提示", "金额格式不正确")
            return

        category_name = ""
        category_id = None
        parents = self.storage.get_root_categories(TransactionType.INCOME)
        if parent_idx != -1 and 0 <= parent_idx < len(parents):
            parent = parents[parent_idx]
            category_name = parent.name
            category_id = parent.id
            if child_idx > 0:
                children = self.storage.get_sub_categories(parent.id)
                child_idx_adj = child_idx - 1
                if 0 <= child_idx_adj < len(children):
                    category_name = f"{parent.name} - {children[child_idx_adj].name}"
                    category_id = children[child_idx_adj].id

        transaction = self.ledger.add_income(self.current_account_id, amount, category_name, description, category_id, created_at)
        if transaction:
            messagebox.showinfo("成功", "收入记录成功")
            self.entry_income_amount.delete(0, tk.END)
            self.entry_income_desc.delete(0, tk.END)
            now = datetime.now()
            self.entry_income_date.delete(0, tk.END)
            self.entry_income_date.insert(0, now.strftime("%Y-%m-%d"))
            self.entry_income_time.delete(0, tk.END)
            self.entry_income_time.insert(0, now.strftime("%H:%M:%S"))
            self._refresh_data()
        else:
            messagebox.showerror("错误", "记录失败")

    def _add_expense(self):
        if not self.current_account_id:
            messagebox.showwarning("提示", "请先选择账户")
            return

        amount_str = self.entry_expense_amount.get().strip()
        parent_idx = self.combo_expense_parent.current()
        child_idx = self.combo_expense_child.current()
        description = self.entry_expense_desc.get().strip()
        date_str = self.entry_expense_date.get().strip()
        time_str = self.entry_expense_time.get().strip()
        
        created_at = self._parse_datetime(date_str, time_str)
        if not created_at:
            messagebox.showwarning("提示", "时间格式不正确，使用当前时间")
            created_at = datetime.now()

        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showwarning("提示", "金额格式不正确")
            return

        category_name = ""
        category_id = None
        parents = self.storage.get_root_categories(TransactionType.EXPENSE)
        if parent_idx != -1 and 0 <= parent_idx < len(parents):
            parent = parents[parent_idx]
            category_name = parent.name
            category_id = parent.id
            if child_idx > 0:
                children = self.storage.get_sub_categories(parent.id)
                child_idx_adj = child_idx - 1
                if 0 <= child_idx_adj < len(children):
                    category_name = f"{parent.name} - {children[child_idx_adj].name}"
                    category_id = children[child_idx_adj].id

        transaction = self.ledger.add_expense(self.current_account_id, amount, category_name, description, category_id, created_at)
        if transaction:
            messagebox.showinfo("成功", "支出记录成功")
            self.entry_expense_amount.delete(0, tk.END)
            self.entry_expense_desc.delete(0, tk.END)
            now = datetime.now()
            self.entry_expense_date.delete(0, tk.END)
            self.entry_expense_date.insert(0, now.strftime("%Y-%m-%d"))
            self.entry_expense_time.delete(0, tk.END)
            self.entry_expense_time.insert(0, now.strftime("%H:%M:%S"))
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
        date_str = self.entry_transfer_date.get().strip()
        time_str = self.entry_transfer_time.get().strip()
        
        created_at = self._parse_datetime(date_str, time_str)
        if not created_at:
            messagebox.showwarning("提示", "时间格式不正确，使用当前时间")
            created_at = datetime.now()

        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showwarning("提示", "金额格式不正确")
            return

        accounts = self.storage.get_all_accounts()
        if to_index >= len(accounts):
            return
        to_account_id = accounts[to_index].id

        transaction = self.ledger.transfer(self.current_account_id, to_account_id, amount, "转账", description, created_at)
        if transaction:
            messagebox.showinfo("成功", "转账成功")
            self.entry_transfer_amount.delete(0, tk.END)
            self.entry_transfer_desc.delete(0, tk.END)
            now = datetime.now()
            self.entry_transfer_date.delete(0, tk.END)
            self.entry_transfer_date.insert(0, now.strftime("%Y-%m-%d"))
            self.entry_transfer_time.delete(0, tk.END)
            self.entry_transfer_time.insert(0, now.strftime("%H:%M:%S"))
            self._refresh_data()
        else:
            messagebox.showerror("错误", "转账失败，请检查余额是否足够")

    def _edit_transaction(self):
        selected = self.tree_transactions.selection()
        if not selected:
            messagebox.showwarning("提示", "请选择要编辑的交易")
            return
        item = self.tree_transactions.item(selected[0])
        transaction_id = item["tags"][0]
        transaction = self.storage.get_transaction(transaction_id)
        if not transaction:
            return

        edit_window = Toplevel(self.root)
        edit_window.title("编辑交易")
        edit_window.geometry("500x450")

        ttk.Label(edit_window, text="类型:").grid(row=0, column=0, sticky=tk.W, pady=10, padx=20)
        combo_type = ttk.Combobox(edit_window, values=[t.value for t in TransactionType], state="readonly", width=30)
        for i, t in enumerate(TransactionType):
            if t == transaction.transaction_type:
                combo_type.current(i)
        combo_type.grid(row=0, column=1, sticky=tk.W, pady=10)

        ttk.Label(edit_window, text="金额:").grid(row=1, column=0, sticky=tk.W, pady=10, padx=20)
        entry_amount = ttk.Entry(edit_window, width=30)
        entry_amount.insert(0, f"{transaction.amount:.2f}")
        entry_amount.grid(row=1, column=1, sticky=tk.W, pady=10)

        ttk.Label(edit_window, text="类别:").grid(row=2, column=0, sticky=tk.W, pady=10, padx=20)
        entry_category = ttk.Entry(edit_window, width=30)
        entry_category.insert(0, transaction.category)
        entry_category.grid(row=2, column=1, sticky=tk.W, pady=10)

        ttk.Label(edit_window, text="备注:").grid(row=3, column=0, sticky=tk.W, pady=10, padx=20)
        entry_desc = ttk.Entry(edit_window, width=30)
        entry_desc.insert(0, transaction.description)
        entry_desc.grid(row=3, column=1, sticky=tk.W, pady=10)

        ttk.Label(edit_window, text="发生时间:").grid(row=4, column=0, sticky=tk.W, pady=10, padx=20)
        frame_time = ttk.Frame(edit_window)
        frame_time.grid(row=4, column=1, sticky=tk.W, pady=10)
        entry_date = ttk.Entry(frame_time, width=12)
        entry_date.insert(0, transaction.created_at.strftime("%Y-%m-%d"))
        entry_date.pack(side=tk.LEFT, padx=2)
        ttk.Label(frame_time, text=" ").pack(side=tk.LEFT)
        entry_time = ttk.Entry(frame_time, width=10)
        entry_time.insert(0, transaction.created_at.strftime("%H:%M:%S"))
        entry_time.pack(side=tk.LEFT, padx=2)

        def save_edit():
            try:
                amount = float(entry_amount.get().strip())
            except ValueError:
                messagebox.showwarning("提示", "金额格式不正确")
                return

            created_at = self._parse_datetime(entry_date.get().strip(), entry_time.get().strip())
            if not created_at:
                messagebox.showwarning("提示", "时间格式不正确")
                return

            type_str = combo_type.get()
            trans_type = None
            for t in TransactionType:
                if t.value == type_str:
                    trans_type = t
                    break

            if self.ledger.update_transaction(
                transaction_id,
                transaction_type=trans_type,
                amount=amount,
                category=entry_category.get().strip(),
                description=entry_desc.get().strip(),
                created_at=created_at
            ):
                messagebox.showinfo("成功", "交易更新成功")
                edit_window.destroy()
                self._refresh_data()
            else:
                messagebox.showerror("错误", "交易更新失败，请检查余额是否足够")

        ttk.Button(edit_window, text="保存", command=save_edit).grid(row=5, column=0, columnspan=2, pady=20)

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

    def _refresh_statistics(self):
        period = self.combo_stat_period.get()
        year = None
        month = None

        if period == "本年":
            year = int(self.combo_stat_year.get()) if self.combo_stat_year.get() else datetime.now().year
            stats = self.ledger.get_statistics("year", year=year)
        elif period == "本月":
            year = int(self.combo_stat_year.get()) if self.combo_stat_year.get() else datetime.now().year
            month = int(self.combo_stat_month.get()) if self.combo_stat_month.get() else datetime.now().month
            stats = self.ledger.get_statistics("month", year=year, month=month)
        elif period == "本周":
            stats = self.ledger.get_statistics("week")
        elif period == "今日":
            stats = self.ledger.get_statistics("day")
        else:
            stats = self.ledger.get_statistics("all")

        self.label_stat_income.config(text=f"{stats['income']:.2f}")
        self.label_stat_expense.config(text=f"{stats['expense']:.2f}")
        balance = stats['balance']
        self.label_stat_balance.config(text=f"{balance:.2f}", foreground="green" if balance >= 0 else "red")

    def _export_excel(self):
        year = None
        month = None
        year_str = self.combo_export_year.get()
        month_str = self.combo_export_month.get()

        if year_str and year_str != "全部":
            year = int(year_str)
            if month_str and month_str != "全部":
                month = int(month_str)

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")],
            title="导出交易记录"
        )
        if file_path:
            if self.ledger.export_to_excel(file_path, year, month):
                messagebox.showinfo("成功", "导出成功！")
            else:
                messagebox.showerror("错误", "导出失败！")
