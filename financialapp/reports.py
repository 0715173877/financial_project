from socket import INADDR_UNSPEC_GROUP
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.contrib.messages import success, error, warning, info, debug
from reportlab.lib import colors
import json
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from .models import  *
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .pdf_generator import *
from django.db.models import Sum, Avg, Count
from decimal import Decimal
from json import JSONEncoder
from .financial_obj import *

class DecimalEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)  # Convert to float
            # OR return str(obj) to preserve exact precision as string
        return super(DecimalEncoder, self).default(obj)
    
@login_required
def all_reports(request):
    """View all generated reports with pagination"""
    reports = FinancialReport.objects.filter(user=request.user).order_by('-generated_at')
    
    # Add pagination
    from django.core.paginator import Paginator
    paginator = Paginator(reports, 10)  # Show 10 reports per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Report statistics
    total_reports = reports.count()
    report_types = reports.values('report_type').annotate(count=Count('id'))
    
    context = {
        'page_obj': page_obj,
        'total_reports': total_reports,
        'report_types': report_types,
    }
    return render(request, 'reports/reports.html', context)

@login_required
def delete_report(request, report_id):
    """Delete a specific report"""
    report = get_object_or_404(FinancialReport, id=report_id, user=request.user)
    
    if request.method == 'POST':
        report.delete()
        success(request, 'Report deleted successfully!')
        return redirect('all_reports')
    
    return render(request, 'reports/confirm_delete.html', {'report': report})

@login_required
def view_report(request, report_id):
    """View a specific generated report"""
    report = get_object_or_404(FinancialReport, id=report_id, user=request.user)
    
    # Render different templates based on report type
    if report.report_type == 'balance_sheet':
        template_name = 'reports/balance_sheet.html'
        context = {
            'report_data': report.data,
            'end_date': datetime.strptime(report.data['period_end'], '%Y-%m-%d').date(),
            'report_id': report.id
        }
    
    elif report.report_type == 'income_statement':
        template_name = 'reports/income_statement.html'
        context = {
            'report_data': report.data,
            'start_date': datetime.strptime(report.data['period_start'], '%Y-%m-%d').date(),
            'end_date': datetime.strptime(report.data['period_end'], '%Y-%m-%d').date(),
            'report_id': report.id
        }
    
    elif report.report_type == 'cash_flow':
        template_name = 'reports/cash_flow.html'
        context = {
            'report_data': report.data,
            'start_date': datetime.strptime(report.data['period_start'], '%Y-%m-%d').date(),
            'end_date': datetime.strptime(report.data['period_end'], '%Y-%m-%d').date(),
            'report_id': report.id
        }
    
    elif report.report_type == 'comprehensive':
        template_name = 'reports/comprehensive.html'
        context = {
            'report_data': report.data,
            'start_date': datetime.strptime(report.data['period_start'], '%Y-%m-%d').date(),
            'end_date': datetime.strptime(report.data['period_end'], '%Y-%m-%d').date(),
            'report_id': report.id
        }
    
    else:
        error(request, 'Unknown report type')
        return redirect('financial_reports')
    
    context['report'] = report
    return render(request, template_name, context)

