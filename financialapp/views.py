from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Avg

from .financial_obj import Operations
from .models import *
from django.contrib.messages import success, error, warning, info, debug
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'auth_register/register.html', {'form': form})

@login_required
def profile(request):
    # Calculate statistics
    income_count = Income.objects.filter(user=request.user).count()
    expense_count = Expense.objects.filter(user=request.user).count()
    asset_count = Asset.objects.filter(user=request.user).count()
    liability_count = Liability.objects.filter(user=request.user).count()
    total_records = income_count + expense_count + asset_count + liability_count
    
    # Financial metrics
    total_assets = Asset.objects.filter(user=request.user).aggregate(Sum('current_value'))['current_value__sum'] or 0
    total_liabilities = Liability.objects.filter(user=request.user).aggregate(Sum('current_balance'))['current_balance__sum'] or 0
    net_worth = total_assets - total_liabilities
    
    # Monthly calculations
    incomes = Income.objects.filter(user=request.user)
    monthly_income = sum(income.get_monthly_amount() for income in incomes)
    monthly_expenses = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
    monthly_cash_flow = monthly_income - monthly_expenses
    
    # Financial ratios
    savings_rate = (monthly_cash_flow / monthly_income * 100) if monthly_income > 0 else 0
    total_monthly_debt = Liability.objects.filter(user=request.user).aggregate(Sum('monthly_payment'))['monthly_payment__sum'] or 0
    debt_to_income = (total_monthly_debt / monthly_income * 100) if monthly_income > 0 else 0
    
    # Recent activity (last 10 transactions)
    recent_income = Income.objects.filter(user=request.user).order_by('-date_received')[:5]
    recent_expenses = Expense.objects.filter(user=request.user).order_by('-date_incurred')[:5]
    
    recent_activity = []
    for income in recent_income:
        recent_activity.append({
            'date': income.date_received,
            'type': 'Income',
            'description': f"{income.income_type.name}",
            'amount': income.amount,
            'badge_color': 'success'
        })
    
    for expense in recent_expenses:
        recent_activity.append({
            'date': expense.date_incurred,
            'type': 'Expense',
            'description': f"{expense.expense_type.name}",
            'amount': -expense.amount,
            'badge_color': 'danger'
        })
    
    # Sort by date and take top 10
    recent_activity.sort(key=lambda x: x['date'], reverse=True)
    recent_activity = recent_activity[:10]
    
    context = {
        'income_count': income_count,
        'expense_count': expense_count,
        'asset_count': asset_count,
        'liability_count': liability_count,
        'total_records': total_records,
        'net_worth': net_worth,
        'total_assets': total_assets,
        'monthly_income': monthly_income,
        'monthly_cash_flow': monthly_cash_flow,
        'savings_rate': savings_rate,
        'debt_to_income': debt_to_income,
        'recent_activity': recent_activity,
    }
    
    return render(request, 'auth_register/profile.html', context)

@login_required
def profile_update(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.username = request.POST.get('username', '')
        
        try:
            user.save()
            success(request, 'Profile updated successfully!')
        except Exception as e:
            error(request, f'Error updating profile: {str(e)}')
        
        return redirect('financialapp:profile')
    
    return redirect('financialapp:profile')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            success(request, 'Your password was successfully updated!')
            return redirect('financialapp:profile')
        else:
            error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'auth_register/change_password.html', {'form': form})

@login_required
def dashboard(request):
    # Auto-generate current month cash flow
    CashFlow.generate_current_month_cash_flow(request.user)

    # Calculate key metrics
    total_assets = Asset.objects.filter(user=request.user).aggregate(Sum('current_value'))['current_value__sum'] or 0
    total_liabilities = Liability.objects.filter(user=request.user).aggregate(Sum('current_balance'))['current_balance__sum'] or 0
    net_worth = total_assets - total_liabilities
    
    # Calculate monthly income (convert all to monthly equivalent)
    incomes = Income.objects.filter(user=request.user)
    monthly_income = sum(income.get_monthly_amount() for income in incomes)
    
    # Calculate monthly expenses
    monthly_expenses = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
    cash_flow = monthly_income - monthly_expenses
    
    # transactions this months
    income = Income.objects.filter(user=request.user).order_by('-date_received')
    expenses = Expense.objects.filter(user=request.user).order_by('-date_incurred')

    # Recent transactions
    recent_income = income[:5]
    recent_expenses = expenses[:5]
    obj = Operations(request)
    barchart = obj.barchart()
    asset_chart = obj.asset_chart()
    
    context = {
        'net_worth': net_worth,
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'cash_flow': cash_flow,
        'recent_income': recent_income,
        'recent_expenses': recent_expenses,
        'barchart':barchart,
        'asset_chart':asset_chart
    }
    
    return render(request, 'general/dashboard.html', context)


