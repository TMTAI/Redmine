import requests


def get_all_time_entries(
    redmine_name,
    redmine_url,
    api_key,
    from_date,
    to_date
):

    headers = {
        "X-Redmine-API-Key": api_key
    }

    entries = []

    offset = 0
    limit = 100

    while True:

        params = {
            "from": from_date,
            "to": to_date,
            "offset": offset,
            "limit": limit
        }

        response = requests.get(
            f"{redmine_url.rstrip('/')}/time_entries.json",
            headers=headers,
            params=params,
            timeout=60
        )

        response.raise_for_status()

        data = response.json()

        entries.extend(
            data["time_entries"]
        )

        print(
            f"[{redmine_name}] "
            f"{len(entries)}/"
            f"{data['total_count']}"
        )

        offset += data["limit"]

        if offset >= data["total_count"]:
            break

    return entries