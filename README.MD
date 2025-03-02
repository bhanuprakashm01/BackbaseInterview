# MyCurrency Django Project

## Overview

MyCurrency is a Django-based web application that allows users to calculate currency exchange rates. It supports multiple exchange rate providers, including CurrencyBeacon and a mock provider for testing purposes. The platform is designed to dynamically select the best provider based on priority.

## Features

- Retrieve historical exchange rates
- Convert currency amounts using real-time exchange rates
- Manage exchange rate providers dynamically
- Asynchronous task execution using Celery
- Scheduled tasks using Celery Beat

## Prerequisites

Ensure you have the following installed:

- Python 3.8+
- SQLite (for development)
- Redis (for Celery task queue)
- RabbitMQ (optional, alternative Celery broker)

## Installation

### 1. Create and Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root and set the following values:

```ini
CURRENCYBEACON_API_KEY=your_api_key
```

### 4. Apply Migrations

```bash
python manage.py migrate
```

### 5. Create a Superuser

```bash
python manage.py createsuperuser
```

### 6. Start the Development Server

```bash
python manage.py runserver
```

## Running Celery

### 1. Start Redis Server

```bash
redis-server
```

### 2. Start Celery Worker

```bash
celery -A CurrencyExchange worker --loglevel=info
```

### 3. Start Celery Beat (For Scheduled Tasks)

```bash
celery -A CurrencyExchange beat --loglevel=info
```

### 4.Inserting Dummy Data
```
python manage.py populate_dummy_data
```

## Running Tests

```bash
python manage.py test
```

