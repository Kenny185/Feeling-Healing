from datetime import datetime, timedelta
import pytz


utc = pytz.utc
available_time_slots = []
start_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
for day in range(7):
    for hour in range(9, 17, 2):  # Assuming 9 AM to 5 PM schedule
        time_slot = start_time + timedelta(days=day, hours=hour-start_time.hour)
        available_time_slots.append(time_slot.strftime('%Y-%m-%d %H:%M'))
        # Assume 'time_slot' is a string like "2023-07-21 14:00"
print(available_time_slots)