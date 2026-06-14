def get_status(missing_hours: float) -> str:
    if missing_hours <= 0:
        return "OK"

    if missing_hours <= 8:
        return "Warning"

    return "Critical"


def build_dashboard_rows(
    mapped_users,
    required_hours,
    summary_hours,
    summary_days,
    missing_summary,
    leave_summary,
    working_days_count,
    min_hours_per_day
):
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

        leave_days = round(
            leave_summary.get(user, 0),
            1
        )

        dashboard_rows.append([
            0,
            user,
            round(missing_hours, 2),
            missing_days,
            logged_days,
            leave_days,
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

    for index, row in enumerate(dashboard_rows, start=1):
        row[0] = index

    return dashboard_rows