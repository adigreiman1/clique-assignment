import csv
import json
from datetime import date, datetime
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parent.parent / "data"

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

def score_breakdown(member: dict, last_contact: dict | None, today: date) -> list[tuple[str, float]]:
    """Return each reason that adds to the score, with its points."""
    flags = parse_flags(member["risk_flags"])
    reasons = []

    if "recent_discharge" in flags:
        reasons.append(("recent discharge", 3))
    if "lives_alone" in flags:
        reasons.append(("lives alone", 2))
    if int(member["age"]) >= 80:
        reasons.append(("age 80+", 1))

    # Only members with a contact record have an outcome and a gap to measure
    if last_contact is not None:
        if last_contact["outcome"] == "no_answer":
            reasons.append(("last contact: no answer", 1))
        days = days_since(last_contact["last_contact_utc"], today)
        reasons.append((f"{days} days since contact", days / 7))

    return reasons

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
        breakdown = score_breakdown(member, last_contact, today)
        results.append({
            "member_id": member["member_id"],
            "full_name": member["full_name"],
            "priority_score": sum((points for _, points in breakdown), 0.0),
            "recommended_window": recommended_window(member),
            "_breakdown": breakdown,  # temporary; converted to the public field below
        })

    results.sort(key=lambda r: r["priority_score"], reverse=True)
    top_results = results[:top]
    for r in top_results:
        r["priority_score"] = round(r["priority_score"], 1)
        r["score_breakdown"] = [
            {"reason": reason, "points": round(points, 1)}
            for reason, points in r.pop("_breakdown")
        ]
    return top_results
