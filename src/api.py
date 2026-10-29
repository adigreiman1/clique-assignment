import datetime

from fastapi import FastAPI

from src.checkin import calculate_due_members, load_data

app = FastAPI()


@app.get("/due")
def get_due(top: int = 5, date: datetime.date | None = None):
    today = date or datetime.date.today()
    members, last_contacts, holidays = load_data()
    return calculate_due_members(members, last_contacts, holidays, today, top)