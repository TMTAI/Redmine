from app.loaders.config_loader import load_config
from app.loaders.mapping_loader import load_user_mapping
from app.loaders.holiday_loader import load_holidays
from app.loaders.leave_loader import load_user_leaves
from app.loaders.penalty_loader import load_penalty_rules
from app.loaders.late_loader import load_late_logs
from app.loaders.penalty_payment_loader import load_penalty_payments

from app.clients.redmine_client import (
    get_all_time_entries
)

from app.clients.csv_client import (
    get_all_time_entries_from_csv
)

from app.services.timesheet_service import (
    aggregate_entries
)

from app.reports.excel_report import (
    generate_excel
)


def main():

    print(
        "Loading configuration..."
    )

    config = load_config()

    data_source = config["data_source"]

    redmines = config["redmines"]

    from_date = config["from_date"]

    to_date = config["to_date"]

    min_hours_per_day = config[
        "min_hours_per_day"
    ]

    default_redmine = (
        redmines[0]["name"]
        if redmines
        else "LOCAL"
    )

    print(
        f"Data Source: "
        f"{data_source}"
    )

    print(
        f"Date Range : "
        f"{from_date} -> {to_date}"
    )

    print(
        "Loading user mapping..."
    )

    (
        user_mapping,
        mapped_users,
        required_hours
    ) = load_user_mapping()

    print(
        f"Mapped Users: "
        f"{len(mapped_users)}"
    )

    holidays = load_holidays()

    print(
        f"Holidays: "
        f"{len(holidays)}"
    )

    user_leaves = load_user_leaves()

    print(
        f"User Leaves: "
        f"{len(user_leaves)}"
    )

    late_logs = load_late_logs()

    print(
        f"Late Logs: {len(late_logs)}"
    )

    penalty_rules = load_penalty_rules()

    print(
        f"Penalty Rules: "
        f"{len(penalty_rules)}"
    )

    penalty_payments = load_penalty_payments()

    print(
        f"Penalty Payments: "
        f"{len(penalty_payments)}"
    )

    all_entries = []

    if data_source == "redmine":

        print()
        print(
            "Loading Redmine data..."
        )

        for redmine in redmines:

            print(
                f"Connecting to "
                f"{redmine['name']}..."
            )

            entries = get_all_time_entries(
                redmine_name=redmine["name"],
                redmine_url=redmine["url"],
                api_key=redmine["api_key"],
                from_date=from_date,
                to_date=to_date
            )

            for entry in entries:
                entry["_redmine_name"] = redmine["name"]
                entry["_redmine_url"] = redmine["url"].rstrip("/")

            print(
                f"Loaded "
                f"{len(entries)} entries"
            )

            all_entries.extend(
                entries
            )

    elif data_source == "local_csv":

        print()
        print(
            "Loading local CSV data..."
        )

        input_folder = config[
            "local_csv"
        ].get(
            "input_folder",
            "input"
        )

        all_entries = (
            get_all_time_entries_from_csv(
                input_folder=input_folder,
                default_redmine=default_redmine
            )
        )

    else:

        raise Exception(
            f"Unsupported data_source: "
            f"{data_source}"
        )

    print()
    print(
        f"Total Entries: "
        f"{len(all_entries)}"
    )

    print()
    print(
        "Processing timesheet..."
    )

    result = aggregate_entries(
        all_entries=all_entries,
        user_mapping=user_mapping,
        mapped_users=mapped_users,
        required_hours=required_hours,
        holidays=holidays,
        user_leaves=user_leaves,
        late_logs=late_logs,
        penalty_rules=penalty_rules,
        penalty_payments=penalty_payments,
        min_hours_per_day=min_hours_per_day,
        from_date=from_date,
        to_date=to_date,
        default_redmine=default_redmine
    )

    print(
        f"Users Found : "
        f"{len(result['users_found'])}"
    )

    print(
        f"Detail Rows : "
        f"{len(result['detail_rows'])}"
    )

    print(
        f"Under Hours : "
        f"{len(result['under_hours_rows'])}"
    )

    print(
        f"No Log      : "
        f"{len(result['no_log_rows'])}"
    )

    print()
    print(
        "Generating Excel report..."
    )

    output_file = generate_excel(
        result=result,
        output_folder="output",
        from_date=from_date,
        to_date=to_date,
        total_entries=len(all_entries),
        redmine_count=len(redmines),
        min_hours=min_hours_per_day
    )

    print()
    print("=" * 60)

    print(
        "REPORT GENERATED"
    )

    print(
        f"File: "
        f"{output_file}"
    )

    print("=" * 60)


if __name__ == "__main__":

    main()