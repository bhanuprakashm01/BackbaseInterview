from django.test import TestCase
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date

class CurrencyRateListViewTests(TestCase):
    """
    Unit tests for the CurrencyRateListView API endpoint.
    """
    def setUp(self):
        """Initialize API client before each test."""
        self.client = APIClient()

    @patch('exchange_app.models.Currency.objects.get')
    @patch('exchange_app.models.ExchangeRate.objects.filter')
    def test_get_currency_rates_success(self, mock_filter, mock_get):
        """
        Test retrieving exchange rates successfully when valid parameters are provided.
        """
        mock_get.return_value = MagicMock()
        mock_filter.return_value = []
        
        response = self.client.get(reverse('currency-rates-list'), {
            'source_currency': 'EUR',
            'date_from': '2024-01-01',
            'date_to': '2024-02-01'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_get_currency_rates_missing_params(self):
        """
        Test that the API returns a 400 error when required parameters are missing.
        """
        response = self.client.get(reverse('currency-rates-list'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class PaginatedExchangeRateListViewTests(TestCase):
    """
    Unit tests for the PaginatedExchangeRateListView API endpoint.
    """
    def setUp(self):
        """Initialize API client before each test."""
        self.client = APIClient()

    @patch('exchange_app.models.Currency.objects.get')
    @patch('exchange_app.models.ExchangeRate.objects.filter')
    def test_get_paginated_rates_success(self, mock_filter, mock_get):
        """
        Test retrieving paginated exchange rates successfully when valid parameters are provided.
        """
        mock_get.return_value = MagicMock()
        mock_filter.return_value = []
        
        response = self.client.get(reverse('paginated_exchange_rate_list'), {
            'source_currency': 'EUR',
            'date_from': '2024-01-01',
            'date_to': '2024-02-01'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_get_paginated_rates_missing_params(self):
        """
        Test that the API returns a 400 error when required parameters are missing.
        """
        response = self.client.get(reverse('paginated_exchange_rate_list'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class ConvertAmountViewTests(TestCase):
    """
    Unit tests for the ConvertAmountView API endpoint.
    """
    def setUp(self):
        """Initialize API client before each test."""
        self.client = APIClient()

    @patch('exchange_app.models.Currency.objects.get')
    @patch('exchange_app.models.Provider.objects.filter')
    @patch('exchange_app.views.get_exchange_rate_data')
    def test_convert_amount_success(self, mock_get_rate, mock_providers, mock_get_currency):
        """
        Test successful currency conversion when valid parameters and providers are available.
        """
        mock_get_currency.return_value = MagicMock()
        mock_providers.return_value.order_by.return_value = [MagicMock(name='Provider1')]
        mock_get_rate.return_value = 1.1
        
        response = self.client.get(reverse('convert-currency'), {
            'source_currency': 'EUR',
            'exchanged_currency': 'USD',
            'amount': 100
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_convert_amount_invalid_currency(self):
        """
        Test that the API returns a 400 error when an invalid currency code is provided.
        """
        response = self.client.get(reverse('convert-currency'), {
            'source_currency': 'XYZ',
            'exchanged_currency': 'USD',
            'amount': 100
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class LoadHistoricalRatesViewTests(TestCase):
    """
    Unit tests for the LoadHistoricalRatesView API endpoint.
    """
    def setUp(self):
        """Initialize API client before each test."""
        self.client = APIClient()

    @patch('exchange_app.views.load_historical_exchange_rates.delay')
    def test_load_historical_rates_success(self, mock_task):
        """
        Test that the API successfully triggers a background task to load historical exchange rates.
        """
        mock_task.return_value.id = '1234'
        
        response = self.client.post(reverse('load-historical-rates'), {
            'start_date': '2024-01-01',
            'end_date': '2024-02-01'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_load_historical_rates_missing_params(self):
        """
        Test that the API returns a 400 error when required parameters are missing.
        """
        response = self.client.post(reverse('load-historical-rates'), {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class CurrencyViewSetTests(TestCase):
    """
    Unit tests for the CurrencyViewSet API endpoint.
    """
    def setUp(self):
        self.client = APIClient()

    @patch('exchange_app.models.Currency.objects.all')
    def test_list_currencies(self, mock_all):
        mock_all.return_value = []
        response = self.client.get(reverse('currency-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class ProviderViewSetTests(TestCase):
    """
    Unit tests for the ProviderViewSet API endpoint.
    """
    def setUp(self):
        self.client = APIClient()

    @patch('exchange_app.models.Provider.objects.all')
    def test_list_providers(self, mock_all):
        mock_all.return_value = []
        response = self.client.get(reverse('provider-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
