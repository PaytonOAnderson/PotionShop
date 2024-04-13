from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from src.api.inventory import INVENTORY

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(f"Update {INVENTORY} SET gold = 100"))
        connection.execute(sqlalchemy.text(f"Update {INVENTORY} SET num_green_ml = 0"))
        connection.execute(sqlalchemy.text(f"Update {INVENTORY} SET num_green_potions = 0"))
    return "OK"
