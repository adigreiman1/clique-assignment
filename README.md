# Clique Check-in Tool

A tool that tells community coordinators which members are due for a check-in today, and in what order of priority.

It has three parts:
- **Core logic** (`src/checkin.py`): decides who is due and calculates the priority score.
- **API** (`src/api.py`): `GET /due?top=5&date=2025-11-05`
- **Web page** (`src/index.html`): a table of members due, with a date picker.

## How to run

1. Create and activate a virtual environment, then install the dependencies:

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install fastapi uvicorn pytest
```

2. Command line (the date is optional and defaults to today):

```
python src\checkin.py 2025-11-05
```

3. Web page and API:

```
python -m uvicorn src.api:app --reload
```

Then open `http://127.0.0.1:8000/` for the page, or `http://127.0.0.1:8000/due?top=5&date=2025-11-05` for the raw JSON.

4. Tests:

```
python -m pytest
```

Note: the sample data is from October 2025, so use a date around `2025-11-05` to see meaningful results. The web page starts on that date for the same reason. With today's real date every gap would be about a year long.

## Assumptions

- **"Today" is a parameter.** The logic never reads the clock itself, which makes it testable and lets us run it on the 2025 sample data.
- **Days are calendar days, in UTC.** Only dates are compared, not hours. A member last contacted a week ago in the evening counts as 7 days.
- **Exactly 7 days qualifies** ("at least 7 days").
- **A channel "exists" if the field is not empty.** I did not hard-code a list of channels, because the sample data may not show every channel that exists.
- **Members with no contact record are included** (as the task says). They have no date to measure a gap from, so they get no time bonus and no `no_answer` bonus. Their score comes only from their risk flags and age.
- **If a member has several contact records, the latest one is used.**
- **On a holiday, nobody is returned.** The web page shows a message instead of an empty table.
- **The `escalate` outcome has no points,** because the task does not define any.
- **Sorting uses the exact score.** Rounding to one decimal happens only for display, so two close scores are not treated as a tie.
- **Ties** keep the order of the members file.

## What I would improve with more time

- Show members who were never contacted separately, so they are not buried low in the list just because they have no gap to measure.
- Decide how `escalate` should affect priority, together with a coordinator.
- Show why a member has their score (for example "+3 discharge, +2 lives alone"), so coordinators can trust the order.
- Validate the input files (bad ages, unknown channels, malformed rows) and report problems clearly.
- Use Israel local time for "today" instead of UTC.
- Move the scoring weights into a config file, so they can be tuned without changing code.
- Add API tests, and a clear tie-breaking rule.

## Tools and how I worked

[Edit this section in your own words: which tools you used, why, what you checked or changed, and what you would do differently.]