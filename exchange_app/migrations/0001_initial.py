# Generated by Django 5.1.6 on 2025-03-02 05:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(help_text='Currency code (e.g., USD, EUR)', max_length=3, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the provider', max_length=100, unique=True)),
                ('is_active', models.BooleanField(default=True, help_text='Indicates if the provider is active')),
                ('priority', models.IntegerField(default=1, help_text='Priority of the provider (lower is higher priority)')),
            ],
        ),
        migrations.CreateModel(
            name='ExchangeRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate', models.DecimalField(decimal_places=6, help_text='Exchange rate value', max_digits=10)),
                ('date', models.DateField(help_text='Date of the exchange rate')),
                ('base_currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='base_rates', to='exchange_app.currency')),
                ('target_currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='target_rates', to='exchange_app.currency')),
            ],
        ),
    ]
