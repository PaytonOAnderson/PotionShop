from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

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
            if potion.potion_type == [0, 1, 0, 0]:
                connection.execute(sqlalchemy.text(f"Update global_inventory SET num_green_ml = num_green_ml - {potion.quantity * 100}"))
                connection.execute(sqlalchemy.text(f"Update global_inventory SET num_green_potions = num_green_potions + {potion.quantity}"))
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
        green_ml_table = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory"))
        for row in green_ml_table:
            green_ml = row[0]
        potions = green_ml // 100
        return [
                {
                    "potion_type": [0, 100, 0, 0],
                    "quantity": potions,
                }
            ]

if __name__ == "__main__":
    print(get_bottle_plan())