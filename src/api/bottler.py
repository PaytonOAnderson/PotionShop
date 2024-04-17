from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from src.api.db_variables import CARTS, CUSTOMER, INVENTORY, ITEMS



router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    """ """
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")
    with db.engine.begin() as connection:
        for potion in potions_delivered:
            # update item table to include potion created
            connection.execute(sqlalchemy.text(f"Update {INVENTORY} SET num_red_ml = num_red_ml - {potion.potion_type[0] * potion.quantity}"))
            connection.execute(sqlalchemy.text(f"Update {INVENTORY} SET num_green_ml = num_green_ml - {potion.potion_type[1] * potion.quantity}"))
            connection.execute(sqlalchemy.text(f"Update {INVENTORY} SET num_blue_ml = num_blue_ml - {potion.potion_type[2] * potion.quantity}"))
            connection.execute(sqlalchemy.text(f"Update {INVENTORY} SET num_dark_ml = num_dark_ml - {potion.potion_type[3] * potion.quantity}"))
            connection.execute(sqlalchemy.text(f"Update {INVENTORY} SET num_potions = num_potions + {potion.quantity}"))
            connection.execute(sqlalchemy.text(f"UPDATE {ITEMS} SET qty = qty + {potion.quantity} WHERE red_qty = {potion.potion_type[0]} AND green_qty = {potion.potion_type[1]} AND blue_qty = {potion.potion_type[2]} AND dark_qty = {potion.potion_type[3]}"))
    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.
    
    with db.engine.begin() as connection:
        total_potions = connection.execute(sqlalchemy.text(f"SELECT num_potions FROM {INVENTORY}")).fetchone()[0]
        #TODO check what the limit is and update it
        potion_limit = 50
        result = []
        green_ml_table = connection.execute(sqlalchemy.text(f"SELECT num_green_ml FROM {INVENTORY}"))
        for row in green_ml_table:
            green_ml = row[0]
        green_potions = green_ml // 100
        if green_potions > 0:
            if green_potions > potion_limit - total_potions: green_potions = potion_limit - total_potions
            result.append(
                {
                    "potion_type": [0, 100, 0, 0],
                    "quantity": green_potions,
                }
            )
        red_ml_table = connection.execute(sqlalchemy.text(f"SELECT num_red_ml FROM {INVENTORY}"))
        for row in red_ml_table:
            red_ml = row[0]
        red_potions = red_ml // 100
        if red_potions > 0:
            if red_potions > potion_limit - total_potions: red_potions = potion_limit - total_potions
            result.append(
                {
                    "potion_type": [100, 0, 0, 0],
                    "quantity": red_potions,
                }
            )
        blue_ml_table = connection.execute(sqlalchemy.text(f"SELECT num_blue_ml FROM {INVENTORY}"))
        for row in blue_ml_table:
            blue_ml = row[0]
        blue_potions = blue_ml // 100
        if blue_potions > 0:
            if blue_potions > potion_limit - total_potions: blue_potions = potion_limit - total_potions
            result.append(
                {
                    "potion_type": [0, 0, 100, 0],
                    "quantity": blue_potions,
                }
            )
        return result
        

if __name__ == "__main__":
    print(get_bottle_plan())