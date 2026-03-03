from django.contrib import admin
from .models import *

@admin.register(IncomeType)
class IncomeTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']

@admin.register(ExpenseType)
class ExpenseTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_active']
    list_filter = ['category', 'is_active']

@admin.register(AssetType)
class AssetTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_depreciable']
    list_filter = ['category']

@admin.register(LiabilityType)
class LiabilityTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'has_interest']
    list_filter = ['category']

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['user', 'income_type', 'amount', 'frequency', 'date_received']
    list_filter = ['income_type', 'frequency', 'date_received']
    search_fields = ['user__username', 'description']

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['user', 'expense_type', 'amount', 'date_incurred']
    list_filter = ['expense_type', 'date_incurred']
    search_fields = ['user__username', 'description']

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['user', 'asset_type', 'name', 'current_value']
    list_filter = ['asset_type']
    search_fields = ['user__username', 'name']

@admin.register(Liability)
class LiabilityAdmin(admin.ModelAdmin):
    list_display = ['user', 'liability_type', 'name', 'current_balance', 'monthly_payment']
    list_filter = ['liability_type']
    search_fields = ['user__username', 'name']

@admin.register(CashFlow)
class CashFlowAdmin(admin.ModelAdmin):
    list_display = ['user', 'year', 'month', 'total_income', 'total_expenses', 'net_cash_flow']
    list_filter = ['year', 'month']
    search_fields = ['user__username']


@admin.register(MoneyRelatedSMS)
class MoneyRelatedSMSAdmin(admin.ModelAdmin):
    list_display = ['user', 'message']
    search_fields = ['user__username', 'message']

@admin.register(KeyWordExpenseType)
class KeyWordExpenseTypeSMSAdmin(admin.ModelAdmin):
    list_display = ['user', 'keyword']
    search_fields = ['user__username', 'keyword']



