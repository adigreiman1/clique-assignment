# Clique Check-in Tool

A tool that tells community coordinators which members are due for a check-in today, and in what order of priority.

It has three parts:
- **Core logic** (`src/checkin.py`): decides who is due, calculates the priority score and explains it.
- **API** (`src/api.py`): `GET /due?top=5&date=2025-11-05`. Each member includes a `score_breakdown` list (reason and points).
- **Web page** (`src/index.html`): a table of members due, with a date picker and a "Details" button that shows why each member got their score.

## How to run

1. Create and activate a virtual environment, then install the dependencies:

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install fastapi uvicorn pytest
```

2. Command line (optional, a quick way to run the logic without a server; the date is optional and defaults to today):

```
python src\checkin.py 2025-11-05
```

It prints the members due as an aligned table, including the score breakdown for each member.

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
- **The score is built from a list of reasons.** The same list produces the score and the breakdown, so they can never disagree.
- **The web page builds its table with `createElement` and `textContent`,** so values from the server are never parsed as HTML.

## What I would improve with more time

- Show members who were never contacted separately, or ask a coordinator how they should be ranked, so they are not buried low in the list just because they have no gap to measure.
- Decide how `escalate` should affect priority, together with a coordinator.
- Validate the input files (bad ages, unknown channels, malformed rows) and report problems clearly.
- Use Israel local time for "today" instead of UTC.
- Move the scoring weights into a config file, so they can be tuned without changing code.
- Add API tests, and a clear tie-breaking rule.
- Add a "Contact" button on each member that opens the conversation in their preferred channel (call, SMS or WhatsApp). This needs phone numbers, which are not in the current data.
- Improve the visual design of the page, for example better support for small screens.

## Tools and how I worked

I used two AI tools:
- **Claude (chat):** I used it as a guide, not as a code generator. Before every step I asked what the step does and why, discussed how to approach it, and used it to check that I hadn't missed a requirement and to help with syntax. I kept the work in small steps so I could understand every line.
- **Claude Code:** I used it for the score breakdown feature. I wrote the prompts, asked it to read the code and show a plan before changing anything, and reviewed what it did.

### Where I questioned the AI's suggestions
- **Members with no contact record.** The AI suggested treating them as "30 days since contact" so they rise in the list. I rejected it, because 30 is an invented number the task doesn't mention. Instead they get no time bonus, and I listed this as a known weakness above.
- **What counts as an existing channel.** The AI first suggested a fixed list of channels. I disagreed: the sample data is small, and a fixed list would silently drop any new channel.
- **The score breakdown view.** The first version added a column that took over the whole table. I asked for a "Details" button that is hidden by default, then changed the layout until it was easy to scan.
- **HTML injection.** The AI offered to leave this as a README note. I decided to fix it now.