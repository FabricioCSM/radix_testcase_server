from datetime import datetime, timedelta
import random

sample_data = []

for equipment_id in range(1, 2001):
    for year in range(2022, 2025):
        for month in range(1, 13):
            if month == 2:
                days_in_month = 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28
            elif month in [4, 6, 9, 11]:
                days_in_month = 30
            else:
                days_in_month = 31
            
            for day in range(1, days_in_month + 1):
                timestamp = datetime(year, month, day, random.randint(0, 23), random.randint(0, 59))
                sample_data.append({
                    "equipment_id": f"EQ-{str(equipment_id).zfill(5)}",
                    "timestamp": timestamp.isoformat(),
                    "value": round(random.uniform(3.5, 20.0), 2),
                    "created_at": datetime.now().isoformat()
                })