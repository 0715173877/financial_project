from mailbox import Message
import re
from decimal import Decimal
from types import NoneType
from .models import *
from django.db.models import Sum, Avg
import random
from django.core.paginator import Paginator

class Operations:
    def __init__(self, request) -> None:
        self.request = request
        try:
            self.user = User.objects.get(id=self.request.user.id)
        except:
            self.user = None

    def get_pagination(self, objects=None, number=10):
        paginator = Paginator(objects, number)  # Show 10 expenses per page
        page_number = self.request.GET.get('page')
        obj = paginator.get_page(page_number)
        return obj

    def barchart(self):
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        current_year = datetime.now().year
        total_expenses_months = []
        total_income_months = []
        for i, month in enumerate(months):
            i+=1
            # print('---', i, month)
            expenses_amount = Expense.objects.filter(
                user=self.request.user,
                date_incurred__month=i,
                date_incurred__year=current_year
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            total_expenses_months.append(expenses_amount)
            income_amount = Income.objects.filter(
                user=self.request.user,
                date_received__month=i,
                date_received__year=current_year
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            total_income_months.append(income_amount)

        return {
            'months': months,
            'income':total_income_months,
            'expense':total_expenses_months
        }
    
    def generate_unique_colors(self,num_colors):
        """Generate unique random colors without repetition"""
        colors = set()
        
        while len(colors) < num_colors:
            color = '#{:06x}'.format(random.randint(0, 0xFFFFFF))
            colors.add(color)
        
        return list(colors)
        
    def asset_chart(self):
        assets = Asset.objects.filter(user=self.request.user)
        colors = self.generate_unique_colors(len(assets))
        assets_data = []
        assets_type = []
        for i in AssetType.objects.all().order_by('name'):
            total_assets = assets.filter(asset_type=i).aggregate(Sum('current_value'))['current_value__sum'] or 0
            assets_data.append(total_assets)
            assets_type.append(i.name)

        return {
            'asset_type':assets_type,
            'asset_value':assets_data,
            'colors':colors
        }
    
    def income_vs_type(self):
        current_year = datetime.now().year
        total_income_months = []
        income_types = []
        income_types_all =IncomeType.objects.all().order_by('name')
        colors = self.generate_unique_colors(len(income_types_all))
        for inc_type in income_types_all:
            income_amount = Income.objects.filter(
                income_type=inc_type,
                user=self.request.user,
                date_received__year=current_year
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            total_income_months.append(income_amount)
            income_types.append(inc_type.name)
            
        return {
                'colors':colors,
                'income_types':income_types,
                'total_income_months':total_income_months

        }

    def expense_vs_category(self):
        total_expenses_months = []
        expense_types = []
        current_year = datetime.now().year
        expense_types_all = ExpenseType.objects.all().order_by('name')
        colors = self.generate_unique_colors(len(expense_types_all))
        for exp_type in expense_types_all:
            expenses_amount = Expense.objects.filter(
                expense_type=exp_type,
                user=self.request.user,
                date_incurred__year=current_year
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            total_expenses_months.append(expenses_amount)
            expense_types.append(exp_type.name)

        return {
                'colors':colors,
                'expense_types':expense_types,
                'total_expenses_months':total_expenses_months
                
        }
    
    def cashflow_chart(self):
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        current_year = datetime.now().year
        total_expenses_months = []
        total_income_months = []
        net_cash_flow_months = []
        for i, month in enumerate(months):
            expenses_amount = Expense.objects.filter(
                user=self.request.user,
                date_incurred__month=i,
                date_incurred__year=current_year
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            total_expenses_months.append(expenses_amount)
            income_amount = Income.objects.filter(
                user=self.request.user,
                date_received__month=i,
                date_received__year=current_year
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            total_income_months.append(income_amount)
            net_cash_flow_months.append((float(income_amount)-float(expenses_amount)))

        return {
            'months': months,
            'income':total_income_months,
            'expense':total_expenses_months,
            'net_cash':net_cash_flow_months
        }

    def convert_decimals_to_floors(self, s):
        # Replace Decimal("123.45") with 123.45
        return re.sub(r'Decimal\("([^"]+)"\)', r'\1', s)

    def convert_decimals_to_floats(self, obj):
        """
        Recursively convert all Decimal objects to floats in a dictionary/list
        """
        if isinstance(obj, dict):
            return {key: self.convert_decimals_to_floats(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_decimals_to_floats(item) for item in obj]
        elif isinstance(obj, Decimal):
            return float(obj)
        else:
            return obj
    
    def match_exact_word_ignore_case(self,text, target_word):
        """
        Match exact word ignoring case
        """
        pattern = r'\b' + re.escape(target_word) + r'\b'
        matches = re.findall(pattern, text, re.IGNORECASE)
        return matches

    def detect_keyword(self,my_keywords, message):
        my_keywords = [kw for kw in my_keywords]
        message = str(message).split()
        # print('------', message)
        for word in my_keywords:
            text_lower = word.keyword.lower()
            found_count = 0
            found_words = []
            # print('=---= ', text_lower)
            for term in message:
                # print('====== ', term)
                matches = self.match_exact_word_ignore_case(text_lower, term)
                if matches:
                    found_count += 1
                    found_words.append(term)
                    # print('------', term.lower(), found_count, found_words)
            if found_count >= 2:

                return {
                        'status':True, 
                        'word':word.pk
                    }
        return {
            'status':False, 
            'word': None
        }
    def saving_income_expense(self, message):
        income_type = None
        expense_type = None
        my_keywords = KeyWordExpenseType.objects.filter(user=self.user)
        detected_data = self.detect_from_message(message)
        if self.request.POST.get('income_type') or self.request.POST.get('expense_type'):
            income_type = self.request.POST.get('income_type')
            expense_type = self.request.POST.get('expense_type')
        else:
            name="General"
        print('------ ', income_type, expense_type)
        is_recurring = False
        if my_keywords:
            data = self.detect_keyword(my_keywords,message)
            # print('----', data)
            if data['status']:
                is_recurring =True
                name = ExpenseType.objects.get(id=KeyWordExpenseType.objects.get(id=data['word']).expense_type.pk).name
        if detected_data['sms_type'] == 'expense' or detected_data['sms_type'] == 'transfer':
            if expense_type:
                name = ExpenseType.objects.get(id=expense_type).name
            Expense.objects.create(
                user = self.user,
                expense_type = ExpenseType.objects.get(name=name),
                amount = detected_data['amount'],
                is_recurring = is_recurring,
                description = detected_data['message'],
                date_incurred = datetime.now()
            )
        elif detected_data['sms_type'] == 'income':
            if income_type:
                name = IncomeType.objects.get(id=income_type).name
            Income.objects.create(
                user = self.user,
                income_type = IncomeType.objects.get(name=name),
                amount = detected_data['amount'],
                description = detected_data['message'],
                is_recurring =False,
                date_received = datetime.now()
            )
        
    def detect_from_message(self, message):
        """Extract SMS data from message text"""
        detected_data = {}
        
        if not message:
            return detected_data
        
        message_upper = message.upper()
        message_lower = message.lower()
        
        # Detect sender
        detected_data['sender'] = self.detect_sender(message_upper)
        
        # Detect amount
        if re.search(r'salio lako', message_lower, re.IGNORECASE) and re.search(r'umetuma', message_lower, re.IGNORECASE):
            # Remove everything before "Umetuma"
            message_lower = re.sub(r'^.*?umetuma', 'umetuma', message_lower, flags=re.IGNORECASE)
        detected_data['amount'] = self.detect_amount(message_lower)
        
        #Message
        detected_data['sms_type'] = self.detect_sms_type(message_lower)

        # Detect SMS type
        detected_data['message'] = message
        
        return detected_data

    def detect_sender(self, message):
        """Detect sender from message content"""
        common_senders = {
            'MPESA': ['MPESA'],
            'YAS': ['TIGO', 'TIGO PESA', "MIXX BY YAS","MIXX"],
            'Airtel Money': ['AIRTEL', 'AIRTEL MONEY'],
            'CRDB Bank': ['CRDB'],
            'NMB Bank': ['NMB'],
            'Stanbic Bank': ['STANBIC'],
            'Selcom Bank': ['SELCOM'],
            'Equity Bank': ['EQUITY'],
            'KCB Bank': ['KCB'],
            'DTB Bank': ['DTB'],
            'Bank of Baroda': ['BARODA'],
            'PBZ Bank': ['PBZ'],
            'Exim Bank': ['EXIM'],
            'Azania Bank': ['AZANIA'],
        }
        
        for sender, keywords in common_senders.items():
            for keyword in keywords:
                if keyword in message:
                    return sender
        
        return ''

    def detect_amount(self, message):
        """Extract amount from message - handles TZS/TSH prefixes and suffixes"""
        amount_patterns = [
            # Patterns with TZS/TSH prefix
            r'(?:tsh|tzs)[\s:]*([\d,]+\.?\d*)',  # tsh 50,000 or tzs:50000
            r'(?:TSH|TZS)[\s:]*([\d,]+\.?\d*)',  # TSH 50,000 or TZS:50000
            
            # Patterns with TZS/TSH suffix  
            r'([\d,]+\.?\d*)[\s]*(?:tsh|tzs)',  # 50,000 tsh or 50000tzs
            r'([\d,]+\.?\d*)[\s]*(?:TSH|TZS)',  # 50,000 TSH or 50000TZS
            
            # Patterns with shilling prefix/suffix
            r'sh[\s:]*([\d,]+\.?\d*)',  # sh 50000
            r'([\d,]+\.?\d*)[\s]*sh',   # 50000 sh
            
            # General amount patterns (fallback)
            r'([\d,]+\.?\d*)\s*(?:/=|/=s)',  # 50,000/=
            r'amount[\s:]*([\d,]+\.?\d*)',   # amount: 50000
            r'amt[\s:]*([\d,]+\.?\d*)',      # amt: 50000
            r'value[\s:]*([\d,]+\.?\d*)',    # value: 50000
        ]
        
        # Clean the message - remove extra spaces for better matching
        cleaned_message = re.sub(r'\s+', ' ', message.strip())
        
        for pattern in amount_patterns:
            matches = re.findall(pattern, cleaned_message, re.IGNORECASE)
            if matches:
                try:
                    amount_str = matches[0].replace(',', '').replace(' ', '')
                    # Handle cases like "50,000.00" or "50000"
                    amount_float = float(amount_str)
                    return amount_float
                except (ValueError, AttributeError):
                    continue
        
        # Additional logic for Tanzanian-specific formats
        return self.detect_tanzanian_specific_amount(cleaned_message)
    
    def detect_tanzanian_specific_amount(self, message):
        """Handle Tanzanian-specific amount formats"""
        # Common Tanzanian SMS patterns
        tz_patterns = [
            # MPESA patterns
            r'received[\s\w]*tsh[^\d]*([\d,]+)',  # received tsh 50,000
            r'sent[\s\w]*tsh[^\d]*([\d,]+)',      # sent tsh 50,000
            r'paid[\s\w]*tsh[^\d]*([\d,]+)',      # paid tsh 50,000
            
            # Tigo Pesa patterns
            r'umepokea[\s\w]*tsh[^\d]*([\d,]+)',  # umepokea tsh 50,000
            r'umelipa[\s\w]*tsh[^\d]*([\d,]+)',   # umelipa tsh 50,000
            r'umenunua[\s\w]*tsh[^\d]*([\d,]+)',   # umenunua tsh 50,000
            r'nunua[\s\w]*tsh[^\d]*([\d,]+)',       # nunua tsh 50,000
            r'(?=.*kiasi)(?!.*(?:umetuma|wakala))TSh\s*([\d,]+)',
            
            # Bank patterns with currency
            r'credited[\s\w]*tzs[^\d]*([\d,]+)',  # credited tzs 50,000
            r'debited[\s\w]*tzs[^\d]*([\d,]+)',   # debited tzs 50,000
            
            # Simple number extraction (fallback for well-structured messages)
            r'\b(\d{3,}(?:,\d{3})*(?:\.\d{2})?)\b',  # matches 50000, 50,000, 50,000.00
        ]
        
        for pattern in tz_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            if matches:
                try:
                    amount_str = matches[0].replace(',', '')
                    return float(amount_str)
                except (ValueError, AttributeError):
                    continue
        
        return None

    def detect_sms_type(self, message):
        """Detect SMS type from message content"""
        income_keywords = [
            'umepokea', 'received', 'credited', 'imeingia', 'imepokelewa',
            'pokewa', 'ingia', 'okota', 'mapokezi', 'walituma'
        ]
        
        expense_keywords = [
            'umelipa', 'paid', 'debited', 'withdraw', 'umesafirisha',
            'umetuma', 'toa', 'tuma', 'lipa', 'malipo', 'ulipe','muamala',
            'wakala', 'imelipwa'
            
        ]
        
        transfer_keywords = [
            'umetuma', 'sent', 'transfer', 'hamisha', 'umesafirisha',
            'kupeleka', 'tuma'
        ]
        
        if any(keyword in message for keyword in income_keywords):
            return 'income'
        elif any(keyword in message for keyword in expense_keywords):
            return 'expense'
        elif any(keyword in message for keyword in transfer_keywords):
            return 'transfer'
        else:
            return 'unknown'

    def get_common_senders(self):
        """Get list of common SMS senders for template"""
        return [
            'MPESA', 'Tigo Pesa', 'Airtel Money', 'CRDB Bank', 'NMB Bank',
            'Stanbic Bank', 'Equity Bank', 'KCB Bank', 'DTB Bank'
        ]

    def get_sms_type_guide(self):
        """Get SMS type guide for template"""
        return {
            'income': {'class': 'success', 'description': 'Money received'},
            'expense': {'class': 'danger', 'description': 'Money sent/paid'},
            'transfer': {'class': 'info', 'description': 'Between accounts'},
            'unknown': {'class': 'secondary', 'description': "Can't determine"},
        }

