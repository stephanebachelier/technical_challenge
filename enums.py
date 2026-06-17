from enum import Enum

class Currency(Enum):
  USD = "USD", "US Dollar"
  EUR = "EUR", "Euro"
  GBP = "GBP", "British Pound"

class TransactionStatus(Enum):
  COMPLETED = "completed", "Completed"
  PENDING = "pending", "Pending"
  FAILED = "failed", "Failed"

class Category(Enum):
  FOOD = "food", "Food"
  TRANSPORT = "transport", "Transport"
  UTILITIES = "utilities", "Utilities"
  ENTERTAINMENT = "entertainment", "Entertainment"
  HEALTH = "health", "Health"
  TRAVEL = "travel", "Travel"

class JobStatus(Enum):
  RUNNING = "running", "Running"
  COMPLETED = "completed", "Completed"
  FAILED = "failed", "Failed"