def export_report(request, report_id):
    """Export report in different formats (PDF, CSV, etc.)"""
    report = get_object_or_404(FinancialReport, id=report_id, user=request.user)
    format_type = request.GET.get('format', 'pdf')

    if format_type == 'pdf':
        if report.report_type == 'balance_sheet':
            end_date = datetime.strptime(report.data['period_end'], '%Y-%m-%d').date()
            return generate_balance_sheet_pdf(request, report.data, end_date)
        
        elif report.report_type == 'income_statement':
            start_date = datetime.strptime(report.data['period_start'], '%Y-%m-%d').date()
            end_date = datetime.strptime(report.data['period_end'], '%Y-%m-%d').date()
            return generate_income_statement_pdf(request, report.data, start_date, end_date)
        
        elif report.report_type == 'cash_flow':
            start_date = datetime.strptime(report.data['period_start'], '%Y-%m-%d').date()
            end_date = datetime.strptime(report.data['period_end'], '%Y-%m-%d').date()
            return generate_cash_flow_pdf(request, report.data, start_date, end_date)
        
        elif report.report_type == 'comprehensive':
            start_date = datetime.strptime(report.data['period_start'], '%Y-%m-%d').date()
            end_date = datetime.strptime(report.data['period_end'], '%Y-%m-%d').date()
            return generate_comprehensive_pdf(request, report.data, start_date, end_date)
    
    elif format_type == 'csv':
        if report.report_type == 'balance_sheet':
            end_date = datetime.strptime(report.data['period_end'], '%Y-%m-%d').date()
            return generate_report_csv(request, report)
        
        elif report.report_type == 'income_statement':
            start_date = datetime.strptime(report.data['period_start'], '%Y-%m-%d').date()
            end_date = datetime.strptime(report.data['period_end'], '%Y-%m-%d').date()
            return generate_report_csv(request, report)
        
        elif report.report_type == 'cash_flow':
            start_date = datetime.strptime(report.data['period_start'], '%Y-%m-%d').date()
            end_date = datetime.strptime(report.data['period_end'], '%Y-%m-%d').date()
            return generate_report_csv(request, report)
        
        elif report.report_type == 'comprehensive':
            start_date = datetime.strptime(report.data['period_start'], '%Y-%m-%d').date()
            end_date = datetime.strptime(report.data['period_end'], '%Y-%m-%d').date()
            return generate_report_csv(request, report)
        
    elif format_type == 'json':
        if report.report_type == 'balance_sheet':
            end_date = datetime.strptime(report.data['period_end'], '%Y-%m-%d').date()
            return generate_report_json(request, report)
        
        elif report.report_type == 'income_statement':
            start_date = datetime.strptime(report.data['period_start'], '%Y-%m-%d').date()
            end_date = datetime.strptime(report.data['period_end'], '%Y-%m-%d').date()
            return generate_report_json(request, report)
        
        elif report.report_type == 'cash_flow':
            start_date = datetime.strptime(report.data['period_start'], '%Y-%m-%d').date()
            end_date = datetime.strptime(report.data['period_end'], '%Y-%m-%d').date()
            return generate_report_json(request, report)
        
        elif report.report_type == 'comprehensive':
            start_date = datetime.strptime(report.data['period_start'], '%Y-%m-%d').date()
            end_date = datetime.strptime(report.data['period_end'], '%Y-%m-%d').date()
            return generate_report_json(request, report)

