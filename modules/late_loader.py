import csv
import os

from resources.settings import LATE_LOG_FILE


def load_late_logs():
    late_logs = []

    if not os.path.exists(LATE_LOG_FILE):
        return late_logs

    with open(LATE_LOG_FILE, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            date = row.get("Date", "").strip()
            user = row.get("User", "").strip()
            late_minutes = row.get("LateMinutes", "").strip()
            description = row.get("Description", "").strip()

            if not date or not user:
                continue

            try:
                late_minutes_value = int(late_minutes) if late_minutes else 0
            except ValueError:
                late_minutes_value = 0

            late_logs.append({
                "date": date,
                "user": user,
                "late_minutes": late_minutes_value,
                "description": description
            })

    return late_logs