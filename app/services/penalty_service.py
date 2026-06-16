def normalize_status(status):
    return str(status or "").strip().upper()


def is_paid_status(status):
    return normalize_status(status) in [
        "ĐÃ ĐÓNG",
        "DA DONG"
    ]


def is_closed_status(status):
    return normalize_status(status) in [
        "ĐÃ ĐÓNG",
        "DA DONG",
        "MIỄN PHẠT",
        "MIEN PHAT"
    ]


def build_penalty_key(date, user, code):
    return (
        f"{date.replace('-', '')}"
        f"|{user.strip()}"
        f"|{code.strip().upper()}"
    )


def get_payment_note(payment):
    note = payment.get("note", "")
    paid_date = payment.get("paid_date", "")
    handled_by = payment.get("handled_by", "")

    payment_infos = []

    if note:
        payment_infos.append(note)

    if paid_date:
        payment_infos.append(
            f"Ngày đóng: {paid_date}"
        )

    if handled_by:
        payment_infos.append(
            f"Người xử lý: {handled_by}"
        )

    return " | ".join(payment_infos)


def build_violation_penalty_row(
    date,
    user,
    code,
    rule,
    penalty_payments,
    extra_note=""
):
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

    paid_flag = (
        "x"
        if is_paid_status(status)
        else ""
    )

    note = rule.get(
        "note",
        ""
    )

    if extra_note:
        note = f"{note} - {extra_note}"

    payment_note = get_payment_note(
        payment
    )

    if payment_note:
        note = f"{note} | {payment_note}"

    return {
        "key": penalty_key,
        "row": [
            date,
            user,
            "Vi phạm",
            rule["violation"],
            rule["amount"],
            status,
            rule["record_type"],
            paid_flag,
            note
        ]
    }


def build_payment_only_penalty_row(
    payment,
    penalty_rules
):
    date = payment.get("date", "")
    user = payment.get("user", "")
    code = payment.get("code", "")

    rule = penalty_rules.get(
        code,
        {}
    )

    violation = rule.get(
        "violation",
        code
    )

    amount = payment.get(
        "paid_amount",
        0
    )

    status = payment.get(
        "status",
        "Đã đóng"
    )

    paid_flag = (
        "x"
        if is_paid_status(status)
        else ""
    )

    record_type = rule.get(
        "record_type",
        "Thanh toán thủ công"
    )

    note = get_payment_note(
        payment
    )

    return [
        date,
        user,
        "Thanh toán thủ công",
        violation,
        amount,
        status,
        record_type,
        paid_flag,
        note
    ]


def build_penalty_rows(
    under_hours_rows,
    no_log_rows,
    late_logs,
    penalty_rules,
    penalty_payments
):
    penalty_rows = []
    generated_keys = set()

    no_log_rule = penalty_rules.get("NO_LOG")
    under_hours_rule = penalty_rules.get("UNDER_HOURS")
    late_rule = penalty_rules.get("LATE")

    if no_log_rule:
        for row in no_log_rows:
            result = build_violation_penalty_row(
                date=row[0],
                user=row[1],
                code="NO_LOG",
                rule=no_log_rule,
                penalty_payments=penalty_payments
            )

            generated_keys.add(
                result["key"]
            )

            penalty_rows.append(
                result["row"]
            )

    if under_hours_rule:
        for row in under_hours_rows:
            result = build_violation_penalty_row(
                date=row[0],
                user=row[1],
                code="UNDER_HOURS",
                rule=under_hours_rule,
                penalty_payments=penalty_payments,
                extra_note=f"Thiếu {row[3]}h"
            )

            generated_keys.add(
                result["key"]
            )

            penalty_rows.append(
                result["row"]
            )

    if late_rule:
        for item in late_logs:
            result = build_violation_penalty_row(
                date=item["date"],
                user=item["user"],
                code="LATE",
                rule=late_rule,
                penalty_payments=penalty_payments,
                extra_note=(
                    f"Trễ "
                    f"{item['late_minutes']} phút"
                )
            )

            generated_keys.add(
                result["key"]
            )

            penalty_rows.append(
                result["row"]
            )

    for penalty_key, payment in penalty_payments.items():
        if penalty_key in generated_keys:
            continue

        penalty_rows.append(
            build_payment_only_penalty_row(
                payment=payment,
                penalty_rules=penalty_rules
            )
        )

    return sorted(
        penalty_rows,
        key=lambda row: (
            row[0],
            row[1],
            row[3]
        )
    )


def build_penalty_pending_rows(penalty_rows):
    return [
        row
        for row in penalty_rows
        if row[2] == "Vi phạm"
        and not is_closed_status(row[5])
    ]


def build_pending_penalty_summary(penalty_pending_rows):
    summary = {}

    for row in penalty_pending_rows:
        user = row[1]
        amount = row[4]

        if user not in summary:
            summary[user] = {
                "count": 0,
                "amount": 0
            }

        summary[user]["count"] += 1
        summary[user]["amount"] += amount

    return summary