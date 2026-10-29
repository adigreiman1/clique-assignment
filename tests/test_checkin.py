from datetime import date

from src.checkin import calculate_due_members


def test_no_members_due_on_holiday():
    members = [
        {"member_id": "1", "full_name": "Test Member", "age": "70",
         "preferred_channel": "call", "risk_flags": ""},
    ]
    last_contacts = [
        {"member_id": "1", "last_contact_utc": "2025-10-01T10:00:00Z", "outcome": "ok"},
    ]
    holidays = ["2025-11-07"]

    result = calculate_due_members(members, last_contacts, holidays, date(2025, 11, 7))

    assert result == []



def test_member_without_contact_record_is_included():
    members = [
        {"member_id": "1", "full_name": "Never Contacted", "age": "70",
         "preferred_channel": "call", "risk_flags": ""},
    ]
    last_contacts = []

    result = calculate_due_members(members, last_contacts, [], date(2025, 11, 5))

    assert len(result) == 1
    assert result[0]["member_id"] == "1"


def test_seven_day_boundary():
    members = [
        {"member_id": "1", "full_name": "Seven Days", "age": "70",
         "preferred_channel": "call", "risk_flags": ""},
        {"member_id": "2", "full_name": "Six Days", "age": "70",
         "preferred_channel": "call", "risk_flags": ""},
    ]
    last_contacts = [
        {"member_id": "1", "last_contact_utc": "2025-10-29T10:00:00Z", "outcome": "ok"},
        {"member_id": "2", "last_contact_utc": "2025-10-30T10:00:00Z", "outcome": "ok"},
    ]

    result = calculate_due_members(members, last_contacts, [], date(2025, 11, 5))

    assert [r["member_id"] for r in result] == ["1"]


def test_member_without_channel_is_excluded():
    members = [
        {"member_id": "1", "full_name": "No Channel", "age": "70",
         "preferred_channel": "", "risk_flags": ""},
        {"member_id": "2", "full_name": "Has Channel", "age": "70",
         "preferred_channel": "call", "risk_flags": ""},
    ]
    last_contacts = []

    result = calculate_due_members(members, last_contacts, [], date(2025, 11, 5))

    assert [r["member_id"] for r in result] == ["2"]


def test_sorted_by_priority_score():
    members = [
        {"member_id": "1", "full_name": "Low Risk", "age": "70",
         "preferred_channel": "call", "risk_flags": ""},
        {"member_id": "2", "full_name": "High Risk", "age": "85",
         "preferred_channel": "sms", "risk_flags": "lives_alone;recent_discharge"},
    ]
    last_contacts = [
        {"member_id": "1", "last_contact_utc": "2025-10-22T10:00:00Z", "outcome": "ok"},
        {"member_id": "2", "last_contact_utc": "2025-10-22T10:00:00Z", "outcome": "ok"},
    ]

    result = calculate_due_members(members, last_contacts, [], date(2025, 11, 5))

    assert [r["member_id"] for r in result] == ["2", "1"]
    assert result[0]["priority_score"] == 8.0
    assert result[0]["recommended_window"] == "morning"
    assert result[1]["recommended_window"] == "afternoon"