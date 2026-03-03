from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime

# LOOKUP TABLES
class IncomeType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'income_types'
    
    def __str__(self):
        return self.name

class ExpenseType(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)  # Fixed, Variable, Periodic
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'expense_types'
    
    def __str__(self):
        return f"{self.name} ({self.category})"

class AssetType(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)  # Liquid, Investment, Personal
    is_depreciable = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'asset_types'
    
    def __str__(self):
        return self.name

class LiabilityType(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)  # Short-term, Long-term
    pill_color = models.CharField(max_length=50, default='primary')
    has_interest = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'liability_types'
    
    def __str__(self):
        return self.name
    

class Income(models.Model):
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
        ('one_time', 'One Time'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    income_type = models.ForeignKey(IncomeType, on_delete=models.PROTECT)
    amount = models.FloatField()
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='monthly')
    description = models.TextField(blank=True)
    date_received = models.DateField()
    is_recurring = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'incomes'
        ordering = ['-date_received']
    
    def __str__(self):
        return f"{self.user.username} - {self.income_type.name} - {self.amount}"
    
    def get_monthly_amount(self):
        """Convert income to monthly equivalent"""
        conversion = {
            'daily': self.amount * 30,
            'weekly': self.amount * 4,
            'monthly': self.amount,
            'quarterly': self.amount / 3,
            'yearly': self.amount / 12,
            'one_time': 0  # One-time income doesn't contribute to monthly
        }
        return conversion.get(self.frequency, self.amount)


class KeyWordExpenseType(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expense_type = models.ForeignKey(ExpenseType, on_delete=models.PROTECT)
    keyword = models.CharField(max_length=100)


class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expense_type = models.ForeignKey(ExpenseType, on_delete=models.PROTECT)
    amount = models.FloatField()
    description = models.TextField(blank=True)
    date_incurred = models.DateField()
    is_recurring = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'expenses'
        ordering = ['-date_incurred']
    
    def __str__(self):
        return f"{self.user.username} - {self.expense_type.name} - {self.amount}"

class Asset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    asset_type = models.ForeignKey(AssetType, on_delete=models.PROTECT)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    current_value = models.FloatField()
    purchase_price = models.FloatField(null=True, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    generates_income = models.BooleanField(default=False)
    monthly_income = models.FloatField(default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'assets'
        ordering = ['-current_value']
    
    def __str__(self):
        return f"{self.user.username} - {self.name} - {self.current_value}"

class Liability(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    liability_type = models.ForeignKey(LiabilityType, on_delete=models.PROTECT)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    original_amount = models.FloatField()
    current_balance = models.FloatField()
    interest_rate = models.FloatField(default=0)
    monthly_payment = models.FloatField()
    due_date = models.DateField(null=True, blank=True)
    lender = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'liabilities'
        ordering = ['-current_balance']
    
    def __str__(self):
        return f"{self.user.username} - {self.name} - {self.current_balance}"


class CashFlow(models.Model):
    """Monthly cash flow summary"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    year = models.IntegerField()
    month = models.IntegerField()
    total_income = models.FloatField(default=0)
    total_expenses = models.FloatField(default=0)
    net_cash_flow = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cash_flows'
        unique_together = ['user', 'year', 'month']
        ordering = ['-year', '-month']
    
    def __str__(self):
        return f"{self.user.username} - {self.year}-{self.month:02d} - {self.net_cash_flow}"
    
    def calculate_cash_flow(self):
        """Calculate cash flow for the month"""
        from django.db.models import Sum
        from django.utils import timezone
        
        # Get monthly income (convert all to monthly equivalent)
        incomes = Income.objects.filter(
            user=self.user,
            date_received__year=self.year,
            date_received__month=self.month
        )
        total_income = sum(income.get_monthly_amount() for income in incomes)
        
        # Get monthly expenses
        expenses = Expense.objects.filter(
            user=self.user,
            date_incurred__year=self.year,
            date_incurred__month=self.month
        )
        total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
        
        self.total_income = total_income
        self.total_expenses = total_expenses
        self.net_cash_flow = total_income - total_expenses
        self.save()
    
    @classmethod
    def generate_monthly_cash_flow(cls, user, year, month):
        """Generate or update cash flow for specific month"""
        cash_flow, created = cls.objects.get_or_create(
            user=user,
            year=year,
            month=month
        )
        cash_flow.calculate_cash_flow()
        return cash_flow
    
    @classmethod
    def generate_current_month_cash_flow(cls, user):
        """Generate cash flow for current month"""
        now = timezone.now()
        return cls.generate_monthly_cash_flow(user, now.year, now.month)
    
    @classmethod
    def generate_all_months_cash_flow(cls, user):
        """Generate cash flow for all months with transactions"""
        # Get all distinct months from income and expenses
        from django.db.models.functions import ExtractYear, ExtractMonth
        
        income_months = Income.objects.filter(user=user).annotate(
            year=ExtractYear('date_received'),
            month=ExtractMonth('date_received')
        ).values('year', 'month').distinct()
        
        expense_months = Expense.objects.filter(user=user).annotate(
            year=ExtractYear('date_incurred'),
            month=ExtractMonth('date_incurred')
        ).values('year', 'month').distinct()
        
        # Combine and generate cash flow for each month
        all_months = income_months.union(expense_months)
        
        for month_data in all_months:
            cls.generate_monthly_cash_flow(user, month_data['year'], month_data['month'])



class FinancialReport(models.Model):
    REPORT_TYPES = [
        ('balance_sheet', 'Balance Sheet'),
        ('income_statement', 'Income Statement'),
        ('cash_flow', 'Cash Flow Statement'),
        ('net_worth', 'Net Worth Report'),
        ('comprehensive', 'Comprehensive Financial Report'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    period_start = models.DateField()
    period_end = models.DateField()
    generated_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()  # Store report data as JSON
    
    class Meta:
        db_table = 'financial_reports'
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_report_type_display()} - {self.period_start} to {self.period_end}"
    


class MoneyRelatedSMS(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    income_type = models.ForeignKey(IncomeType, on_delete=models.PROTECT, null=True, blank=True)
    expense_type = models.ForeignKey(ExpenseType, on_delete=models.PROTECT, null=True, blank=True)
    message = models.TextField()
    is_processed = models.BooleanField(default=False)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'money_related_sms'
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.pk}"
    