@login_required
def generate_report_csv(request, report):
    """Generate CSV export for a report"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{report.report_type}_{report.period_end}.csv"'
    
    writer = csv.writer(response)
    if report.report_type == 'balance_sheet':
        writer.writerow(['Balance Sheet', f"As of {report.period_end}"])
        writer.writerow([])
        writer.writerow(['ASSETS', 'Amount (TZS)'])
        writer.writerow(['Current Assets', report.data['assets']['current_assets']])
        writer.writerow(['Fixed Assets', report.data['assets']['fixed_assets']])
        writer.writerow(['Personal Assets', report.data['assets']['personal_assets']])
        writer.writerow(['Total Assets', report.data['assets']['total_assets']])
        writer.writerow([])
        writer.writerow(['LIABILITIES', 'Amount (TZS)'])
        writer.writerow(['Current Liabilities', report.data['liabilities']['current_liabilities']])
        writer.writerow(['Long-term Liabilities', report.data['liabilities']['long_term_liabilities']])
        writer.writerow(['Total Liabilities', report.data['liabilities']['total_liabilities']])
        writer.writerow([])
        writer.writerow(['NET WORTH', report.data['net_worth']])
    
    elif report.report_type == 'income_statement':
        writer.writerow(['Income Statement', f"Period: {report.period_start} to {report.period_end}"])
        writer.writerow([])
        writer.writerow(['INCOME', 'Amount (TZS)'])
        for income_type, amount in report.data['income']['by_type'].items():
            writer.writerow([income_type, amount])
        writer.writerow(['Total Income', report.data['income']['total']])
        writer.writerow([])
        writer.writerow(['EXPENSES', 'Amount (TZS)'])
        for expense_type, amount in report.data['expenses']['by_type'].items():
            writer.writerow([expense_type, amount])
        writer.writerow(['Total Expenses', report.data['expenses']['total']])
        writer.writerow([])
        writer.writerow(['NET INCOME', report.data['net_income']])
        writer.writerow(['Savings Rate', f"{report.data['savings_rate']:.1f}%"])
    
    elif report.report_type == 'cash_flow':
        writer.writerow(['Cash Flow Statement', f"Period: {report.period_start} to {report.period_end}"])
        writer.writerow([])
        # print('========= ', report.data)
        # Operating Activities
        writer.writerow(['OPERATING ACTIVITIES', 'Amount (TZS)'])
        # for activity, amount in report.data['operating_activities'].items():
        writer.writerow(['Income', report.data['operating_activities']['income']])
        writer.writerow(['Expense', report.data['operating_activities']['expenses']])
        writer.writerow(['Net Cash from Operations', report.data['operating_activities']['net_cash']])
        writer.writerow([])
        
        # Investing Activities
        writer.writerow(['INVESTING ACTIVITIES', 'Amount (TZS)'])
        # writer.writerow([activity, amount])
        writer.writerow(['Net Cash from Investing', report.data['investing_activities']])
        writer.writerow([])
        
        # Financing Activities
        writer.writerow(['FINANCING ACTIVITIES', 'Amount (TZS)'])
        # for activity, amount in report.data['financing_activities'].items():
        #     writer.writerow([activity, amount])
        writer.writerow(['Net Cash from Financing', report.data['financing_activities']])
        writer.writerow([])

        # TOTAL 
        writer.writerow(['NET INCREASE IN CASH AND CASH EQUIVALENTS', 'Amount (TZS)'])
        total = report.data['operating_activities']['net_cash'] + report.data['investing_activities'] + report.data['financing_activities']
        # for activity, amount in report.data['financing_activities'].items():
        #     writer.writerow([activity, amount])
        writer.writerow(['Net Increase in Cash and Cash Equivalents:', total])
        writer.writerow([])
    return response

@login_required
def generate_report_json(request, report):
    """Generate JSON export for a report"""
    from django.http import JsonResponse
    
    response_data = {
        'report_type': report.report_type,
        'period_start': report.period_start.isoformat(),
        'period_end': report.period_end.isoformat(),
        'generated_at': report.generated_at.isoformat(),
        'data': report.data
    }
    
    response = JsonResponse(response_data)
    response['Content-Disposition'] = f'attachment; filename="{report.report_type}_{report.period_end}.json"'
    return response

@login_required
def financial_reports(request):
    """Main reports dashboard"""
    # Get recent reports
    recent_reports = FinancialReport.objects.filter(user=request.user)[:5]
    
    context = {
        # 'recent_reports': recent_reports,
    }
    return render(request, 'reports/financial_reports.html', context)

@login_required
def generate_balance_sheet(request):
    """Generate Balance Sheet Report"""
    obj = Operations(request)

    if request.method == 'POST':
        end_date = request.POST.get('end_date')
        if not end_date:
            end_date = datetime.date.today()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        start_date = end_date - timedelta(days=365)  # One year period
        
        # Calculate assets
        assets = Asset.objects.filter(user=request.user)
        current_assets = assets.filter(asset_type__category='Liquid')
        fixed_assets = assets.filter(asset_type__category='Investment')
        personal_assets = assets.filter(asset_type__category='Personal')
        
        total_current_assets = current_assets.aggregate(Sum('current_value'))['current_value__sum'] or 0
        total_fixed_assets = fixed_assets.aggregate(Sum('current_value'))['current_value__sum'] or 0
        total_personal_assets = personal_assets.aggregate(Sum('current_value'))['current_value__sum'] or 0
        total_assets = total_current_assets + total_fixed_assets + total_personal_assets
        
        # Calculate liabilities
        liabilities = Liability.objects.filter(user=request.user)
        current_liabilities = liabilities.filter(liability_type__category='Short-term')
        long_term_liabilities = liabilities.filter(liability_type__category='Long-term')
        
        total_current_liabilities = current_liabilities.aggregate(Sum('current_balance'))['current_balance__sum'] or 0
        total_long_term_liabilities = long_term_liabilities.aggregate(Sum('current_balance'))['current_balance__sum'] or 0
        total_liabilities = total_current_liabilities + total_long_term_liabilities
        
        # Calculate net worth
        net_worth = total_assets - total_liabilities
        
        # Prepare report data
        report_data = {
            "period_end": end_date.isoformat(),
            "assets": {
                "current_assets": float(total_current_assets),
                "fixed_assets": float(total_fixed_assets),
                "personal_assets": float(total_personal_assets),
                "total_assets": float(total_assets),
            },
            "liabilities": {
                "current_liabilities": float(total_current_liabilities),
                "long_term_liabilities": float(total_long_term_liabilities),
                "total_liabilities": float(total_liabilities),
            },
            "net_worth": float(net_worth),
            "asset_details": [
                {"name": asset.name, "value": float(asset.current_value), "type": asset.asset_type.name}
                for asset in assets
            ],
            "liability_details": [
                {"name": liability.name, "balance": float(liability.current_balance), "type": liability.liability_type.name}
                for liability in liabilities
            ]
        }

        # Save report
        report = FinancialReport.objects.create(
            user=request.user,
            report_type='balance_sheet',
            period_start=start_date,
            period_end=end_date,
            data=report_data
        )
        
        format = request.POST.get('format', 'html')
        if format == 'pdf':
            return generate_balance_sheet_pdf(request, json.dumps(str(report_data)), end_date)
        else:
            return render(request, 'reports/balance_sheet.html', {
                'report_data': report_data,
                'end_date': end_date,
                'report_id': report.id
            })
    
    return render(request, 'reports/generate_balance_sheet.html')

@login_required
def generate_income_statement(request):
    """Generate Income Statement Report"""
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        if not end_date:
            end_date = datetime.date.today()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if not start_date:
            start_date = end_date - timedelta(days=30)  # Default to last 30 days
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        # Calculate income
        incomes = Income.objects.filter(
            user=request.user,
            date_received__range=[start_date, end_date]
        )
        
        income_by_type = {}
        total_income = 0
        for income in incomes:
            income_type = income.income_type.name
            monthly_amount = income.get_monthly_amount()
            if income_type in income_by_type:
                income_by_type[income_type] += monthly_amount
            else:
                income_by_type[income_type] = monthly_amount
            total_income += monthly_amount
        
        # Calculate expenses
        expenses = Expense.objects.filter(
            user=request.user,
            date_incurred__range=[start_date, end_date]
        )
        
        expense_by_type = {}
        total_expenses = 0
        for expense in expenses:
            expense_type = expense.expense_type.name
            if expense_type in expense_by_type:
                expense_by_type[expense_type] += expense.amount
            else:
                expense_by_type[expense_type] = expense.amount
            total_expenses += expense.amount
        
        # Calculate net income
        net_income = total_income - total_expenses
        
        report_data = {
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "income": {
                "by_type": income_by_type,
                "total": float(total_income)
            },
            "expenses": {
                "by_type": expense_by_type,
                "total": float(total_expenses)
            },
            "net_income": float(net_income),
            "savings_rate": float((net_income / total_income * 100) if total_income > 0 else 0)
        }
        # Save report
        report = FinancialReport.objects.create(
            user=request.user,
            report_type='income_statement',
            period_start=start_date,
            period_end=end_date,
            data=report_data
        )
        
        format = request.POST.get('format', 'html')
        if format == 'pdf':
            return generate_income_statement_pdf(request, report_data, start_date, end_date)
        else:
            return render(request, 'reports/income_statement.html', {
                'report_data': report_data,
                'start_date': start_date,
                'end_date': end_date,
                'report_id': report.id,
                'report': report,
                
            })
        
    
    return render(request, 'reports/generate_income_statement.html')

@login_required
def generate_cash_flow_statement(request):
    """Generate Cash Flow Statement"""
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        if not end_date:
            end_date = datetime.now().date()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if not start_date:
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        # Operating Activities
        operating_income = Income.objects.filter(
            user=request.user,
            date_received__range=[start_date, end_date]
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        operating_expenses = Expense.objects.filter(
            user=request.user,
            date_incurred__range=[start_date, end_date]
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        net_operating_cash = operating_income - operating_expenses
        
        # Investing Activities (asset purchases/sales - simplified)
        investing_activities = 0  # This would require tracking asset transactions
        
        # Financing Activities (loan proceeds/repayments)
        loan_repayments = Liability.objects.filter(
            user=request.user
        ).aggregate(Sum('monthly_payment'))['monthly_payment__sum'] or 0
        
        net_financing_cash = -loan_repayments  # Negative for repayments
        
        net_cash_flow = net_operating_cash + investing_activities + net_financing_cash
        
        report_data = {
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "operating_activities": {
                "income": operating_income,
                "expenses": operating_expenses,
                "net_cash": net_operating_cash
            },
            "investing_activities": investing_activities,
            "financing_activities": net_financing_cash,
            "net_cash_flow": net_cash_flow
        }
        
        report = FinancialReport.objects.create(
            user=User.objects.get(username=request.user),
            report_type='cash_flow',
            period_start=start_date,
            period_end=end_date,
            data=report_data
        )
        
        format = request.POST.get('format', 'html')
        if format == 'pdf':
            return generate_cash_flow_pdf(request, report_data, start_date, end_date)
        else:
            return render(request, 'reports/cash_flow.html', {
                'report_data': report_data,
                'start_date': start_date,
                'end_date': end_date,
                'report_id': report.id,
                'report': report,
            })
    
    return render(request, 'reports/generate_cash_flow.html')

@login_required
def generate_comprehensive_report(request):
    """Generate Comprehensive Financial Report"""
    if request.method == 'POST':
        end_date = request.POST.get('end_date')
        if not end_date:
            end_date = datetime.now().date()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        start_date = end_date - timedelta(days=365)  # 12-month analysis period
        
        # Get all data by calling existing functions
        balance_sheet_data = get_balance_sheet_data(request.user, end_date)
        income_statement_data = get_income_statement_data(request.user, start_date, end_date)
        cash_flow_data = get_cash_flow_data(request.user, start_date, end_date)
        
        # Calculate financial ratios
        total_assets = balance_sheet_data.get('assets', {}).get('total_assets', 0)
        total_liabilities = balance_sheet_data.get('liabilities', {}).get('total_liabilities', 0)
        net_income = income_statement_data.get('net_income', 0)
        total_income = income_statement_data.get('income', {}).get('total', 0)
        net_worth = balance_sheet_data.get('net_worth', 0)
        
        # Get previous period data for growth calculation
        prev_start_date = start_date - timedelta(days=365)
        prev_end_date = end_date - timedelta(days=365)
        prev_balance_sheet_data = get_balance_sheet_data(request.user, prev_end_date)
        prev_net_worth = prev_balance_sheet_data.get('net_worth', 0)
        
        # Calculate growth rates
        net_worth_growth = ((net_worth - prev_net_worth) / prev_net_worth * 100) if prev_net_worth > 0 else 0
        
        ratios = {
            'debt_to_asset': (total_liabilities / total_assets * 100) if total_assets > 0 else 0,
            'savings_rate': (net_income / total_income * 100) if total_income > 0 else 0,
            'net_worth_growth': net_worth_growth,
            'current_ratio': (balance_sheet_data.get('assets', {}).get('current_assets', 0) / 
                             balance_sheet_data.get('liabilities', {}).get('current_liabilities', 1)) if balance_sheet_data.get('liabilities', {}).get('current_liabilities', 0) > 0 else 0,
            'return_on_assets': (net_income / total_assets * 100) if total_assets > 0 else 0,
        }
        
        report_data = {
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "balance_sheet": balance_sheet_data,
            "income_statement": income_statement_data,
            "cash_flow": cash_flow_data,
            "financial_ratios": ratios,
            "recommendations": generate_financial_recommendations(ratios, balance_sheet_data, income_statement_data)
        }
        
        # Save report
        report = FinancialReport.objects.create(
            user=request.user,
            report_type='comprehensive',
            period_start=start_date,
            period_end=end_date,
            data=report_data
        )
        
        format = request.POST.get('format', 'html')
        if format == 'pdf':
            return generate_comprehensive_pdf(request, report_data, start_date, end_date)
        else:
            return render(request, 'reports/comprehensive.html', {
                'report_data': report_data,
                'start_date': start_date,
                'end_date': end_date,
                'report_id': report.pk,
                'report': report
            })
    
    # GET request - show the form
    current_date = datetime.now().date()
    
    context = {
        'current_date': current_date,
    }
    return render(request, 'reports/generate_comprehensive.html', context)

def get_balance_sheet_data(user, end_date):
    """Extract balance sheet data for comprehensive report"""
    assets = Asset.objects.filter(user=user)
    liabilities = Liability.objects.filter(user=user)
    
    # Categorize assets
    current_assets = assets.filter(asset_type__category='Liquid').aggregate(Sum('current_value'))['current_value__sum'] or 0
    fixed_assets = assets.filter(asset_type__category='Investment').aggregate(Sum('current_value'))['current_value__sum'] or 0
    personal_assets = assets.filter(asset_type__category='Personal').aggregate(Sum('current_value'))['current_value__sum'] or 0
    total_assets = current_assets + fixed_assets + personal_assets
    
    # Categorize liabilities
    current_liabilities = liabilities.filter(liability_type__category='Short-term').aggregate(Sum('current_balance'))['current_balance__sum'] or 0
    long_term_liabilities = liabilities.filter(liability_type__category='Long-term').aggregate(Sum('current_balance'))['current_balance__sum'] or 0
    total_liabilities = current_liabilities + long_term_liabilities
    
    # Calculate net worth
    net_worth = total_assets - total_liabilities
    
    return {
        'period_end': end_date.isoformat(),
        'assets': {
            'current_assets': current_assets,
            'fixed_assets': fixed_assets,
            'personal_assets': personal_assets,
            'total_assets': total_assets,
        },
        'liabilities': {
            'current_liabilities': current_liabilities,
            'long_term_liabilities': long_term_liabilities,
            'total_liabilities': total_liabilities,
        },
        'net_worth': net_worth,
        'asset_details': [
            {
                'name': asset.name,
                'value': float(asset.current_value),
                'type': asset.asset_type.name,
                'generates_income': asset.generates_income
            }
            for asset in assets
        ],
        'liability_details': [
            {
                'name': liability.name,
                'balance': float(liability.current_balance),
                'type': liability.liability_type.name,
                'interest_rate': float(liability.interest_rate)
            }
            for liability in liabilities
        ]
    }

def get_income_statement_data(user, start_date, end_date):
    """Extract income statement data for comprehensive report"""
    # Calculate income
    incomes = Income.objects.filter(
        user=user,
        date_received__range=[start_date, end_date]
    )
    
    income_by_type = {}
    total_income = 0
    for income in incomes:
        income_type = income.income_type.name
        # Convert all income to the period equivalent
        if income.frequency == 'daily':
            period_amount = income.amount * (end_date - start_date).days
        elif income.frequency == 'weekly':
            period_amount = income.amount * ((end_date - start_date).days / 7)
        elif income.frequency == 'monthly':
            period_amount = income.amount * ((end_date - start_date).days / 30)
        elif income.frequency == 'yearly':
            period_amount = income.amount * ((end_date - start_date).days / 365)
        else:  # one_time or monthly
            period_amount = income.amount
        
        if income_type in income_by_type:
            income_by_type[income_type] += period_amount
        else:
            income_by_type[income_type] = period_amount
        total_income += period_amount
    
    # Calculate expenses
    for ex in Expense.objects.all():
        if ex.expense_type.name=="General":
            ex.is_recurring =False
            ex.save()

    expenses = Expense.objects.filter(
        user=user,
        date_incurred__range=[start_date, end_date]
    )
    # incurred_expense = expenses.filter(is_recurring=True).aggregate(Sum('amount'))['amount__sum'] or 0 * 12
    
    expense_by_type = {}
    total_expenses = 0
    for expense in expenses:
        expense_type = expense.expense_type.name
        if expense_type in expense_by_type:
            if expense.is_recurring:
                expense_by_type[expense_type] += expense.amount
            else:
                expense_by_type[expense_type] += expense.amount
        else:
            expense_by_type[expense_type] = expense.amount
        total_expenses += expense.amount

    total_expenses = 0
    expense_by_type = {}
    for expense_type in ExpenseType.objects.all().order_by('name'):
        expense_amount_incurring = 0
        expense_amount = 0
        expense_amount_incurring = expenses.filter(is_recurring=True).filter(expense_type=expense_type).aggregate(Sum('amount'))['amount__sum'] or 0       
        expense_amount = expenses.exclude(is_recurring=True).filter(expense_type=expense_type).aggregate(Sum('amount'))['amount__sum'] or 0
        if expense_amount_incurring:
            expense_by_type[str(expense_type.name)] = expense_amount_incurring * 12
            total_expenses += expense_amount_incurring * 12
        if expense_amount:
            expense_by_type[str(expense_type.name)] = expense_amount
            total_expenses +=expense_amount
        # print(total_expenses)
    # print('-------- ', total_expenses, expense_by_type)
    # Calculate net income and savings rate
    net_income = total_income - total_expenses
    savings_rate = (net_income / total_income * 100) if total_income > 0 else 0
    
    return {
        'period_start': start_date.isoformat(),
        'period_end': end_date.isoformat(),
        'income': {
            'by_type': income_by_type,
            'total': total_income
        },
        'expenses': {
            'by_type': expense_by_type,
            'total': total_expenses
        },
        'net_income': net_income,
        'savings_rate': savings_rate
    }

def get_cash_flow_data(user, start_date, end_date):
    """Extract cash flow data for comprehensive report"""
    # Operating Activities
    operating_income = Income.objects.filter(
        user=user,
        date_received__range=[start_date, end_date]
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    operating_expenses = Expense.objects.filter(
        user=user,
        date_incurred__range=[start_date, end_date]
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    net_operating_cash = operating_income - operating_expenses
    
    # Investing Activities (simplified - asset purchases/sales)
    # This would ideally track actual asset transactions
    investing_activities = 0
    
    # Financing Activities (loan repayments)
    loan_repayments = Liability.objects.filter(user=user).aggregate(
        Sum('monthly_payment')
    )['monthly_payment__sum'] or 0.0
    
    # Adjust for period (assuming monthly payments)
    days_in_period = (end_date - start_date).days
    monthly_factor = days_in_period / 30.0  # Approximate
    adjusted_loan_repayments = float(loan_repayments) * float(monthly_factor)
    
    net_financing_cash = - adjusted_loan_repayments
    
    net_cash_flow = net_operating_cash + investing_activities + net_financing_cash
    
    return {
        'period_start': start_date.isoformat(),
        'period_end': end_date.isoformat(),
        'operating_activities': {
            'income': float(operating_income),
            'expenses': float(operating_expenses),
            'net_cash': float(net_operating_cash)
        },
        'investing_activities': float(investing_activities),
        'financing_activities': float(net_financing_cash),
        'net_cash_flow': float(net_cash_flow)
    }

def generate_financial_recommendations(ratios, balance_sheet_data, income_statement_data):
    """Generate personalized financial recommendations based on comprehensive analysis"""
    recommendations = []
    
    # Debt analysis
    debt_ratio = ratios.get('debt_to_asset', 0)
    if debt_ratio > 60:
        recommendations.append("Your debt levels are high. Consider focusing on paying down high-interest debt to improve your debt-to-asset ratio.")
    elif debt_ratio > 40:
        recommendations.append("Your debt levels are manageable but could be optimized. Consider paying off higher-interest debts first.")
    elif debt_ratio < 20:
        recommendations.append("You have low debt levels, which is excellent for financial stability.")
    
    # Savings analysis
    savings_rate = ratios.get('savings_rate', 0)
    if savings_rate < 10:
        recommendations.append("Your savings rate is low. Try to increase it to at least 15-20% for better financial security and future growth.")
    elif savings_rate < 20:
        recommendations.append("Good savings rate! Consider increasing to 20% or more to accelerate wealth building.")
    else:
        recommendations.append("Excellent savings rate! You're on track for strong financial growth.")
    
    # Net worth growth
    net_worth_growth = ratios.get('net_worth_growth', 0)
    if net_worth_growth < 5:
        recommendations.append("Your net worth growth is slow. Consider reviewing your investment strategy and expense management.")
    elif net_worth_growth > 15:
        recommendations.append("Strong net worth growth! Continue with your current financial strategy.")
    
    # Current ratio analysis
    current_ratio = ratios.get('current_ratio', 0)
    if current_ratio < 1:
        recommendations.append("Your current ratio indicates potential liquidity issues. Build up your emergency fund and liquid assets.")
    elif current_ratio > 3:
        recommendations.append("You have strong liquidity. Consider putting some excess cash to work in higher-yielding investments.")
    
    # Return on assets
    return_on_assets = ratios.get('return_on_assets', 0)
    if return_on_assets < 5:
        recommendations.append("Your return on assets is low. Consider reviewing your investment portfolio for better returns.")
    
    # Income diversification
    income_sources = len(income_statement_data.get('income', {}).get('by_type', {}))
    if income_sources < 2:
        recommendations.append("Consider diversifying your income sources to reduce financial risk and increase stability.")
    
    # Emergency fund check
    current_assets = balance_sheet_data.get('assets', {}).get('current_assets', 0)
    monthly_expenses = income_statement_data.get('expenses', {}).get('total', 0) / 12  # Approximate monthly
    if current_assets < monthly_expenses * 3:
        recommendations.append("Build your emergency fund to cover 3-6 months of essential expenses for better financial security.")
    
    # If no specific issues found
    if not recommendations:
        recommendations.append("Your financial position appears healthy. Continue monitoring your finances regularly and maintain your good habits.")
    
    return recommendations[:6]  # Return top 6 recommendations
    """Generate personalized financial recommendations"""
    recommendations = []
    
    if ratios['debt_to_asset'] > 50:
        recommendations.append("Consider paying down high-interest debt to improve your debt-to-asset ratio.")
    
    if ratios['savings_rate'] < 20:
        recommendations.append("Try to increase your savings rate to at least 20% for better financial security.")
    
    if len(recommendations) == 0:
        recommendations.append("Your financial ratios look healthy. Continue with your current strategy!")
    
    return recommendations