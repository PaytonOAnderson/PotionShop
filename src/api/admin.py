from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from src.api.db_variables import CARTS, CUSTOMER, INVENTORY, ITEMS, CAPACITY

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
        connection.execute(sqlalchemy.text(f'''UPDATE {INVENTORY} SET gold = 100,
                                            num_red_ml = 0,
                                            num_green_ml = 0,
                                            num_blue_ml = 0,
                                            num_dark_ml = 0,
                                            num_potions = 0'''))
        connection.execute(sqlalchemy.text(f'''UPDATE {CAPACITY} SET potion_capacity = 50,
                                            ml_capacity = 10000'''))
        connection.execute(sqlalchemy.text(f"UPDATE {ITEMS} SET qty = 0"))
        connection.execute(sqlalchemy.text("DELETE FROM account_ledger_entries"))
        connection.execute(sqlalchemy.text("DELETE FROM account_transactions"))
        connection.execute(sqlalchemy.text(f'''UPDATE accounts SET gold = 100,
                                            ml = 0,
                                            potions = 0,
                                            potion_capacity = 50,
                                            ml_capacity = 10000'''))
        
        
    return "OK"
