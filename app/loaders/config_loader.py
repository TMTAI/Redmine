import json
from datetime import datetime, timedelta


def load_config():

    with open(
        "config.json",
        encoding="utf-8"
    ) as f:

        config = json.load(f)

    report = config["report"]

    toDate = report["to_date"]
    if toDate == "today":
        toDate = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        toDate = report["to_date"]

    return {
        "data_source": config.get(
            "data_source",
            "redmine"
        ),
        "redmines": config.get(
            "redmines",
            []
        ),
        "local_csv": config.get(
            "local_csv",
            {
                "input_folder": "input"
            }
        ),
        "from_date": report["from_date"],
        "to_date": toDate,
        "min_hours_per_day": report.get(
            "min_hours_per_day",
            8
        )
    }