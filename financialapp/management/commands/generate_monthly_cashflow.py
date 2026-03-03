# core/management/commands/generate_monthly_cashflow.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from financialapp.models import CashFlow

class Command(BaseCommand):
    help = 'Generate monthly cash flow for all users'
    
    def handle(self, *args, **options):
        users = User.objects.all()
        for user in users:
            CashFlow.generate_all_months_cash_flow(user)
            self.stdout.write(
                self.style.SUCCESS(f'Generated cash flow for {user.username}')
            )