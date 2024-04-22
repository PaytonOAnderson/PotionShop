from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from src.api.db_variables import CARTS, CUSTOMER, INVENTORY, ITEMS, CAPACITY



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
        #TODO bottle potions up to potion_limit//types of potion
        potion_limit = connection.execute(sqlalchemy.text(f"SELECT potion_capacity FROM {CAPACITY}")).fetchone()[0]
        result = []
        items = connection.execute(sqlalchemy.text(f"SELECT * FROM {ITEMS} WHERE sku != 'TEAL_POTION_0'"))
        print(f"items {items}")
        item_count = connection.execute(sqlalchemy.text(f"SELECT COUNT(*) FROM {ITEMS} WHERE sku != 'TEAL_POTION_0'")).fetchone()[0]
        print(f"item count {item_count}")
        

        green_ml = connection.execute(sqlalchemy.text(f"SELECT num_green_ml FROM {INVENTORY}")).fetchone()[0]
        
        red_ml = connection.execute(sqlalchemy.text(f"SELECT num_red_ml FROM {INVENTORY}")).fetchone()[0]

        blue_ml = connection.execute(sqlalchemy.text(f"SELECT num_blue_ml FROM {INVENTORY}")).fetchone()[0]

        dark_ml = connection.execute(sqlalchemy.text(f"SELECT num_dark_ml FROM {INVENTORY}")).fetchone()[0]

        for item in items:
            qty = 0
            min_qty = float('inf')  # Initialize min_qty to positive infinity
            # print(f"item {item}")
            if item.red_qty != 0:
                min_qty = min(min_qty, red_ml // item.red_qty)
                # print(f"1 : {min_qty}")
            if item.green_qty != 0:
                min_qty = min(min_qty, green_ml // item.green_qty)
                # print(f"2 : {min_qty}")
            if item.blue_qty != 0:
                min_qty = min(min_qty, blue_ml // item.blue_qty)
                # print(f"3 : {min_qty}")
            if item.dark_qty != 0:
                min_qty = min(min_qty, dark_ml // item.dark_qty)
                # print(f"4 : {min_qty}")
            if min_qty != float('inf'):
                max_qty = potion_limit // item_count
                max_qty -= item.qty
                qty = min(max_qty, min_qty, potion_limit - total_potions)
                # print(f"max: {max_qty} min: {min_qty} limit - total = {potion_limit - total_potions}, {potion_limit}, {total_potions}")
                
                # print(f"qty to bottle: {qty}")
                if qty > 0:
                    result.append(
                        {
                            "potion_type": [item.red_qty, item.green_qty, item.blue_qty, item.dark_qty],
                            "quantity": qty,
                        }
                    )
                    total_potions += qty
                    red_ml -= item.red_qty * qty
                    green_ml -= item.green_qty * qty
                    blue_ml -= item.blue_qty * qty
                    dark_ml -= item.dark_qty * qty
        print(f"bottler result: {result}")
        return result
        

if __name__ == "__main__":
    print(get_bottle_plan())