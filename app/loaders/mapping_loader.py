import csv
import os

from resources.settings import USER_MAPPING_FILE


def load_user_mapping(invalid_data=None):
    if not os.path.exists(USER_MAPPING_FILE):
        raise FileNotFoundError(
            f"User mapping file not found: {USER_MAPPING_FILE}"
        )

    mapping = {}
    mapped_users = set()
    required_hours = {}
    user_teams = {}
    user_roles = {}

    with open(USER_MAPPING_FILE, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            standard_user = row.get("StandardUser", "").strip()

            if not standard_user:
                if invalid_data:
                    invalid_data.add(
                        source="USER_MAPPING",
                        file_name=USER_MAPPING_FILE,
                        row_number=index,
                        reason="StandardUser is empty",
                        raw_data=row
                    )
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

            team = row.get("Team", "").strip()
            role = row.get("Role", "").strip()

            user_teams[standard_user] = team
            user_roles[standard_user] = role

    return mapping, mapped_users, required_hours, user_teams, user_roles