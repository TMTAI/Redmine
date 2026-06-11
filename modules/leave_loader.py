import csv
import os

from resources.settings import USER_LEAVE_FILE


def load_user_leaves():
    user_leaves = set()

    if not os.path.exists(USER_LEAVE_FILE):
        return user_leaves

    with open(USER_LEAVE_FILE, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            date = row.get("Date", "").strip()
            user = row.get("User", "").strip()

            if date and user:
                user_leaves.add((date, user))

    return user_leaves