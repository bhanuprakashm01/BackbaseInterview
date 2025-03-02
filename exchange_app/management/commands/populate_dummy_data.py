from django.core.management.base import BaseCommand
from django.utils.timezone import now
from datetime import timedelta
import random
from exchange_app.models import Provider, Currency, ExchangeRate

class Command(BaseCommand):
    help = "Populate database with dummy exchange rate data for past and future dates"

    def handle(self, *args, **kwargs):
        # Updated currency list to include INR (Indian Rupee) and CNY (Chinese Yuan)
        currencies = ['EUR', 'USD', 'GBP', 'CHF', 'INR', 'CNY']
        days_range = 30  # Generate data for the past 30 days and next 30 days

        # Create providers if they don't exist
        Provider.objects.get_or_create(name='CurrencyBeacon', defaults={'is_active': True, 'priority': 1})
        Provider.objects.get_or_create(name='Mock', defaults={'is_active': True, 'priority': 2})

        # Create currencies if they don't exist
        for code in currencies:
            Currency.objects.get_or_create(code=code)

        # Generate exchange rates for past and future dates
        today = now().date()
        date_range = [today + timedelta(days=i) for i in range(-days_range, days_range + 1)]

        for exchange_date in date_range:
            for base in currencies:
                for target in currencies:
                    if base != target:
                        ExchangeRate.objects.update_or_create(
                            base_currency=Currency.objects.get(code=base),
                            target_currency=Currency.objects.get(code=target),
                            date=exchange_date,
                            defaults={'rate': round(random.uniform(0.5, 1.5), 4)}
                        )

        self.stdout.write(self.style.SUCCESS('Dummy data successfully created!!'))