from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from src.api.db_variables import CARTS, CUSTOMER, INVENTORY, ITEMS, TIME

router = APIRouter(
    prefix="/info",
    tags=["info"],
    dependencies=[Depends(auth.get_api_key)],
)

class Timestamp(BaseModel):
    day: str
    hour: int

@router.post("/current_time")
def post_time(timestamp: Timestamp):
    """
    Share current time.
    """
    #TODO add current time to a databases to attack to transactions to see if date/time affects purchases
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(f"INSERT INTO {TIME} (day, hour) VALUES ('{timestamp.day}', {timestamp.hour})"))
    return "OK"

