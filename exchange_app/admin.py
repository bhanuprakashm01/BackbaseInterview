from django.contrib import admin
from .models import Currency, ExchangeRate, Provider

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for managing currencies.
    """
    list_display = ('code',)
    search_fields = ('code',)

@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for managing exchange rates.
    """
    list_display = ('base_currency', 'target_currency', 'rate', 'date')
    list_filter = ('base_currency', 'target_currency', 'date')
    search_fields = ('base_currency__code', 'target_currency__code')
    ordering = ('-date',)

@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for managing exchange rate providers.
    """
    list_display = ('name', 'is_active', 'priority')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('priority',)
    actions = ['activate_providers', 'deactivate_providers']

    def activate_providers(self, request, queryset):
        queryset.update(is_active=True)
    activate_providers.short_description = "Activate selected providers"

    def deactivate_providers(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_providers.short_description = "Deactivate selected providers"
