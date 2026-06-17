from django.db import models
from enums import Category, Currency, JobStatus, TransactionStatus

class Transaction(models.Model):
    reference = models.CharField(max_length=64)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, choices=[(currency.value, currency.name) for currency in Currency])
    category = models.CharField(max_length=64, choices=[(category.value, category.name) for category in Category])
    merchant = models.CharField(max_length=128)
    status = models.CharField(max_length=16, choices=[(status.value, status.name) for status in TransactionStatus])
    transacted_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reference


class ImportJob(models.Model):
    filename = models.CharField(max_length=256)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    total_rows = models.IntegerField(default=0)
    imported_rows = models.IntegerField(default=0)
    failed_rows = models.IntegerField(default=0)
    status = models.CharField(max_length=16, choices=[(status.value, status.name) for status in JobStatus], default=JobStatus.PENDING.value)
    error_log = models.TextField(blank=True)
