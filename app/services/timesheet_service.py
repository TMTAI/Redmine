from collections import defaultdict
from datetime import datetime, timedelta

from app.services.dashboard_service import build_dashboard_rows
from app.services.penalty_service import (build_penalty_rows, build_penalty_pending_rows, build_pending_penalty_summary)
from app.services.dashboard_service import build_dashboard_rows
from app.services.date_service import is_date_in_range

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


def build_detail_result(
    all_entries,
    user_mapping,
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
            redmine_name = item.get(
                "_redmine_name",
                default_redmine
            )

            project = item.get(
                "project",
                {}
            ).get(
                "name",
                ""
            )

            user_name = item.get(
                "user",
                {}
            ).get(
                "name",
                ""
            )

            hours = float(
                item.get(
                    "hours",
                    0
                )
            )

            issue = item.get(
                "issue",
                {}
            )

            issue_id = issue.get(
                "id",
                ""
            )

            issue_url = ""

            redmine_url = item.get(
                "_redmine_url",
                ""
            )

            if issue_id and redmine_url:
                issue_url = (
                    f"{redmine_url}/issues/{issue_id}"
                )

            user_key = (
                user_name
                .strip()
                .lower()
            )

            standard_user = user_mapping.get(
                user_key
            )

            if standard_user is None:
                continue

            users_found.add(
                standard_user
            )

            if standard_user not in user_redmine:
                user_redmine[
                    standard_user
                ] = redmine_name

            detail_rows.append([
                date,
                standard_user,
                redmine_name,
                project,
                issue_id,
                issue_url,
                hours
            ])

            user_hours[
                (
                    date,
                    standard_user
                )
            ] += hours

            summary_hours[
                standard_user
            ] += hours

            summary_days[
                standard_user
            ].add(date)

        except Exception as ex:
            print("ERROR while building detail result:")
            print(item)
            print(ex)

    detail_rows = sorted(
        detail_rows,
        key=lambda row: (
            row[0],  # Date
            row[1],  # User
            row[3],  # Project
            row[4]   # Issue ID
        )
    )

    return {
        "detail_rows": detail_rows,
        "user_hours": user_hours,
        "summary_hours": summary_hours,
        "summary_days": summary_days,
        "users_found": users_found,
        "user_redmine": user_redmine
    }


def build_under_hours_rows(
    user_hours,
    required_hours,
    user_leaves,
    min_hours_per_day
):
    under_hours_rows = []

    for (date, user), total in sorted(
        user_hours.items()
    ):
        base_required = required_hours.get(
            user,
            min_hours_per_day
        )

        leave_hours = user_leaves.get(
            (
                date,
                user
            ),
            0
        )

        required = max(
            0,
            base_required - leave_hours
        )

        EPSILON = 0.01

        total = round(total, 2)
        required = round(required, 2)
        missing = round(required - total, 2)

        if required > 0 and missing > EPSILON:
            under_hours_rows.append([
                date,
                user,
                total,
                missing,
                required
            ])

    return under_hours_rows


def build_no_log_rows(
    mapped_users,
    user_hours,
    required_hours,
    user_leaves,
    user_redmine,
    working_days,
    default_redmine,
    min_hours_per_day
):
    no_log_rows = []

    for user in sorted(mapped_users):
        base_required = required_hours.get(
            user,
            min_hours_per_day
        )

        for date in working_days:
            leave_hours = user_leaves.get(
                (
                    date,
                    user
                ),
                0
            )

            required = max(
                0,
                base_required - leave_hours
            )

            if required <= 0:
                continue

            if (date, user) not in user_hours:
                no_log_rows.append([
                    date,
                    user,
                    user_redmine.get(
                        user,
                        default_redmine
                    ),
                    required
                ])

    return no_log_rows


def build_summary_rows(
    mapped_users,
    summary_hours,
    summary_days,
    required_hours,
    min_hours_per_day,
    missing_summary
):
    summary_rows = []

    for user in sorted(mapped_users):

        missing_days = (
            missing_summary
            .get(user, {})
            .get("days", 0)
        )

        missing_hours = (
            missing_summary
            .get(user, {})
            .get("hours", 0)
        )

        summary_rows.append([
            user,
            len(summary_days[user]),
            round(summary_hours[user], 2),
            required_hours.get(
                user,
                min_hours_per_day
            ),
            missing_days,
            round(missing_hours, 2)
        ])

    return summary_rows


def build_missing_summary(
    under_hours_rows,
    no_log_rows
):
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

    for user in sorted(
        missing_summary.keys()
    ):
        missing_summary_rows.append([
            user,
            missing_summary[user]["days"],
            round(
                missing_summary[user]["hours"],
                2
            )
        ])

    return (
        missing_summary,
        missing_summary_rows
    )

def build_over_hours_rows(
    user_hours,
    required_hours,
    user_leaves,
    min_hours_per_day
):
    over_hours_rows = []

    for (date, user), total in sorted(
        user_hours.items()
    ):
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

        if required > 0 and total > required:
            over_hours_rows.append([
                date,
                user,
                round(total, 2),
                round(required, 2),
                round(total - required, 2)
            ])

    return over_hours_rows

def build_leave_summary(
    mapped_users,
    user_leaves,
    required_hours,
    min_hours_per_day
):
    leave_summary = {
        user: 0
        for user in mapped_users
    }

    for (date, user), leave_hours in user_leaves.items():
        required = required_hours.get(
            user,
            min_hours_per_day
        )

        if required <= 0:
            continue

        leave_summary[user] = (
            leave_summary.get(user, 0)
            + leave_hours / required
        )

    return leave_summary

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
    working_days = build_working_days(
        from_date=from_date,
        to_date=to_date,
        holidays=holidays
    )

    working_days_count = len(
        working_days
    )

    detail_result = build_detail_result(
        all_entries=all_entries,
        user_mapping=user_mapping,
        default_redmine=default_redmine
    )

    detail_rows = detail_result[
        "detail_rows"
    ]

    user_hours = detail_result[
        "user_hours"
    ]

    summary_hours = detail_result[
        "summary_hours"
    ]

    summary_days = detail_result[
        "summary_days"
    ]

    users_found = detail_result[
        "users_found"
    ]

    user_redmine = detail_result[
        "user_redmine"
    ]

    under_hours_rows = build_under_hours_rows(
        user_hours=user_hours,
        required_hours=required_hours,
        user_leaves=user_leaves,
        min_hours_per_day=min_hours_per_day
    )

    over_hours_rows = build_over_hours_rows(
        user_hours=user_hours,
        required_hours=required_hours,
        user_leaves=user_leaves,
        min_hours_per_day=min_hours_per_day
    )

    no_log_rows = build_no_log_rows(
        mapped_users=mapped_users,
        user_hours=user_hours,
        required_hours=required_hours,
        user_leaves=user_leaves,
        user_redmine=user_redmine,
        working_days=working_days,
        default_redmine=default_redmine,
        min_hours_per_day=min_hours_per_day
    )

    (
        missing_summary,
        missing_summary_rows
    ) = build_missing_summary(
        under_hours_rows=under_hours_rows,
        no_log_rows=no_log_rows
    )

    missing_log_rows = build_missing_log_rows(
        under_hours_rows=under_hours_rows,
        no_log_rows=no_log_rows,
        default_redmine=default_redmine
    )

    summary_rows = build_summary_rows(
        mapped_users=mapped_users,
        summary_hours=summary_hours,
        summary_days=summary_days,
        required_hours=required_hours,
        min_hours_per_day=min_hours_per_day,
        missing_summary=missing_summary
    )

    late_logs_in_range = [
        item
        for item in late_logs
        if is_date_in_range(
            item["date"],
            from_date,
            to_date
        )
    ]

    penalty_rows = build_penalty_rows(
        under_hours_rows=under_hours_rows,
        no_log_rows=no_log_rows,
        late_logs=late_logs_in_range,
        penalty_rules=penalty_rules,
        penalty_payments=penalty_payments
    )

    penalty_pending_rows = build_penalty_pending_rows(
        penalty_rows
    )

    penalty_pending_summary = build_pending_penalty_summary(
        penalty_pending_rows
    )

    leave_summary = build_leave_summary(
        mapped_users=mapped_users,
        user_leaves=user_leaves,
        required_hours=required_hours,
        min_hours_per_day=min_hours_per_day
    )

    dashboard_rows = build_dashboard_rows(
        mapped_users=mapped_users,
        leave_summary=leave_summary,
        summary_hours=summary_hours,
        summary_days=summary_days,
        no_log_rows=no_log_rows,
        under_hours_rows=under_hours_rows,
        late_logs=late_logs_in_range,
        penalty_pending_summary=penalty_pending_summary
    )

    leave_rows = build_leave_rows(
        user_leaves=user_leaves,
        required_hours=required_hours,
        min_hours_per_day=min_hours_per_day
    )

    return {
        "detail_rows": detail_rows,
        "under_hours_rows": under_hours_rows,
        "no_log_rows": no_log_rows,
        "summary_rows": summary_rows,
        "dashboard_rows": dashboard_rows,
        "users_found": users_found,
        "working_days_count": working_days_count,
        "over_hours_rows": over_hours_rows,
        "penalty_rows": penalty_rows,
        "penalty_pending_rows": penalty_pending_rows,
        "missing_log_rows": missing_log_rows,
        "leave_rows": leave_rows,
    }

def build_missing_log_rows(
    under_hours_rows,
    no_log_rows,
    default_redmine
):
    missing_log_rows = []

    for row in under_hours_rows:
        missing_log_rows.append([
            row[0],
            row[1],
            "",
            row[2],
            row[4],
            row[3],
            "",
            1
        ])

    for row in no_log_rows:
        missing_log_rows.append([
        row[0],
        row[1],
        row[2],
        0,
        row[3],
        row[3],
        "X",
        0
    ])

    missing_log_rows = sorted(
        missing_log_rows,
        key=lambda row: (
            row[0],                     # Date
            0 if row[7] == "NO_LOG" else 1,  # No Log trước
            row[1]                      # User
        )
    )

    for row in missing_log_rows:
        row.pop()

    return missing_log_rows


def build_leave_rows(
    user_leaves,
    required_hours,
    min_hours_per_day
):
    leave_rows = []

    for (date, user), leave_hours in sorted(
        user_leaves.items()
    ):
        required = required_hours.get(
            user,
            min_hours_per_day
        )

        leave_days = 0

        if required > 0:
            leave_days = leave_hours / required

        leave_rows.append([
            date,
            user,
            round(leave_hours, 2),
            round(leave_days, 2)
        ])

    return leave_rows