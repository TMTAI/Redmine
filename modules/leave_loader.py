import csv
import os

from resources.settings import USER_LEAVE_FILE


def load_user_leaves():
    user_leaves = {}

    if not os.path.exists(USER_LEAVE_FILE):
        return user_leaves

    with open(USER_LEAVE_FILE, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            date = row.get("Date", "").strip()
            user = row.get("User", "").strip()
            leave_hours = row.get("LeaveHours", "").strip()

            if not date or not user:
                continue

            try:
                leave_hours_value = float(
                    leave_hours.replace(",", ".")
                ) if leave_hours else 8
            except ValueError:
                leave_hours_value = 8

            user_leaves[(date, user)] = leave_hours_value

    return user_leaves