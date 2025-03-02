from rest_framework import serializers
from .models import ExchangeRate, Currency, Provider

class ProviderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Provider model.
    """
    class Meta:
        model = Provider
        fields = '__all__'

class CurrencySerializer(serializers.ModelSerializer):
    """
    Serializer for the Currency model.
    """
    class Meta:
        model = Currency
        fields = '__all__'

class ExchangeRateSerializer(serializers.ModelSerializer):
    """
    Serializer for the ExchangeRate model.
    """
    base_currency = serializers.SlugRelatedField(slug_field='code', queryset=Currency.objects.all())
    target_currency = serializers.SlugRelatedField(slug_field='code', queryset=Currency.objects.all())

    class Meta:
        model = ExchangeRate
        fields = '__all__'
