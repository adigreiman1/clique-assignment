import csv
import json
import sys
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
    # Rule 1: skip members contacted in the last 7 days
    if last_contact is not None and days_since(last_contact["last_contact_utc"], today) < 7:
        return False

    # Rule 2: no check-ins on holidays
    if today.isoformat() in holidays:
        return False

    # Rule 3: the member must have a preferred channel
    if not member["preferred_channel"].strip():
        return False

    return True

def priority_score(member: dict, last_contact: dict | None, today: date) -> float:
    """Return how urgently the member needs a check-in."""
    flags = parse_flags(member["risk_flags"])
    score = 0.0

    if "recent_discharge" in flags:
        score += 3
    if "lives_alone" in flags:
        score += 2
    if int(member["age"]) >= 80:
        score += 1

        # Only members with a contact record have an outcome and a gap to measure
    if last_contact is not None:
        if last_contact["outcome"] == "no_answer":
            score += 1
        score += days_since(last_contact["last_contact_utc"], today) / 7    

    return score   

def recommended_window(member: dict) -> str:
    """Return the best time of day to contact the member."""
    return "morning" if int(member["age"]) >= 80 else "afternoon" 

def latest_contact_by_member(last_contacts: list[dict]) -> dict:
    """Map each member_id to their most recent contact record."""
    latest = {}
    for record in last_contacts:
        member_id = record["member_id"]
        if member_id not in latest or record["last_contact_utc"] > latest[member_id]["last_contact_utc"]:
            latest[member_id] = record
    return latest

def load_data():
    with open(f"{DATA_PATH}/members.csv") as f:
        members = list(csv.DictReader(f))
    with open(f"{DATA_PATH}/last_contacts.csv") as f:
        last_contacts = list(csv.DictReader(f))
    with open(f"{DATA_PATH}/holidays.json") as f:
        holidays = json.load(f)
    return members, last_contacts, holidays

def calculate_due_members(members, last_contacts, holidays, today, top=5):
    """Return the members who need a check-in today, most urgent first."""
    latest = latest_contact_by_member(last_contacts)
    results = []

    for member in members:
        last_contact = latest.get(member["member_id"])
        if not is_due(member, last_contact, today, holidays):
            continue
        results.append({
            "member_id": member["member_id"],
            "full_name": member["full_name"],
            "priority_score": round(priority_score(member, last_contact, today), 1),
            "recommended_window": recommended_window(member),
        })

    results.sort(key=lambda r: r["priority_score"], reverse=True)
    return results[:top]

def main():
    members, last_contacts, holidays = load_data()
    # Optional date argument, e.g. python checkin.py 2025-11-05
    today = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
    results = calculate_due_members(members, last_contacts, holidays, today)
    print(f"Members due for check-in on {today}:")
    for m in results:
        print(m)

if __name__ == "__main__":
    main()
