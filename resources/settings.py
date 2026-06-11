import os

RESOURCE_FOLDER = "resources"

USER_MAPPING_FILE = os.path.join(
    RESOURCE_FOLDER,
    "user_mapping.csv"
)

HOLIDAY_FILE = os.path.join(
    RESOURCE_FOLDER,
    "holidays.csv"
)

USER_LEAVE_FILE = os.path.join(
    RESOURCE_FOLDER,
    "user_leaves.csv"
)

PENALTY_FOLDER = os.path.join(
    RESOURCE_FOLDER,
    "penalty"
)

PENALTY_RULE_FILE = os.path.join(
    PENALTY_FOLDER,
    "penalty_rules.csv"
)

LATE_LOG_FILE = os.path.join(
    PENALTY_FOLDER,
    "late_logs.csv"
)

PENALTY_EXCEPTION_FILE = os.path.join(
    PENALTY_FOLDER,
    "penalty_exceptions.csv"
)

PENALTY_PAYMENT_FILE = os.path.join(
    PENALTY_FOLDER,
    "penalty_payments.csv"
)