from io import BytesIO
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
from .financial_obj import *

def generate_balance_sheet_pdf(request, report_data, end_date):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    elements = []
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Center', alignment=1, spaceAfter=30))
    styles.add(ParagraphStyle(name='Right', alignment=2))
    
    # Title
    elements.append(Paragraph("BALANCE SHEET", styles['Heading1']))
    elements.append(Paragraph(f"As of {end_date.strftime('%B %d, %Y')}", styles['Center']))
    elements.append(Spacer(1, 20))
    
    # Assets Section
    elements.append(Paragraph("ASSETS", styles['Heading2']))
    assets_data = [
        ['Current Assets', f"TZS {report_data['assets']['current_assets']:,.2f}"],
        ['Fixed Assets', f"TZS {report_data['assets']['fixed_assets']:,.2f}"],
        ['Personal Assets', f"TZS {report_data['assets']['personal_assets']:,.2f}"],
        ['Total Assets', f"TZS {report_data['assets']['total_assets']:,.2f}"]
    ]
    
    assets_table = Table(assets_data, colWidths=[3*inch, 2*inch])
    assets_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
    ]))
    elements.append(assets_table)
    elements.append(Spacer(1, 20))
    
    # Liabilities & Net Worth Section
    elements.append(Paragraph("LIABILITIES & NET WORTH", styles['Heading2']))
    
    liabilities_data = [
        ['Current Liabilities', f"TZS {report_data['liabilities']['current_liabilities']:,.2f}"],
        ['Long-term Liabilities', f"TZS {report_data['liabilities']['long_term_liabilities']:,.2f}"],
        ['Total Liabilities', f"TZS {report_data['liabilities']['total_liabilities']:,.2f}"],
        ['', ''],
        ['NET WORTH', f"TZS {report_data['net_worth']:,.2f}"]
    ]
    
    liabilities_table = Table(liabilities_data, colWidths=[3*inch, 2*inch])
    liabilities_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (2, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
    ]))
    elements.append(liabilities_table)
    
    doc.build(elements)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="balance_sheet_{end_date}.pdf"'
    return response

