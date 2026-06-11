import sys

required_packages = [
    "requests",
    "openpyxl"
]

missing = []

for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        missing.append(package)

if missing:
    sys.exit(1)

sys.exit(0)