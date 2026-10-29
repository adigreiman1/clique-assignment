import datetime
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse

from src.checkin import calculate_due_members, load_data

app = FastAPI()


@app.get("/")
def home():
    return FileResponse(Path(__file__).parent / "index.html")


@app.get("/due")
def get_due(top: int = Query(5, ge=1), date: datetime.date | None = None):
    today = date or datetime.date.today()
    members, last_contacts, holidays = load_data()
    return calculate_due_members(members, last_contacts, holidays, today, top)