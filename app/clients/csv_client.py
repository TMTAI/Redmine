import csv
import glob
import os


def get_all_time_entries_from_csv(
    input_folder,
    default_redmine
):

    entries = []

    csv_files = glob.glob(
        os.path.join(
            input_folder,
            "*.csv"
        )
    )

    if not csv_files:
        raise Exception(
            f"No CSV files found in folder: {input_folder}"
        )

    for csv_file in csv_files:

        print(f"Reading CSV: {csv_file}")

        with open(
            csv_file,
            encoding="utf-8-sig"
        ) as f:

            reader = csv.DictReader(f)

            for line_no, row in enumerate(reader, start=2):

                try:

                    if not any(row.values()):
                        continue

                    project = row.get("Project", "").strip()
                    date = row.get("Date", "").strip()
                    user = row.get("User", "").strip()
                    hours = row.get("Hours", "").strip()

                    if not date or not user or not hours:
                        continue

                    entry = {
                        "spent_on": date,
                        "project": {
                            "name": project
                        },
                        "user": {
                            "name": user
                        },
                        "hours": float(
                            hours.replace(",", ".")
                        ),
                        "_redmine_name": default_redmine
                    }

                    entries.append(entry)

                except Exception as ex:

                    print(
                        f"ERROR in {csv_file} line {line_no}"
                    )
                    print(row)
                    print(ex)

    return entries