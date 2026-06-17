from django.db import models

class Currency(models.TextChoices):
  USD = "USD", "US Dollar"
  EUR = "EUR", "Euro"
  GBP = "GBP", "British Pound"

class TransactionStatus(models.TextChoices):
  COMPLETED = "completed", "Completed"
  PENDING = "pending", "Pending"
  FAILED = "failed", "Failed"

class Category(models.TextChoices):
  FOOD = "food", "Food"
  TRANSPORT = "transport", "Transport"
  UTILITIES = "utilities", "Utilities"
  ENTERTAINMENT = "entertainment", "Entertainment"
  HEALTH = "health", "Health"
  TRAVEL = "travel", "Travel"

class JobStatus(models.TextChoices):
  PENDING = "pending", "Pending"
  RUNNING = "running", "Running"
  COMPLETED = "completed", "Completed"
  FAILED = "failed", "Failed"