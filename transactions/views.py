import os
import tempfile

from django.http import JsonResponse
from django.db.models import Sum
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import datetime
from .models import ImportJob, Transaction
from .tasks import import_transactions

UPLOAD_DIR = "/tmp/imports"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@method_decorator(csrf_exempt, name="dispatch")
class ImportView(View):
    """
    Accepts a CSV upload, saves the file, and queues an async import task.
    """

    def post(self, request):
        file = request.FILES.get("file")
        if not file:
            return JsonResponse({"error": "No file provided."}, status=400)

        # Save uploaded file to a temp location so the worker can read it
        suffix = os.path.splitext(file.name)[1]
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=UPLOAD_DIR)
        for chunk in file.chunks():
            tmp.write(chunk)
        tmp.close()

        job = ImportJob.objects.create(filename=file.name, status="pending")

        # Queue the task
        result = import_transactions.delay(job.id, tmp.name)

        # Wait for it to finish before responding — so the client doesn't time out
        result.get(timeout=300)

        job.refresh_from_db()

        return JsonResponse(
            {
                "job_id": job.id,
                "imported": job.imported_rows,
                "failed": job.failed_rows,
            }
        )


class SummaryView(View):
    """
    Returns total amount per category, with optional date range filter.
    """

    def get(self, request):
        date_from = request.GET.get("from")
        date_to = request.GET.get("to")

        transactions = Transaction.objects.values("category").annotate(total=Sum("amount")).all()

        try:
            if date_from:
                date_from = datetime.fromisoformat(date_from)
                transactions = transactions.filter(transacted_at__gte=date_from)
        except ValueError:
            print("Invalid date format for 'from':", date_from)
            return JsonResponse({"error": "Invalid date format for 'from'. Use ISO format."}, status=400)

        try:
            if date_to:
                date_to = datetime.fromisoformat(date_to)
                transactions = transactions.filter(transacted_at__lte=date_to)
        except ValueError:
            print("Invalid date format for 'to':", date_to)
            return JsonResponse({"error": "Invalid date format for 'to'. Use ISO format."}, status=400)

        result = [{"category": t["category"], "total": round(t["total"], 2)} for t in transactions.order_by('-total')]
        print("Aggregated result from database:", result)

        return JsonResponse({"results": result })


class JobStatusView(View):
    """
    Returns the current status of an import job.
    """

    def get(self, request, job_id):
        try:
            job = ImportJob.objects.get(id=job_id)
        except ImportJob.DoesNotExist:
            return JsonResponse({"error": "Job not found."}, status=404)

        return JsonResponse(
            {
                "id": job.id,
                "status": job.status,
                "filename": job.filename,
                "total_rows": job.total_rows,
                "imported_rows": job.imported_rows,
                "failed_rows": job.failed_rows,
                "started_at": job.started_at.isoformat(),
                "finished_at": job.finished_at.isoformat() if job.finished_at else None,
            }
        )