def generate_cash_flow_pdf(request, report_data, start_date, end_date):
    """Generate PDF for Cash Flow Statement"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    elements = []
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Center', alignment=1, spaceAfter=30))
    styles.add(ParagraphStyle(name='Right', alignment=2))
    styles.add(ParagraphStyle(name='Bold', fontName='Helvetica-Bold', fontSize=10))
    
    # Title
    elements.append(Paragraph("CASH FLOW STATEMENT", styles['Heading1']))
    elements.append(Paragraph(f"For the Period {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}", styles['Center']))
    elements.append(Spacer(1, 30))
    
    # Operating Activities
    elements.append(Paragraph("CASH FLOWS FROM OPERATING ACTIVITIES", styles['Heading2']))
    
    operating_data = [
        ['Cash received from income:', f"TZS {report_data['operating_activities']['income']:,.2f}"],
        ['Cash paid for expenses:', f"(TZS {report_data['operating_activities']['expenses']:,.2f})"],
        ['', ''],
        ['Net Cash Provided by Operating Activities:', f"TZS {report_data['operating_activities']['net_cash']:,.2f}"]
    ]
    
    operating_table = Table(operating_data, colWidths=[3.5*inch, 2*inch])
    operating_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(operating_table)
    elements.append(Spacer(1, 20))
    
    # Investing Activities
    elements.append(Paragraph("CASH FLOWS FROM INVESTING ACTIVITIES", styles['Heading2']))
    
    investing_data = [
        ['Purchase/Sale of Assets:', f"TZS {report_data['investing_activities']:,.2f}"],
        ['', ''],
        ['Net Cash Used in Investing Activities:', f"TZS {report_data['investing_activities']:,.2f}"]
    ]
    
    investing_table = Table(investing_data, colWidths=[3.5*inch, 2*inch])
    investing_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
    ]))
    elements.append(investing_table)
    elements.append(Spacer(1, 20))
    
    # Financing Activities
    elements.append(Paragraph("CASH FLOWS FROM FINANCING ACTIVITIES", styles['Heading2']))
    
    financing_data = [
        ['Loan Repayments:', f"(TZS {abs(report_data['financing_activities']):,.2f})"],
        ['', ''],
        ['Net Cash Used in Financing Activities:', f"TZS {report_data['financing_activities']:,.2f}"]
    ]
    
    financing_table = Table(financing_data, colWidths=[3.5*inch, 2*inch])
    financing_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
    ]))
    elements.append(financing_table)
    elements.append(Spacer(1, 20))
    
    # Net Increase in Cash
    elements.append(Paragraph("NET INCREASE IN CASH AND CASH EQUIVALENTS", styles['Heading2']))
    
    net_cash_data = [
        ['', ''],
        ['Net Increase in Cash and Cash Equivalents:', f"TZS {report_data['net_cash_flow']:,.2f}"]
    ]
    
    net_cash_table = Table(net_cash_data, colWidths=[3.5*inch, 2*inch])
    net_cash_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
    ]))
    elements.append(net_cash_table)
    elements.append(Spacer(1, 30))
    
    # Cash Flow Analysis
    elements.append(Paragraph("CASH FLOW ANALYSIS", styles['Heading2']))
    
    if report_data['net_cash_flow'] > 0:
        analysis_text = """
        <b>POSITIVE CASH FLOW</b><br/>
        Your business is generating more cash than it is spending. This is a healthy financial position 
        that allows for investment, debt reduction, or savings accumulation.
        """
    else:
        analysis_text = """
        <b>NEGATIVE CASH FLOW</b><br/>
        Your cash outflows exceed your cash inflows. Consider reviewing your expenses, 
        increasing income sources, or managing your cash reserves carefully.
        """
    
    elements.append(Paragraph(analysis_text, styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Key Metrics
    elements.append(Paragraph("KEY METRICS", styles['Heading2']))
    
    metrics_data = [
        ['Operating Cash Flow Margin:', f"{(report_data['operating_activities']['net_cash'] / report_data['operating_activities']['income'] * 100) if report_data['operating_activities']['income'] > 0 else 0:.1f}%"],
        ['Cash Flow Coverage Ratio:', f"{(report_data['operating_activities']['net_cash'] / abs(report_data['financing_activities'])) if report_data['financing_activities'] < 0 else 'N/A'}"],
    ]
    
    metrics_table = Table(metrics_data, colWidths=[3*inch, 2*inch])
    metrics_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(metrics_table)
    
    doc.build(elements)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="cash_flow_{start_date}_{end_date}.pdf"'
    return response

def generate_comprehensive_pdf(request, report_data, start_date, end_date):
    """Generate PDF for Comprehensive Financial Report"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    elements = []
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Center', alignment=1, spaceAfter=30))
    styles.add(ParagraphStyle(name='Right', alignment=2))
    styles.add(ParagraphStyle(name='Bold', fontName='Helvetica-Bold', fontSize=10))
    
    # Title and Header
    elements.append(Paragraph("COMPREHENSIVE FINANCIAL REPORT", styles['Heading1']))
    elements.append(Paragraph(f"Period: {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}", styles['Center']))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %H:%M')}", styles['Center']))
    elements.append(Spacer(1, 30))
    
    # Executive Summary
    elements.append(Paragraph("EXECUTIVE SUMMARY", styles['Heading2']))
    
    # Calculate key metrics for summary
    net_worth = report_data['balance_sheet']['net_worth']
    total_assets = report_data['balance_sheet']['assets']['total_assets']
    total_liabilities = report_data['balance_sheet']['liabilities']['total_liabilities']
    net_income = report_data['income_statement']['net_income']
    total_income = report_data['income_statement']['income']['total']
    net_cash_flow = report_data['cash_flow']['net_cash_flow']
    
    summary_text = f"""
    This comprehensive financial report provides a complete overview of your financial position 
    and performance during the specified period. Key highlights include:
    
    • <b>Net Worth:</b> TZS {net_worth:,.2f}
    • <b>Net Income:</b> TZS {net_income:,.2f}
    • <b>Net Cash Flow:</b> TZS {net_cash_flow:,.2f}
    • <b>Savings Rate:</b> {report_data['income_statement']['savings_rate']:.1f}%
    • <b>Debt-to-Asset Ratio:</b> {report_data['financial_ratios']['debt_to_asset']:.1f}%
    """
    
    elements.append(Paragraph(summary_text, styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Balance Sheet Section
    elements.append(Paragraph("BALANCE SHEET ANALYSIS", styles['Heading2']))
    
    balance_sheet_data = [
        ['ASSETS', '', 'LIABILITIES & NET WORTH', ''],
        ['Current Assets', f"TZS {report_data['balance_sheet']['assets']['current_assets']:,.2f}", 
         'Current Liabilities', f"TZS {report_data['balance_sheet']['liabilities']['current_liabilities']:,.2f}"],
        ['Fixed Assets', f"TZS {report_data['balance_sheet']['assets']['fixed_assets']:,.2f}", 
         'Long-term Liabilities', f"TZS {report_data['balance_sheet']['liabilities']['long_term_liabilities']:,.2f}"],
        ['Personal Assets', f"TZS {report_data['balance_sheet']['assets']['personal_assets']:,.2f}", 
         'Total Liabilities', f"TZS {total_liabilities:,.2f}"],
        ['', '', '', ''],
        ['Total Assets', f"TZS {total_assets:,.2f}", 'NET WORTH', f"TZS {net_worth:,.2f}"],
    ]
    
    balance_sheet_table = Table(balance_sheet_data, colWidths=[1.8*inch, 1.2*inch, 1.8*inch, 1.2*inch])
    balance_sheet_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(balance_sheet_table)
    elements.append(Spacer(1, 20))
    
    # Income Statement Section
    elements.append(Paragraph("INCOME STATEMENT ANALYSIS", styles['Heading2']))
    
    income_statement_data = [
        ['REVENUE', 'Amount (TZS)', 'EXPENSES', 'Amount (TZS)'],
    ]
    
    # Add income items
    max_rows = max(len(report_data['income_statement']['income']['by_type']), 
                   len(report_data['income_statement']['expenses']['by_type']))
    
    income_items = list(report_data['income_statement']['income']['by_type'].items())
    expense_items = list(report_data['income_statement']['expenses']['by_type'].items())
    
    for i in range(max_rows):
        income_row = income_items[i] if i < len(income_items) else ('', '')
        expense_row = expense_items[i] if i < len(expense_items) else ('', '')
        
        income_statement_data.append([
            income_row[0], 
            f"TZS {income_row[1]:,.2f}" if income_row[1] else '',
            expense_row[0], 
            f"TZS {expense_row[1]:,.2f}" if expense_row[1] else ''
        ])
    
    # Add totals
    income_statement_data.append(['', '', '', ''])
    income_statement_data.append([
        'Total Income:', 
        f"TZS {total_income:,.2f}",
        'Total Expenses:', 
        f"TZS {report_data['income_statement']['expenses']['total']:,.2f}"
    ])
    income_statement_data.append(['', '', '', ''])
    income_statement_data.append([
        'NET INCOME:', 
        f"TZS {net_income:,.2f}", 
        'Savings Rate:', 
        f"{report_data['income_statement']['savings_rate']:.1f}%"
    ])
    
    income_statement_table = Table(income_statement_data, colWidths=[1.5*inch, 1.2*inch, 1.5*inch, 1.2*inch])
    income_statement_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -2), (-1, -1), 'Helvetica-Bold'),
        ('LINEABOVE', (0, -2), (-1, -2), 1, colors.black),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
    ]))
    elements.append(income_statement_table)
    elements.append(Spacer(1, 20))
    
    # Cash Flow Section
    elements.append(Paragraph("CASH FLOW ANALYSIS", styles['Heading2']))
    
    cash_flow_data = [
        ['CASH FLOW CATEGORY', 'AMOUNT (TZS)'],
        ['Operating Activities', f"TZS {report_data['cash_flow']['operating_activities']['net_cash']:,.2f}"],
        ['Investing Activities', f"TZS {report_data['cash_flow']['investing_activities']:,.2f}"],
        ['Financing Activities', f"TZS {report_data['cash_flow']['financing_activities']:,.2f}"],
        ['', ''],
        ['NET CASH FLOW: ', f"TZS {net_cash_flow:,.2f}"]
    ]
    
    cash_flow_table = Table(cash_flow_data, colWidths=[3*inch, 2*inch])
    cash_flow_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
    ]))
    elements.append(cash_flow_table)
    elements.append(Spacer(1, 20))
    
    # Financial Ratios Section
    elements.append(Paragraph("FINANCIAL RATIOS & METRICS", styles['Heading2']))
    
    ratios_data = [
        ['RATIO', 'VALUE', 'INTERPRETATION'],
        ['Debt-to-Asset Ratio', f"{report_data['financial_ratios']['debt_to_asset']:.1f}%", 
         get_ratio_interpretation('debt_to_asset', report_data['financial_ratios']['debt_to_asset'])],
        ['Savings Rate', f"{report_data['financial_ratios']['savings_rate']:.1f}%", 
         get_ratio_interpretation('savings_rate', report_data['financial_ratios']['savings_rate'])],
        ['Net Worth Growth', f"{report_data['financial_ratios']['net_worth_growth']:.1f}%", 
         get_ratio_interpretation('net_worth_growth', report_data['financial_ratios']['net_worth_growth'])],
    ]
    
    ratios_table = Table(ratios_data, colWidths=[1.5*inch, 1*inch, 2.5*inch])
    ratios_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(ratios_table)
    elements.append(Spacer(1, 20))
    
    # Recommendations Section
    elements.append(Paragraph("FINANCIAL RECOMMENDATIONS", styles['Heading2']))
    
    if report_data['recommendations']:
        for i, recommendation in enumerate(report_data['recommendations'], 1):
            elements.append(Paragraph(f"{i}. {recommendation}", styles['Normal']))
    else:
        elements.append(Paragraph("No specific recommendations at this time. Your financial position appears healthy.", styles['Normal']))
    
    elements.append(Spacer(1, 20))
    
    # Risk Assessment
    elements.append(Paragraph("RISK ASSESSMENT", styles['Heading2']))
    
    risk_level = "LOW"
    if report_data['financial_ratios']['debt_to_asset'] > 60:
        risk_level = "HIGH"
    elif report_data['financial_ratios']['debt_to_asset'] > 40:
        risk_level = "MEDIUM"
    
    risk_text = f"""
    Based on the analysis of your financial ratios and cash flow patterns, your overall financial risk level is assessed as:
    
    <b>{risk_level} RISK</b>
    
    This assessment considers your debt levels, savings rate, cash flow stability, and net worth position.
    """
    
    elements.append(Paragraph(risk_text, styles['Normal']))
    
    doc.build(elements)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="comprehensive_report_{start_date}_{end_date}.pdf"'
    return response

