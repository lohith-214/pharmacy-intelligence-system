from datetime import datetime, timedelta
import random

start = datetime(2023, 1, 1)
end   = datetime(2024, 12, 31)
total_days = (end - start).days     # 730 days

# Generate a random date in that range
random_date = start + timedelta(days=random.randint(0, total_days))
print("Random date:", random_date.strftime("%Y-%m-%d"))
print("Month:", random_date.month)
print("Day of week:", random_date.strftime("%A"))