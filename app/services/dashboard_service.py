def get_current_status(
    pending_penalty_count,
    pending_penalty_amount
):
    if pending_penalty_count <= 0 and pending_penalty_amount <= 0:
        return "OK"

    return "Pending"


def build_dashboard_rows(
    mapped_users,
    leave_summary,
    summary_hours,
    summary_days,
    no_log_rows,
    under_hours_rows,
    late_logs,
    penalty_pending_summary
):
    no_log_count = {}
    under_hours_count = {}
    late_count = {}

    for row in no_log_rows:
        user = row[1]
        no_log_count[user] = no_log_count.get(user, 0) + 1

    for row in under_hours_rows:
        user = row[1]
        under_hours_count[user] = under_hours_count.get(user, 0) + 1

    for item in late_logs:
        user = item["user"]
        late_count[user] = late_count.get(user, 0) + 1

    dashboard_rows = []

    for user in sorted(mapped_users):
        pending = penalty_pending_summary.get(
            user,
            {
                "count": 0,
                "amount": 0
            }
        )

        pending_count = pending["count"]
        pending_amount = pending["amount"]

        dashboard_rows.append([
            0,
            user,
            round(leave_summary.get(user, 0), 2),
            len(summary_days[user]),
            round(summary_hours[user], 2),
            no_log_count.get(user, 0),
            under_hours_count.get(user, 0),
            late_count.get(user, 0),
            pending_count,
            round(pending_amount, 0),
            get_current_status(
                pending_count,
                pending_amount
            )
        ])

    dashboard_rows = sorted(
        dashboard_rows,
        key=lambda row: (
            row[8],
            row[9]
        ),
        reverse=True
    )

    for index, row in enumerate(dashboard_rows, start=1):
        row[0] = index

    return dashboard_rows