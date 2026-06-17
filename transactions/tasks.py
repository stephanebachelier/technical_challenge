import pandas as pd
from celery import shared_task

from .models import ImportJob, Transaction
from .utils import parse_rows

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