def get_ratio_interpretation(ratio_type, value):
    """Helper function to provide interpretations for financial ratios"""
    interpretations = {
        'debt_to_asset': {
            'range': [(0, 30, 'Excellent'), (30, 50, 'Good'), (50, 70, 'Fair'), (70, 100, 'Concerning')]
        },
        'savings_rate': {
            'range': [(20, 100, 'Excellent'), (15, 20, 'Good'), (10, 15, 'Fair'), (0, 10, 'Needs Improvement')]
        },
        'net_worth_growth': {
            'range': [(10, 100, 'Strong'), (5, 10, 'Good'), (0, 5, 'Stable'), (-100, 0, 'Declining')]
        }
    }
    
    if ratio_type in interpretations:
        for min_val, max_val, interpretation in interpretations[ratio_type]['range']:
            if min_val <= value <= max_val:
                return interpretation
    
    return "No data"

def generate_income_statement_pdf(request, report_data, start_date, end_date):
    """Generate PDF for income statement"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph("INCOME STATEMENT", styles['Heading1']))
    elements.append(Paragraph(f"Period: {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    # Income Section
    elements.append(Paragraph("INCOME", styles['Heading2']))
    income_data = []
    for income_type, amount in report_data['income']['by_type'].items():
        income_data.append([income_type, f"TZS {amount:,.2f}"])
    income_data.append(['Total Income', f"TZS {report_data['income']['total']:,.2f}"])

    income_table = Table(income_data, colWidths=[3*inch, 2*inch])
    income_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
    ]))
    elements.append(income_table)
    elements.append(Spacer(1, 20))

    # Expenses Section
    elements.append(Paragraph("EXPENSES", styles['Heading2']))
    expenses_data = []
    for expense_type, amount in report_data['expenses']['by_type'].items():
        expenses_data.append([expense_type, f"TZS {amount:,.2f}"])
    expenses_data.append(['Total Expenses', f"TZS {report_data['expenses']['total']:,.2f}"])

    expenses_table = Table(expenses_data, colWidths=[3*inch, 2*inch])
    expenses_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
    ]))
    elements.append(expenses_table)
    elements.append(Spacer(1, 20))

    # Net Income Section
    net_income = report_data['income']['total'] - report_data['expenses']['total']
    net_income_data = [
        ['Net Income', f"TZS {net_income:,.2f}"]
    ]

    net_income_table = Table(net_income_data, colWidths=[3*inch, 2*inch])
    net_income_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('LINEABOVE', (0, 0), (-1, -1), 1, colors.black),
        ('LINEBELOW', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(net_income_table)

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="income_statement_{end_date}.pdf"'
    return response
