@login_required
def income_list(request):
    incomes = Income.objects.filter(user=request.user).order_by('-date_received')
    income_types = IncomeType.objects.filter(is_active=True)
    # paginaton
    obj = Operations(request)
    incomes = obj.get_pagination(incomes)
    context = {
        'obj': incomes,
        'income_types': income_types,
    }
    return render(request, 'income/income.html', context)

@login_required
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date_incurred')
    expense_types = ExpenseType.objects.filter(is_active=True)
    # Calculate summary metrics
    fixed_expenses = Expense.objects.filter(
        user=request.user, 
        expense_type__category='Fixed'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    variable_expenses = Expense.objects.filter(
        user=request.user, 
        expense_type__category='Variable'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    total_expenses = fixed_expenses + variable_expenses

    # paginaton
    obj = Operations(request)
    expenses = obj.get_pagination(expenses, 30)
    
    context = {
        'obj': expenses,
        'expense_types': expense_types,
        'fixed_expenses': fixed_expenses,
        'variable_expenses': variable_expenses,
        'total_expenses': total_expenses,
    }
    return render(request, 'expense/expense.html', context)

@login_required
def asset_list(request):
    assets = Asset.objects.filter(user=request.user).order_by('-current_value')
    asset_types = AssetType.objects.all()
    
    # Calculate summary metrics
    total_assets = assets.aggregate(Sum('current_value'))['current_value__sum'] or 0
    income_assets = assets.filter(generates_income=True).aggregate(Sum('current_value'))['current_value__sum'] or 0
    liquid_assets = assets.filter(asset_type__category='Liquid').aggregate(Sum('current_value'))['current_value__sum'] or 0
    monthly_asset_income = assets.aggregate(Sum('monthly_income'))['monthly_income__sum'] or 0
    # paginaton
    obj = Operations(request)
    assets = obj.get_pagination(assets)

    context = {
        'obj': assets,
        'asset_types': asset_types,
        'total_assets': total_assets,
        'income_assets': income_assets,
        'liquid_assets': liquid_assets,
        'monthly_asset_income': monthly_asset_income,
    }
    return render(request, 'asset/asset.html', context)

@login_required
def liability_list(request):
    liabilities = Liability.objects.filter(user=request.user).order_by('-current_balance')
    liability_types = LiabilityType.objects.all()
    
    # Calculate summary metrics
    total_debt = liabilities.aggregate(Sum('current_balance'))['current_balance__sum'] or 0
    monthly_payments = liabilities.aggregate(Sum('monthly_payment'))['monthly_payment__sum'] or 0
    
    # Calculate monthly interest (simplified)
    monthly_interest = sum(
        liability.current_balance * (liability.interest_rate / 100 / 12) 
        for liability in liabilities
    )
        # paginaton
    obj = Operations(request)
    liabilities = obj.get_pagination(liabilities)
    context = {
        'obj': liabilities,
        'liability_types': liability_types,
        'total_debt': total_debt,
        'monthly_payments': monthly_payments,
        'monthly_interest': monthly_interest,
    }
    return render(request, 'liability/liability.html', context)

@login_required
def cash_flow(request):
    cash_flows = CashFlow.objects.filter(user=request.user).order_by('-year', '-month')[:12]
    recent_cash_flows = cash_flows[:6]
    
    # Calculate averages
    if cash_flows:
        avg_income = cash_flows.aggregate(Avg('total_income'))['total_income__avg']
        avg_expenses = cash_flows.aggregate(Avg('total_expenses'))['total_expenses__avg']
        avg_cash_flow = cash_flows.aggregate(Avg('net_cash_flow'))['net_cash_flow__avg']
    else:
        avg_income = avg_expenses = avg_cash_flow = 0
    # charts
    obj = Operations(request)
    cashflow_chart = obj.cashflow_chart()
    income_vs_type = obj.income_vs_type()
    expense_vs_category = obj.expense_vs_category()
    context = {
        'cash_flows': cash_flows,
        'recent_cash_flows': recent_cash_flows,
        'avg_income': avg_income,
        'avg_expenses': avg_expenses,
        'avg_cash_flow': avg_cash_flow,
        'expense_vs_category':expense_vs_category,
        'income_vs_type':income_vs_type,
        'cashflow_chart':cashflow_chart
    }
    # print('======== ', context)
    return render(request, 'cashflow/cash_flow.html', context)



def offline(request):
    return render(request, 'offline.html')