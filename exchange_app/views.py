from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from datetime import date
from .models import ExchangeRate, Currency, Provider
from .serializers import ExchangeRateSerializer, CurrencySerializer, ProviderSerializer
from .tasks import *
from .utility import get_exchange_rate_data
import random

class CurrencyRateListView(APIView):
    """
    API to retrieve exchange rates for a given source currency within a time range.
    """
    def get(self, request):
        try:
            source_currency_code = request.GET.get('source_currency', 'EUR')
            date_from = request.GET.get('date_from')
            date_to = request.GET.get('date_to')

            if not date_from or not date_to:
                return Response({'error': 'date_from and date_to are required'}, status=status.HTTP_400_BAD_REQUEST)

            # Parse date strings to date objects
            date_from = parse_date(date_from)
            date_to = parse_date(date_to)

            if not date_from or not date_to:
                return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                source_currency = Currency.objects.get(code=source_currency_code)
            except Currency.DoesNotExist:
                return Response({'error': 'Invalid source currency'}, status=status.HTTP_400_BAD_REQUEST)

            # Debugging statements
            print(f"Source Currency: {source_currency.code}, Date From: {date_from}, Date To: {date_to}")

            # Fetch exchange rates within the date range
            rates = ExchangeRate.objects.filter(
                base_currency=source_currency, 
                date__range=[date_from, date_to]
            )

            # print(f"Found {rates.count()} rates")

            if not rates.exists():
                return Response({'message': 'No exchange rates found for the given criteria'}, status=status.HTTP_404_NOT_FOUND)

            serializer = ExchangeRateSerializer(rates, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Currency.DoesNotExist:
            return Response({'error': 'Invalid source currency'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PaginatedExchangeRateListView(APIView):
    """
    API view to fetch exchange rates with pagination support.
    """
    def get(self, request):
        try:
            source_currency_code = request.GET.get('source_currency', 'EUR')
            date_from = request.GET.get('date_from')
            date_to = request.GET.get('date_to')

            if not date_from or not date_to:
                return Response({'error': 'Both date_from and date_to are required'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                source_currency = Currency.objects.get(code=source_currency_code)
            except Currency.DoesNotExist:
                return Response({'error': 'Invalid source currency'}, status=status.HTTP_400_BAD_REQUEST)

            rates = ExchangeRate.objects.filter(
                base_currency=source_currency,
                date__range=[date_from, date_to]
            )

            paginator = PageNumberPagination()
            paginator.page_size = request.GET.get('page_size', 10)  # Default page size is 10
            result_page = paginator.paginate_queryset(rates, request)
            serializer = ExchangeRateSerializer(result_page, many=True)

            return paginator.get_paginated_response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConvertAmountView(APIView):
    """
    API to convert an amount from one currency to another using the latest exchange rate.
    """
    def get(self, request):
        try:
            source_currency_code = request.GET.get('source_currency', 'EUR')
            exchanged_currency_code = request.GET.get('exchanged_currency', 'USD')
            amount = float(request.GET.get('amount', 1))

            try:
                source_currency = Currency.objects.get(code=source_currency_code)
                exchanged_currency = Currency.objects.get(code=exchanged_currency_code)
            except Currency.DoesNotExist:
                return Response({'error': 'Invalid currency code'}, status=status.HTTP_400_BAD_REQUEST)

            providers = Provider.objects.filter(is_active=True).order_by('priority')
            rate = None
            
            for provider in providers:
                try:
                    rate = get_exchange_rate_data(source_currency.code, exchanged_currency.code, str(date.today()), provider.name)
                    if rate:
                        break
                except Exception:
                    continue  # Try next provider if one fails
            
            if rate:
                converted_amount = amount * rate
                return Response({
                    'source_currency': source_currency_code,
                    'exchanged_currency': exchanged_currency_code,
                    'amount': amount,
                    'rate': rate,
                    'converted_amount': converted_amount
                })
            return Response({'error': 'No exchange rate available'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CurrencyViewSet(viewsets.ModelViewSet):
    """
    CRUD API for managing available currencies.
    """
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

class ProviderViewSet(viewsets.ModelViewSet):
    """
    API for managing providers (activation, deactivation, priority update).
    """
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer

    def update(self, request, pk=None):
        """
        Allows updating provider details such as priority and active status.
        """
        try:
            provider = get_object_or_404(Provider, pk=pk)
            serializer = ProviderSerializer(provider, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoadHistoricalRatesView(APIView):
    """
    API view to trigger a background task for loading historical exchange rates.
    
    Methods:
        - POST: Initiates a background task to fetch historical exchange rates.
    
    Request Body:
        - source_currency (str): The base currency.
        - target_currency (str): The currency to convert to.
        - start_date (str): The start date for historical data (format: 'YYYY-MM-DD').
        - end_date (str): The end date for historical data (format: 'YYYY-MM-DD').
    """
    def post(self, request):
        try:
            # source_currency = request.data.get('source_currency')
            # target_currency = request.data.get('target_currency')
            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date')

            # Validate required input fields
            if not all([start_date, end_date]):
                return Response({'error': 'Missing required parameters'}, status=status.HTTP_400_BAD_REQUEST)

            # Trigger Celery task to load historical exchange rates
            task = load_historical_exchange_rates.delay(start_date, end_date)

            return Response({'message': 'Historical exchange rate loading started', 'task_id': task.id}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
