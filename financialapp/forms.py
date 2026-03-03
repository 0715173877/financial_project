from django import forms
from .models import *

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['income_type', 'amount', 'frequency', 'date_received', 'description', 'is_recurring']
        widgets = {
            'date_received': forms.DateInput(attrs={'type': 'date'}),
            'amount': forms.TextInput(attrs={'type': 'number', 'step':0.01}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'is_recurring': forms.CheckboxInput(attrs={'type': 'checkbox', 'class':'form-check-input'})
        }
    
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     for field in self.fields:
    #         self.fields[field].widget.attrs.update({'class': 'form-control'})

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['expense_type', 'amount', 'date_incurred', 'description', 'is_recurring']
        widgets = {
            'date_incurred': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'amount': forms.TextInput(attrs={'type': 'number', 'step':0.01}),
        }
    
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     for field in self.fields:
    #         self.fields[field].widget.attrs.update({'class': 'form-control'})

class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['asset_type', 'name', 'description', 'current_value', 'purchase_price', 
                 'purchase_date', 'monthly_income', 'notes', 'generates_income']
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'current_value': forms.TextInput(attrs={'type': 'number', 'step':0.01}),
            'purchase_price': forms.TextInput(attrs={'type': 'number', 'step':0.01}),
            'monthly_income': forms.TextInput(attrs={'type': 'number', 'step':0.01}),

        }
    
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     for field in self.fields:
    #         self.fields[field].widget.attrs.update({'class': 'form-control'})

class LiabilityForm(forms.ModelForm):
    class Meta:
        model = Liability
        fields = ['liability_type', 'name', 'description', 'original_amount', 
                 'current_balance', 'interest_rate', 'monthly_payment', 'due_date', 'lender']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'original_amount': forms.TextInput(attrs={'type': 'number', 'step':0.01}),
            'current_balance': forms.TextInput(attrs={'type': 'number', 'step':0.01}),
            'monthly_payment': forms.TextInput(attrs={'type': 'number', 'step':0.01}),
            'interest_rate': forms.TextInput(attrs={'type': 'number', 'step':0.01}),

        }
    


class MoneyRelatedSMSForm(forms.ModelForm):
    class Meta:
        model = MoneyRelatedSMS
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 10, 'class': 'form-control'}),
        }



