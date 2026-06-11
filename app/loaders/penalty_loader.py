import csv
import os

from resources.settings import PENALTY_RULE_FILE


def load_penalty_rules():
    rules = {}

    if not os.path.exists(PENALTY_RULE_FILE):
        return rules

    with open(PENALTY_RULE_FILE, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            enabled = row.get("Enabled", "Y").strip().upper()

            if enabled != "Y":
                continue

            code = row.get("Code", "").strip()

            if not code:
                continue

            amount_value = row.get("Amount", "0").strip()

            try:
                amount = float(amount_value.replace(",", ""))
            except ValueError:
                amount = 0

            rules[code] = {
                "code": code,
                "source": row.get("Source", "").strip(),
                "violation": row.get("Violation", "").strip(),
                "amount": amount,
                "default_status": row.get("DefaultStatus", "Chưa đóng").strip(),
                "record_type": row.get("RecordType", "Lần đầu").strip(),
                "currency": row.get("Currency", "VND").strip(),
                "note": row.get("Note", "").strip()
            }

    return rules