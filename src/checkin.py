import csv
import json
from datetime import date, datetime, timezone
from pathlib import Path

# === Clique Home Assignment Starter (Python) ===
# You may freely modify this file or start from scratch.
# The data files are located in ../data/

DATA_PATH = "../data"

def parse_flags(raw: str) -> set[str]:
    """Return the member's risk statuses as a set."""
    return {flag for flag in raw.split(";") if flag}

def days_since(last_contact_utc: str, today: date) -> int:
    """Return the number of calendar days since the last contact."""
    last = datetime.fromisoformat(last_contact_utc.replace("Z", "+00:00")).date()
    return (today - last).days

def is_due(member: dict, last_contact: dict | None, today: date, holidays: list[str]) -> bool:
    """Return True if the member should be contacted today."""
    # Rule 1: no check-ins on holidays
    if today.isoformat() in holidays:
        return False

    # Rule 2: the member must have a preferred channel
    if not member["preferred_channel"].strip():
        return False

    # Rule 3: no previous contact, or at least 7 days have passed
    if last_contact is None:
        return True
    return days_since(last_contact["last_contact_utc"], today) >= 7

def load_data():
    with open(f"{DATA_PATH}/members.csv") as f:
        members = list(csv.DictReader(f))
    with open(f"{DATA_PATH}/last_contacts.csv") as f:
        last_contacts = list(csv.DictReader(f))
    with open(f"{DATA_PATH}/holidays.json") as f:
        holidays = json.load(f)
    return members, last_contacts, holidays

def calculate_due_members(members, last_contacts, holidays):
    # TODO: Implement logic from the assignment
    # 1. Determine who needs a check-in
    # 2. Compute priority_score
    # 3. Sort and return list
    return []

def main():
    members, last_contacts, holidays = load_data()
    results = calculate_due_members(members, last_contacts, holidays)
    print("Members due for check-in:")
    for m in results:
        print(m)

if __name__ == "__main__":
    main()
