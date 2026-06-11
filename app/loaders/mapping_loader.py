import csv
import os

from resources.settings import USER_MAPPING_FILE


def load_user_mapping():
    if not os.path.exists(USER_MAPPING_FILE):
        raise FileNotFoundError(
            f"User mapping file not found: {USER_MAPPING_FILE}"
        )

    mapping = {}
    mapped_users = set()
    required_hours = {}

    with open(USER_MAPPING_FILE, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            standard_user = row.get("StandardUser", "").strip()

            if not standard_user:
                continue

            mapped_users.add(standard_user)

            hours_value = row.get("RequiredHours", "").strip()

            required_hours[standard_user] = (
                float(hours_value) if hours_value else 8
            )

            alias = row.get("Alias", "").strip()

            if alias:
                mapping[alias.lower()] = standard_user

            mapping[standard_user.lower()] = standard_user

    return mapping, mapped_users, required_hours