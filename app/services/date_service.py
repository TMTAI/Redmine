from datetime import datetime


def is_date_in_range(
    date_value,
    from_date,
    to_date
):
    if not date_value:
        return False

    date_obj = datetime.strptime(
        date_value,
        "%Y-%m-%d"
    )

    from_obj = datetime.strptime(
        from_date,
        "%Y-%m-%d"
    )

    to_obj = datetime.strptime(
        to_date,
        "%Y-%m-%d"
    )

    return from_obj <= date_obj <= to_obj