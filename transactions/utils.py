from datetime import datetime
from django.utils import timezone
from enums import Category, Currency, TransactionStatus

date_formats = ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d', '%d/%m/%Y']

def parse_date(value):
    """
    Parses a date string in ISO format and returns a datetime object.
    Returns None if the input is invalid.
    """
    if value == "" or pd.isna(value):
        return None

    for fmt in date_formats:
        try:
            ts = datetime.strptime(value, fmt)
            return timezone.make_aware(ts)
        except ValueError:
            continue

    return None


def parse_amount(value):
    """
    Parses an amount string and returns a float.
    Returns None if the input is invalid.
    """
    if value == "" or pd.isna(value):
        return None

    try:
        return float(value)
    except ValueError:
        return None

def parse_currency(value):
    """
    Parses a currency string and returns it if valid.
    Returns None if the input is invalid.
    """
    if value == "" or value is None:
        return None

    try: 
        return Currency(value.upper())
    except ValueError:
        return None

def parse_category(value):
    """
    Parses a category string and returns it if valid.
    Returns None if the input is invalid.
    """
    if value == "" or value is None:
        return None

    try:
        return Category(value.upper())
    except ValueError:
        return None

def parse_status(value):
    """
    Parses a status string and returns it if valid.
    Returns None if the input is invalid.
    """
    if value == "" or value is None:
        return None

    try:
        return TransactionStatus(value.upper())
    except ValueError:
        return None

def parse_rows(rows):
    """
    Parses a list of rows (DataFrame rows) and returns a list of dicts with parsed values.
    """
    transactions = []
    bad_rows = []

    for row in rows:
        amount = parse_amount(row.amount)

        if amount is None:
            print(f"Invalid amount for row {row.reference}: {row.amount}")
            bad_rows.append(row.reference)
            continue


        transacted_at = parse_date(row.transacted_at)

        if transacted_at is None:
            print(f"Invalid date format for row {row.reference}: {row.transacted_at}")
            bad_rows.append(row.reference)
            continue

        transactions.append({
            "reference": row.reference,
            "amount": amount,
            "currency": parse_currency(row.currency),
            "category": parse_category(row.category),
            "merchant": row.merchant,
            "status": parse_status(row.status),
            "transacted_at": transacted_at,
        })

    return transactions