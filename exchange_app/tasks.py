import asyncio
from datetime import datetime, timedelta
from celery import shared_task, group
from django.db import transaction
from .models import Currency, ExchangeRate
from .utility import get_exchange_rate_data

BATCH_SIZE = 100  # Number of records inserted in bulk


async def fetch_exchange_rates_async(date_str):
    """
    Asynchronous function to fetch exchange rates for all currency pairs.
    Uses `asyncio.to_thread()` to run `get_exchange_rate_data` concurrently.
    """
    currencies = await asyncio.to_thread(list, Currency.objects.all())  # Safe Django ORM call
    tasks = []

    for base_currency in currencies:
        for target_currency in currencies:
            if base_currency == target_currency:
                continue

            # Schedule currency rate fetching as an async task
            tasks.append(asyncio.to_thread(
                get_exchange_rate_data,
                base_currency.code, target_currency.code, date_str
            ))

    # Run all tasks concurrently
    results = await asyncio.gather(*tasks)

    return currencies, results


@shared_task
def fetch_and_store_exchange_rates(date_str):
    """
    Celery task to fetch and store exchange rates for a given date asynchronously.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    currencies, results = loop.run_until_complete(fetch_exchange_rates_async(date_str))

    exchange_rate_entries = []
    index = 0

    for base_currency in currencies:
        for target_currency in currencies:
            if base_currency == target_currency:
                continue

            rate = results[index]
            index += 1

            if rate is not None:
                exchange_rate_entries.append(
                    ExchangeRate(
                        base_currency=base_currency,
                        target_currency=target_currency,
                        date=date_str,
                        rate=rate
                    )
                )

            # Insert in batches
            if len(exchange_rate_entries) >= BATCH_SIZE:
                bulk_insert_exchange_rates(exchange_rate_entries)
                exchange_rate_entries = []

    # Final bulk insert
    if exchange_rate_entries:
        bulk_insert_exchange_rates(exchange_rate_entries)

    return f"Exchange rates for {date_str} stored successfully."


def bulk_insert_exchange_rates(entries):
    """
    Helper function to perform bulk insert inside a database transaction.
    """
    with transaction.atomic():
        ExchangeRate.objects.bulk_create(entries, ignore_conflicts=True)


@shared_task
def load_historical_exchange_rates(start_date, end_date):
    """
    Celery task to schedule multiple parallel tasks for fetching historical exchange rates.
    """
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")

    # Create a task for each date
    tasks = [fetch_and_store_exchange_rates.s((start_date_obj + timedelta(days=n)).strftime("%Y-%m-%d"))
             for n in range((end_date_obj - start_date_obj).days + 1)]

    # Run tasks in parallel using Celery's group feature
    job = group(tasks)
    result = job.apply_async()

    return f"Historical exchange rates loading started for {start_date} to {end_date}. Task ID: {result.id}"


@shared_task
def scheduled_historical_exchange_rates():
    """
    Scheduled Celery task to fetch and store historical exchange rates daily.
    """
    yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.today().strftime("%Y-%m-%d")

    load_historical_exchange_rates.delay(yesterday, today)

    return "Daily exchange rate update scheduled."
