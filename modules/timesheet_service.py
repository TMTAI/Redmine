from collections import defaultdict
from datetime import datetime, timedelta


def build_working_days(from_date, to_date, holidays):
    working_days = []

    current = datetime.strptime(from_date, "%Y-%m-%d")
    end_date = datetime.strptime(to_date, "%Y-%m-%d")

    while current <= end_date:
        date_str = current.strftime("%Y-%m-%d")

        if current.weekday() < 5 and date_str not in holidays:
            working_days.append(date_str)

        current += timedelta(days=1)

    return working_days


def get_status(missing_hours):
    if missing_hours <= 0:
        return "OK"
    if missing_hours <= 8:
        return "Warning"
    return "Critical"


def aggregate_entries(
    all_entries,
    user_mapping,
    mapped_users,
    required_hours,
    holidays,
    user_leaves,
    late_logs,
    penalty_rules,
    penalty_payments,
    min_hours_per_day,
    from_date,
    to_date,
    default_redmine
):
    detail_rows = []

    user_hours = defaultdict(float)
    summary_hours = defaultdict(float)
    summary_days = defaultdict(set)

    users_found = set()
    user_redmine = {}

    for item in all_entries:
        try:
            date = item["spent_on"]
            redmine_name = item.get("_redmine_name", default_redmine)
            project = item.get("project", {}).get("name", "")
            user_name = item.get("user", {}).get("name", "")
            hours = float(item.get("hours", 0))

            issue = item.get("issue", {})
            issue_id = issue.get("id", "")

            issue_url = ""
            redmine_url = item.get("_redmine_url", "")
            if issue_id and redmine_url:
                issue_url = f"{redmine_url}/issues/{issue_id}"

            user_key = user_name.strip().lower()
            standard_user = user_mapping.get(user_key)

            if standard_user is None:
                continue

            users_found.add(standard_user)

            if standard_user not in user_redmine:
                user_redmine[standard_user] = redmine_name

            detail_rows.append([
                date,
                standard_user,
                redmine_name,
                project,
                issue_id,
                issue_url,
                hours
            ])

            detail_rows = sorted(
                detail_rows,
                key=lambda row: (
                    row[0],  # Date
                    row[1],  # User
                    row[3],  # Project
                    row[4]   # Issue ID
                )
            )

            user_hours[(date, standard_user)] += hours
            summary_hours[standard_user] += hours
            summary_days[standard_user].add(date)

        except Exception as ex:
            print("ERROR while aggregating entry:")
            print(item)
            print(ex)

    working_days = build_working_days(
        from_date,
        to_date,
        holidays
    )

    working_days_count = len(working_days)

    under_hours_rows = []

    for (date, user), total in sorted(user_hours.items()):
        base_required = required_hours.get(
            user,
            min_hours_per_day
        )

        leave_hours = user_leaves.get(
            (date, user),
            0
        )

        required = max(
            0,
            base_required - leave_hours
        )

        if required > 0 and total < required:
            under_hours_rows.append([
                date,
                user,
                round(total, 2),
                round(required - total, 2),
                required
            ])

    no_log_rows = []

    for user in sorted(mapped_users):
        base_required = required_hours.get(
            user,
            min_hours_per_day
        )

        for date in working_days:
            leave_hours = user_leaves.get(
                (date, user),
                0
            )

            required = max(
                0,
                base_required - leave_hours
            )

            # Nghỉ đủ cả ngày, không cần log
            if required <= 0:
                continue

            if (date, user) not in user_hours:
                no_log_rows.append([
                    date,
                    user,
                    user_redmine.get(user, default_redmine),
                    required
                ])

    summary_rows = []

    for user in sorted(mapped_users):
        summary_rows.append([
            user,
            len(summary_days[user]),
            round(summary_hours[user], 2),
            required_hours.get(user, min_hours_per_day)
        ])

    missing_summary = defaultdict(
        lambda: {
            "days": 0,
            "hours": 0.0
        }
    )

    for row in under_hours_rows:
        user = row[1]
        missing = row[3]

        missing_summary[user]["days"] += 1
        missing_summary[user]["hours"] += missing

    for row in no_log_rows:
        user = row[1]
        required = row[3]

        missing_summary[user]["days"] += 1
        missing_summary[user]["hours"] += required

    missing_summary_rows = []

    for user in sorted(missing_summary.keys()):
        missing_summary_rows.append([
            user,
            missing_summary[user]["days"],
            round(missing_summary[user]["hours"], 2)
        ])

    dashboard_rows = []

    for user in sorted(mapped_users):
        user_required_hours = required_hours.get(
            user,
            min_hours_per_day
        )

        expected_hours = (
            working_days_count * user_required_hours
        )

        total_hours = summary_hours[user]
        logged_days = len(summary_days[user])

        missing_days = missing_summary[user]["days"]
        missing_hours = missing_summary[user]["hours"]

        missing_percent = 0

        if expected_hours > 0:
            missing_percent = (
                missing_hours / expected_hours
            ) * 100

        dashboard_rows.append([
            0,
            user,
            round(missing_hours, 2),
            missing_days,
            logged_days,
            round(total_hours, 2),
            user_required_hours,
            working_days_count,
            round(expected_hours, 2),
            round(missing_percent, 2),
            get_status(missing_hours)
        ])

    dashboard_rows = sorted(
        dashboard_rows,
        key=lambda x: x[2],
        reverse=True
    )

    for index, row in enumerate(
        dashboard_rows,
        start=1
    ):
        row[0] = index

    penalty_rows = build_penalty_rows(
        under_hours_rows=under_hours_rows,
        no_log_rows=no_log_rows,
        late_logs=late_logs,
        penalty_rules=penalty_rules,
        penalty_payments=penalty_payments
    )

    penalty_rows = sorted(
        penalty_rows,
        key=lambda row: (
            row[0],  # Ngày
            row[1],  # Thành viên
            row[2]   # Vi phạm
        )
    )

    return {
        "detail_rows": detail_rows,
        "under_hours_rows": under_hours_rows,
        "no_log_rows": no_log_rows,
        "summary_rows": summary_rows,
        "missing_summary_rows": missing_summary_rows,
        "dashboard_rows": dashboard_rows,
        "users_found": users_found,
        "working_days_count": working_days_count,
        "penalty_rows": penalty_rows
    }

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

    return penalty_rows

def build_penalty_key(date, user, code):
    return (
        f"{date.replace('-', '')}"
        f"|{user}"
        f"|{code}"
    )