from django.db import models

class Provider(models.Model):
    """
    Model representing a currency exchange rate provider.
    """
    name = models.CharField(max_length=100, unique=True, help_text="Name of the provider")
    is_active = models.BooleanField(default=True, help_text="Indicates if the provider is active")
    priority = models.IntegerField(default=1, help_text="Priority of the provider (lower is higher priority)")

    def __str__(self):
        return f"{self.name} (Priority: {self.priority})"

class Currency(models.Model):
    """
    Model representing a currency.
    """
    code = models.CharField(max_length=3, unique=True, help_text="Currency code (e.g., USD, EUR)")

    def __str__(self):
        return self.code

class ExchangeRate(models.Model):
    """
    Model representing an exchange rate between two currencies on a given date.
    """
    base_currency = models.ForeignKey(Currency, related_name="base_rates", on_delete=models.CASCADE)
    target_currency = models.ForeignKey(Currency, related_name="target_rates", on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=10, decimal_places=6, help_text="Exchange rate value")
    date = models.DateField(help_text="Date of the exchange rate")

    def __str__(self):
        return f"{self.base_currency.code} to {self.target_currency.code} on {self.date}: {self.rate}"
