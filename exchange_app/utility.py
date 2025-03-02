from abc import ABC, abstractmethod
import random
import requests
from django.conf import settings
from datetime import date
from .models import Provider

class ExchangeRateProvider(ABC):
    """
    Abstract base class for currency exchange rate providers.
    All providers must implement the `get_exchange_rate` method.
    """
    
    @abstractmethod
    def get_exchange_rate(self, source_currency, exchanged_currency, valuation_date):
        """
        Fetches the exchange rate for a given currency pair on a specific date.
        
        :param source_currency: The base currency (e.g., "EUR")
        :param exchanged_currency: The target currency (e.g., "USD")
        :param valuation_date: The date for which the exchange rate is requested
        :return: Exchange rate as a float or None if unavailable
        """
        pass

class CurrencyBeaconProvider(ExchangeRateProvider):
    """
    Exchange rate provider that integrates with the CurrencyBeacon API.
    """
    
    def get_exchange_rate(self, source_currency, exchanged_currency, valuation_date):
        """
        Retrieves the exchange rate from CurrencyBeacon API for a given currency pair.
        
        :param source_currency: The base currency (e.g., "EUR")
        :param exchanged_currency: The target currency (e.g., "USD")
        :param valuation_date: The date for which the exchange rate is requested
        :return: Exchange rate as a float or None if unavailable
        """
        api_key = settings.CURRENCYBEACON_API_KEY  # API key stored in Django settings
        url = f"https://api.currencybeacon.com/v1/historical?api_key={api_key}&base={source_currency}&date={valuation_date}"
        response = requests.get(url)
        data = response.json()
        
        return data.get('rates', {}).get(exchanged_currency, None)

class MockProvider(ExchangeRateProvider):
    """
    Mock exchange rate provider that generates random exchange rates.
    Useful for testing purposes.
    """
    
    def get_exchange_rate(self, source_currency, exchanged_currency, valuation_date):
        """
        Generates a random exchange rate for testing.
        
        :param source_currency: The base currency (e.g., "EUR")
        :param exchanged_currency: The target currency (e.g., "USD")
        :param valuation_date: The date for which the exchange rate is requested
        :return: Randomly generated exchange rate as a float
        """
        # Generate a random mock exchange rate
        return round(random.uniform(0.5, 1.5), 4)  


def get_exchange_rate_data(source_currency, exchanged_currency, valuation_date):
    """
    Retrieves the exchange rate from the highest-priority active provider.
    If no provider returns a valid exchange rate, it returns None.
    
    :param source_currency: The base currency (e.g., "EUR")
    :param exchanged_currency: The target currency (e.g., "USD")
    :param valuation_date: The date for which the exchange rate is requested
    :return: Exchange rate as a float or None if no provider returns a valid rate
    """
    
    # Fetch all active providers sorted by priority (ascending order)
    providers = Provider.objects.filter(is_active=True).order_by('priority')
    
    for provider in providers:
        # Dynamically select the provider class based on provider name
        provider_class = CurrencyBeaconProvider if provider.name.lower() == 'currencybeacon' else MockProvider
        provider_instance = provider_class()
        
        # Attempt to get exchange rate from provider
        rate = provider_instance.get_exchange_rate(source_currency, exchanged_currency, valuation_date)
        
        if rate is not None:
            return rate  # Return the first valid rate found
    # Return None if no provider returns a valid exchange rate
    return None  
