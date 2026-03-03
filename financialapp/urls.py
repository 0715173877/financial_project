from django.urls import path, include
from .views import *
from .financial_crud import *
from .reports import *

app_name = 'financialapp'

urlpatterns = [
    # Add registration URL
    path('register/', register, name='register'),
    # Add profile URLs
    path('profile/', profile, name='profile'),
    path('profile/update/', profile_update, name='profile_update'),
    path('profile/change-password/', change_password, name='change_password'),

    path('', dashboard, name='dashboard'),
    
    # Income URLs
    path('income/', income_list, name='income_list'),
    path('income/create/', income_create, name='income_create'),
    path('income/<int:pk>/edit/', income_edit, name='income_edit'),
    path('income/<int:pk>/delete/', income_delete, name='income_delete'),
    path('income/create/<int:pk>/repeate/', income_create_repeated, name='income_create_repeate'),
    
    # Expense URLs
    path('expenses/', expense_list, name='expense_list'),
    path('expenses/create/', expense_create, name='expense_create'),
    path('expenses/<int:pk>/edit/', expense_edit, name='expense_edit'),
    path('expenses/<int:pk>/delete/', expense_delete, name='expense_delete'),
    path('expense/create/<int:pk>/repeate/', expense_create_repeated, name='expense_create_repeate'),
    
    # Asset URLs
    path('assets/', asset_list, name='asset_list'),
    path('assets/create/', asset_create, name='asset_create'),
    path('assets/<int:pk>/edit/', asset_edit, name='asset_edit'),
    path('assets/<int:pk>/delete/', asset_delete, name='asset_delete'),
    
    # Liability URLs
    path('liabilities/', liability_list, name='liability_list'),
    path('liabilities/create/', liability_create, name='liability_create'),
    path('liabilities/<int:pk>/edit/', liability_edit, name='liability_edit'),
    path('liabilities/<int:pk>/delete/', liability_delete, name='liability_delete'),
    
    path('cash-flow/', cash_flow, name='cash_flow'),

    # Reports URLs
    path('reports/', financial_reports, name='financial_reports'),
    path('reports/balance-sheet/', generate_balance_sheet, name='generate_balance_sheet'),
    path('reports/income-statement/', generate_income_statement, name='generate_income_statement'),
    path('reports/cash-flow/', generate_cash_flow_statement, name='generate_cash_flow'),
    path('reports/comprehensive/', generate_comprehensive_report, name='generate_comprehensive'),
    
    
    # Report Viewing and Export URLs
    path('reports/<int:report_id>/', view_report, name='view_report'),
    path('reports/<int:report_id>/export/', export_report, name='export_report'),
    
    # Report Management URLs
    path('reports/<int:report_id>/delete/', delete_report, name='delete_report'),
    path('reports/all/', all_reports, name='all_reports'),

    # SMS
    path('sms/', sms_create, name='sms_create'),
    path('offline/', offline, name='offline'),
]