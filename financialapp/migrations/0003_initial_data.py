# financialapp/migrations/0002_initial_data.py
from django.db import migrations

def create_initial_data(apps, schema_editor):
    # Get models
    IncomeType = apps.get_model('financialapp', 'IncomeType')
    ExpenseType = apps.get_model('financialapp', 'ExpenseType')
    AssetType = apps.get_model('financialapp', 'AssetType')
    LiabilityType = apps.get_model('financialapp', 'LiabilityType')
    
    # Income Types
    income_types = [
        ('Salary', 'Regular employment salary'),
        ('Business Income', 'Income from business activities'),
        ('Rental Income', 'Income from property rentals'),
        ('Investment Income', 'Dividends, interest, etc.'),
        ('Freelance', 'Contract or freelance work'),
        ('Bonus', 'Performance or annual bonus'),
        ('Other Income', 'Other sources of income'),
    ]
    
    for name, desc in income_types:
        IncomeType.objects.create(name=name, description=desc)
    
    # Expense Types
    expense_types = [
        ('Home Spendings', 'Fixed', 'Regular household expenses'),
        ('Children School', 'Fixed', 'Education and school fees'),
        ('Clothes', 'Variable', 'Clothing and personal items'),
        ('Transport Fuel', 'Variable', 'Transportation costs'),
        ('Communication', 'Fixed', 'Phone, internet, etc.'),
        ('Taxes', 'Periodic', 'Income and property taxes'),
        ('Food & Groceries', 'Variable', 'Food and household supplies'),
        ('Utilities', 'Fixed', 'Electricity, water, etc.'),
        ('Entertainment', 'Variable', 'Leisure activities'),
        ('Healthcare', 'Variable', 'Medical expenses'),
    ]
    
    for name, category, desc in expense_types:
        ExpenseType.objects.create(name=name, category=category, description=desc)
    
    # Asset Types
    asset_types = [
        ('Cash', 'Liquid', False, 'Physical cash and bank accounts'),
        ('Real Estate', 'Investment', False, 'Properties and land'),
        ('Vehicles', 'Personal', True, 'Cars, motorcycles, etc.'),
        ('Investments', 'Investment', False, 'Stocks, bonds, etc.'),
        ('Business', 'Investment', False, 'Business ownership'),
        ('Personal Property', 'Personal', True, 'Electronics, furniture, etc.'),
    ]
    
    for name, category, depreciable, desc in asset_types:
        AssetType.objects.create(
            name=name, 
            category=category, 
            is_depreciable=depreciable, 
            description=desc
        )
    
    # Liability Types
    liability_types = [
        ('Personal Loan', 'Short-term', True, 'Personal loans from banks/friends'),
        ('Mortgage', 'Long-term', True, 'Property mortgage'),
        ('Car Loan', 'Long-term', True, 'Vehicle financing'),
        ('Credit Card', 'Short-term', True, 'Credit card debt'),
        ('SACCO Loan', 'Short-term', True, 'Loans from SACCOs'),
        ('Business Loan', 'Long-term', True, 'Loans for business'),
    ]
    
    for name, category, has_interest, desc in liability_types:
        LiabilityType.objects.create(
            name=name, 
            category=category, 
            has_interest=has_interest, 
            description=desc
        )

class Migration(migrations.Migration):
    dependencies = [
        ('financialapp', '0001_initial'),
    ]
    
    operations = [
        migrations.RunPython(create_initial_data),
    ]