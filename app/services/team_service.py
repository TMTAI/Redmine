from collections import defaultdict


def get_user_team(user, user_teams):
    team = user_teams.get(user, "").strip()

    if not team:
        return "UNKNOWN"

    return team


def build_team_summary_rows(
    mapped_users,
    user_teams,
    summary_hours,
    summary_days,
    leave_summary,
    missing_summary
):
    team_data = {}

    for user in mapped_users:
        team = get_user_team(
            user,
            user_teams
        )

        if team not in team_data:
            team_data[team] = {
                "members": set(),
                "logged_days": 0,
                "total_hours": 0.0,
                "leave_days": 0.0,
                "missing_days": 0,
                "missing_hours": 0.0
            }

        team_data[team]["members"].add(user)

        team_data[team]["logged_days"] += len(
            summary_days[user]
        )

        team_data[team]["total_hours"] += summary_hours[user]

        team_data[team]["leave_days"] += leave_summary.get(
            user,
            0
        )

        team_data[team]["missing_days"] += (
            missing_summary
            .get(user, {})
            .get("days", 0)
        )

        team_data[team]["missing_hours"] += (
            missing_summary
            .get(user, {})
            .get("hours", 0)
        )

    rows = []

    for team in sorted(team_data.keys()):
        data = team_data[team]

        rows.append([
            team,
            len(data["members"]),
            data["logged_days"],
            round(data["total_hours"], 2),
            round(data["leave_days"], 2),
            data["missing_days"],
            round(data["missing_hours"], 2)
        ])

    return rows


def build_team_productivity_rows(
    mapped_users,
    user_teams,
    required_hours,
    summary_hours,
    user_leaves,
    working_days_count,
    min_hours_per_day
):
    team_data = {}

    for user in mapped_users:
        team = get_user_team(
            user,
            user_teams
        )

        user_required_hours = required_hours.get(
            user,
            min_hours_per_day
        )

        expected_hours = (
            working_days_count
            * user_required_hours
        )

        leave_hours = 0

        for (
            leave_date,
            leave_user
        ), hours in user_leaves.items():
            if leave_user == user:
                leave_hours += hours

        expected_hours = max(
            0,
            expected_hours - leave_hours
        )

        actual_hours = summary_hours[user]

        if team not in team_data:
            team_data[team] = {
                "expected_hours": 0.0,
                "actual_hours": 0.0,
                "leave_hours": 0.0
            }

        team_data[team]["expected_hours"] += expected_hours
        team_data[team]["actual_hours"] += actual_hours
        team_data[team]["leave_hours"] += leave_hours

    rows = []

    for team in sorted(team_data.keys()):
        data = team_data[team]

        expected = data["expected_hours"]
        actual = data["actual_hours"]

        productivity = 0

        if expected > 0:
            productivity = (
                actual / expected
            ) * 100

        rows.append([
            team,
            round(expected, 2),
            round(actual, 2),
            round(data["leave_hours"], 2),
            round(productivity, 2)
        ])

    return rows


def build_team_project_rows(
    detail_rows,
    user_teams
):
    """
    detail_rows format:
    [
        Date,
        User,
        Redmine,
        Project,
        Issue ID,
        Issue URL,
        Hours
    ]
    """

    team_project_hours = defaultdict(float)

    for row in detail_rows:
        user = row[1]
        project = row[3]
        hours = row[6]

        team = get_user_team(
            user,
            user_teams
        )

        key = (
            team,
            project
        )

        team_project_hours[key] += hours

    rows = []

    for (
        team,
        project
    ), hours in sorted(
        team_project_hours.items()
    ):
        rows.append([
            team,
            project,
            round(hours, 2)
        ])

    return rows