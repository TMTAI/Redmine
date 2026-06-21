from app.services.date_service import is_date_in_range


def filter_user_leaves_by_date(
    user_leaves,
    from_date,
    to_date
):
    return {
        key: value
        for key, value in user_leaves.items()
        if is_date_in_range(
            key[0],
            from_date,
            to_date
        )
    }

def merge_user_leaves(
    base_leaves,
    extra_leaves,
    required_hours,
    default_required_hours=8
):
    merged = dict(base_leaves)

    for key, leave_hours in extra_leaves.items():
        user = key

        max_hours = required_hours.get(
            user,
            default_required_hours
        )

        merged[key] = min(
            max_hours,
            merged.get(key, 0) + leave_hours
        )

    return merged