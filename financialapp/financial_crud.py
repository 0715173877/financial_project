from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Avg
from django.http import JsonResponse
from datetime import date
from dateutil.relativedelta import relativedelta
from .financial_obj import *
from .models import *
from .forms import *

# INCOME CRUD
@login_required
def income_create(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            messages.success(request, 'Income added successfully!')
            return redirect('financialapp:income_list')
    else:
        form = IncomeForm()
    return render(request, 'income/income_form.html', {'form': form, 'title': 'Add Income'})

@login_required
def income_edit(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            form.save()
            messages.success(request, 'Income updated successfully!')
            return redirect('financialapp:income_list')
    else:
        form = IncomeForm(instance=income)
    return render(request, 'income/income_form.html', {'form': form, 'title': 'Edit Income', 'pk':pk})

@login_required
def income_delete(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    if request.method == 'POST':
        income.delete()
        messages.success(request, 'Income deleted successfully!')
        return redirect('financialapp:income_list')
    return render(request, 'general/confirm_delete.html', {'object': income, 'type': 'income'})

# INCOME CRUD
@login_required
def income_create_repeated(request, pk):
    income = Income.objects.get(id=pk)
    user = User.objects.get(id=request.user.id)
    income_type=IncomeType.objects.get(id=income.income_type.pk)
    new_date = income.date_received + relativedelta(months=1)

    Income.objects.create(
        user=user,income_type=income_type,amount=income.amount,date_received=new_date
    )
    return redirect("financialapp:income_list")



# EXPENSE CRUD
@login_required
def expense_create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, 'Expense added successfully!')
            return redirect('financialapp:expense_list')
    else:
        form = ExpenseForm()
    return render(request, 'expense/expense_form.html', {'form': form, 'title': 'Add Expense'})

@login_required
def expense_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully!')
            return redirect('financialapp:expense_list')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'expense/expense_form.html', {'form': form, 'title': 'Edit Expense', 'pk':pk})

@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted successfully!')
        return redirect('financialapp:expense_list')
    return render(request, 'general/confirm_delete.html', {'object': expense, 'type': 'expense'})

@login_required
def expense_create_repeated(request, pk):
    expense = Expense.objects.get(id=pk)
    user = User.objects.get(id=request.user.id)
    expense_type=ExpenseType.objects.get(id=expense.expense_type.pk)
    new_date = expense.date_incurred + relativedelta(months=1)

    Expense.objects.create(
        user=user,expense_type=expense_type,amount=expense.amount,date_incurred=new_date
    )
    return redirect("financialapp:expense_list")


# ASSET CRUD
@login_required
def asset_create(request):
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.user = request.user
            asset.save()
            messages.success(request, 'Asset added successfully!')
            return redirect('financialapp:asset_list')
    else:
        form = AssetForm()
    return render(request, 'asset/asset_form.html', {'form': form, 'title': 'Add Asset'})

@login_required
def asset_edit(request, pk):
    asset = get_object_or_404(Asset, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AssetForm(request.POST, instance=asset)
        if form.is_valid():
            form.save()
            messages.success(request, 'Asset updated successfully!')
            return redirect('financialapp:asset_list')
    else:
        form = AssetForm(instance=asset)
    return render(request, 'asset/asset_form.html', {'form': form, 'title': 'Edit Asset', 'pk':pk})

@login_required
def asset_delete(request, pk):
    asset = get_object_or_404(Asset, pk=pk, user=request.user)
    if request.method == 'POST':
        asset.delete()
        messages.success(request, 'Asset deleted successfully!')
        return redirect('financialapp:asset_list')
    return render(request, 'general/confirm_delete.html', {'object': asset, 'type': 'asset'})

# LIABILITY CRUD
@login_required
def liability_create(request):
    if request.method == 'POST':
        form = LiabilityForm(request.POST)
        if form.is_valid():
            liability = form.save(commit=False)
            liability.user = request.user
            liability.save()
            messages.success(request, 'Liability added successfully!')
            return redirect('financialapp:liability_list')
    else:
        form = LiabilityForm()
    return render(request, 'liability/liability_form.html', {'form': form, 'title': 'Add Liability'})

@login_required
def liability_edit(request, pk):
    liability = get_object_or_404(Liability, pk=pk, user=request.user)
    if request.method == 'POST':
        form = LiabilityForm(request.POST, instance=liability)
        if form.is_valid():
            form.save()
            messages.success(request, 'Liability updated successfully!')
            return redirect('financialapp:liability_list')
    else:
        form = LiabilityForm(instance=liability)
    return render(request, 'liability/liability_form.html', {'form': form, 'title': 'Edit Liability', 'pk':pk})

@login_required
def liability_delete(request, pk):
    liability = get_object_or_404(Liability, pk=pk, user=request.user)
    if request.method == 'POST':
        liability.delete()
        messages.success(request, 'Liability deleted successfully!')
        return redirect('financialapp:liability_list')
    return render(request, 'general/confirm_delete.html', {'object': liability, 'type': 'liability'})

@login_required
def sms_create(request):
    income_types = IncomeType.objects.all().order_by('name')
    expense_types = ExpenseType.objects.all().order_by('name')
    if request.method == 'POST':
        form = MoneyRelatedSMSForm(request.POST)
        if form.is_valid():
            sms = form.save(commit=False)
            sms.user = request.user
            message_content = sms.message
            sms.is_processed =True
            sms.save()
            messages.success(request, 'SMS created successfully!')
            obj = Operations(request)
            obj.saving_income_expense(message_content)
            return redirect('financialapp:sms_create')
    else:
        form = MoneyRelatedSMSForm()

    return render(request, 'general/sms_form.html', {'form': form, 'title': 'submit SMS','income_types':income_types, 'expense_types':expense_types})