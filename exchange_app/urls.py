from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

# Using DefaultRouter for ViewSets (Currency & Provider)
router = DefaultRouter()
router.register(r'currencies', CurrencyViewSet, basename='currency')
router.register(r'providers', ProviderViewSet, basename='provider')

urlpatterns = [
    # API to get exchange rates for a given time range
    path('currency-rates/list', CurrencyRateListView.as_view(), name='currency-rates-list'),
    path('exchange-rates/pagination', PaginatedExchangeRateListView.as_view(), name='paginated_exchange_rate_list'),

    # API to convert currency based on latest exchange rate
    path('convert/', ConvertAmountView.as_view(), name='convert-currency'),
    path('currency/load-historical-rates/', LoadHistoricalRatesView.as_view(), name='load-historical-rates'),
    
    # Including ViewSets (Currency & Provider)
    path('', include(router.urls)),
]
