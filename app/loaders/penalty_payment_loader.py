import csv
import os

from resources.settings import PENALTY_PAYMENT_FILE


def build_penalty_key(date, user, code):
    return (
        f"{date.replace('-', '').strip()}"
        f"|{user.strip()}"
        f"|{code.strip().upper()}"
    )


def load_penalty_payments():
    payments = {}

    if not os.path.exists(PENALTY_PAYMENT_FILE):
        return payments

    with open(PENALTY_PAYMENT_FILE, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            date = row.get("Date", "").strip()
            user = row.get("User", "").strip()
            code = row.get("Code", "").strip().upper()

            if not date or not user or not code:
                continue

            penalty_key = build_penalty_key(
                date=date,
                user=user,
                code=code
            )

            paid_amount_value = row.get("PaidAmount", "0").strip()

            try:
                paid_amount = float(
                    paid_amount_value.replace(",", "")
                )
            except ValueError:
                paid_amount = 0

            payments[penalty_key] = {
                "date": date,
                "user": user,
                "code": code,
                "status": row.get("Status", "").strip(),
                "paid_amount": paid_amount,
                "paid_date": row.get("PaidDate", "").strip(),
                "handled_by": row.get("HandledBy", "").strip(),
                "note": row.get("Note", "").strip()
            }

    return payments