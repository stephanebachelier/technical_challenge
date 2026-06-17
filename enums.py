from enum import Enum

class Currency(Enum):
  USD = "USD"
  EUR = "EUR"
  GBP = "GBP"

class TransactionStatus(Enum):
  COMPLETED = "completed"
  PENDING = "pending"
  FAILED = "failed"

class Category(Enum):
  FOOD = "food"
  TRANSPORT = "transport"
  UTILITIES = "utilities"
  ENTERTAINMENT = "entertainment"
  HEALTH = "health"
  TRAVEL = "travel"

class JobStatus(Enum):
  RUNNING = "RUNNING"
  COMPLETED = "COMPLETED"
  FAILED = "FAILED"