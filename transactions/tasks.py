import pandas as pd
from datetime import datetime
from celery import shared_task
from django.utils import timezone

from .models import ImportJob, Transaction


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

    for index, row in enumerate(chunks, start=1):
        total_rows += len(row)
        try:
            # Check duplicate row by row
            exists = Transaction.objects.filter(reference=row["reference"]).exists()
            if exists:
                job.failed_rows += 1
                job.error_log += f"Duplicate: {row['reference']}\n"
                job.save()
                continue

            t = Transaction(
                reference=row["reference"],
                amount=row["amount"],
                currency=row["currency"],
                category=row["category"],
                merchant=row["merchant"],
                status=row["status"],
                transacted_at=datetime.fromisoformat(str(row["transacted_at"])),
            )
            t.save()

            job.imported_rows += 1
            job.save()

        except Exception as e:
            job.failed_rows += 1
            job.error_log += f"Error on row {index} ({row.get('reference', '?')}): {e}\n"
            job.save()

    job.total_rows = total_rows
    job.status = "done"
    job.finished_at = timezone.now()
    job.save()
