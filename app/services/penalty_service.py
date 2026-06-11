
def build_penalty_rows(
    under_hours_rows,
    no_log_rows,
    late_logs,
    penalty_rules,
    penalty_payments
):
    penalty_rows = []

    def append_penalty(date, user, code, rule, extra_note=""):
        penalty_key = build_penalty_key(
            date,
            user,
            code
        )

        payment = penalty_payments.get(
            penalty_key,
            {}
        )

        status = payment.get(
            "status",
            rule["default_status"]
        )

        note = rule["note"]

        if extra_note:
            note = f"{note} - {extra_note}"

        payment_note = payment.get("note", "")
        paid_date = payment.get("paid_date", "")
        handled_by = payment.get("handled_by", "")

        payment_infos = []

        if payment_note:
            payment_infos.append(payment_note)

        if paid_date:
            payment_infos.append(f"Ngày đóng: {paid_date}")

        if handled_by:
            payment_infos.append(f"Người xử lý: {handled_by}")

        if payment_infos:
            note = f"{note} | " + " | ".join(payment_infos)

        penalty_rows.append([
            date,
            user,
            rule["violation"],
            rule["amount"],
            status,
            rule["record_type"],
            rule["currency"],
            note
        ])

    no_log_rule = penalty_rules.get("NO_LOG")
    under_hours_rule = penalty_rules.get("UNDER_HOURS")
    late_rule = penalty_rules.get("LATE")

    if no_log_rule:
        for row in no_log_rows:
            append_penalty(
                date=row[0],
                user=row[1],
                code="NO_LOG",
                rule=no_log_rule
            )

    if under_hours_rule:
        for row in under_hours_rows:
            append_penalty(
                date=row[0],
                user=row[1],
                code="UNDER_HOURS",
                rule=under_hours_rule,
                extra_note=f"Thiếu {row[3]}h"
            )

    if late_rule:
        for item in late_logs:
            append_penalty(
                date=item["date"],
                user=item["user"],
                code="LATE",
                rule=late_rule,
                extra_note=f"Trễ {item['late_minutes']} phút"
            )

    penalty_rows = sorted(
        penalty_rows,
        key=lambda row: (
            row[0],  # Ngày
            row[1],  # Thành viên
            row[2]   # Vi phạm
        )
    )

    return penalty_rows

def build_penalty_key(date, user, code):
    return (
        f"{date.replace('-', '')}"
        f"|{user}"
        f"|{code}"
    )