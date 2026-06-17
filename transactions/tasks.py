import pandas as pd
from datetime import datetime
from celery import shared_task
from django.utils import timezone

from .models import ImportJob, Transaction
from enums import Category, Currency, TransactionStatus

date_formats = ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d', '%d/%m/%Y']

def parse_date(value):
    """
    Parses a date string in ISO format and returns a datetime object.
    Returns None if the input is invalid.
    """
    if value == "" or pd.isna(value):
        #print(f"Invalid date format: '{value}'")
        return None

    for fmt in date_formats:
        try:
            ts = datetime.strptime(value, fmt)
            return timezone.make_aware(ts)
        except ValueError:
            continue

    #print(f"Invalid date format: '{value}'")
    return None


def parse_amount(value):
    """
    Parses an amount string and returns a float.
    Returns None if the input is invalid.
    """
    if value == "" or pd.isna(value):
        #print(f"Invalid amount value: '{value}'")
        return None

    try:
        return float(value)
    except ValueError:
        #print(f"Invalid amount value: '{value}'")
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

    #print(transactions)  # Debugging: print the list of parsed transactions
    print(f"Bad rows: {bad_rows}")  # Debugging: print the list of bad rows
    return transactions

@shared_task
def import_transactions(job_id, file_path):
    """
    Reads the uploaded CSV and imports all transactions into the database.
    Called asynchronously after the file is saved to disk.
    """
    job = ImportJob.objects.get(id=job_id)
    job.status = "running"
    job.save()

    # Load the file in chunks to avoid memory issues with large files
    chunks = pd.read_csv(
        file_path,
        chunksize=1000,
        low_memory=True,
    )

    total_rows = 0
    failed_rows = 0
    imported_rows = 0

    seen_references = set()

    for index, chunk in enumerate(chunks, start=1):
        chunk_rows = len(chunk)
        print(f"Processing chunk {index} with {chunk_rows} rows...")
        total_rows += chunk_rows

        incoming_refs = chunk["reference"].tolist()

        # eliminate duplicated references within the chunk
        deduplicated_refs = []

        for ref in incoming_refs:
            if ref not in seen_references:
                deduplicated_refs.append(ref)
                seen_references.add(ref)

        # Bulk read to fetch database
        existing_refs = set(
            Transaction.objects.filter(reference__in=deduplicated_refs).values_list("reference", flat=True)
        )

        print(f"Found {len(existing_refs)} existing references in chunk {index}.")

        try:
            new_rows = chunk[~chunk['reference'].isin(existing_refs)]
            print(f"Found {len(new_rows)} new references in chunk {index}.")

            new_transactions = [
                Transaction(**row)
                for row in parse_rows(new_rows.itertuples(index=False))
            ]

            failed_rows += chunk_rows - len(existing_refs) - len(new_transactions)

            # Bulk create new transactions
            imported = Transaction.objects.bulk_create(new_transactions)
            chunk_imported_rows = len(imported)
            print(f"Imported {chunk_imported_rows} new transactions in chunk {index}.")
            imported_rows += chunk_imported_rows

        except Exception as e:
            print(f"Error processing chunk {index} rows #{chunk_rows}: {e}")
            job.failed_rows += chunk_rows
            job.error_log += f"Error on chunk {index} (rows {chunk_rows}): {e}\n"
            job.save()

    job.failed_rows = failed_rows
    job.imported_rows = imported_rows
    job.total_rows = total_rows
    job.status = "done"
    job.finished_at = timezone.now()
    job.save()
