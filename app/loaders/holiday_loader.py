import csv
import os

from resources.settings import HOLIDAY_FILE


def load_holidays():
    holidays = set()

    if not os.path.exists(HOLIDAY_FILE):
        return holidays

    with open(HOLIDAY_FILE, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            date = row.get("Date", "").strip()

            if date:
                holidays.add(date)

    return holidays