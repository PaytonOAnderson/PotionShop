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
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml - :red_qty * :qty, num_green_ml = num_green_ml - :green_qty * :qty, num_blue_ml = num_blue_ml - :blue_qty * :qty, num_dark_ml = num_dark_ml - :dark_qty * :qty, num_potions = num_potions + :qty"),
                               [{"red_qty" :potion.potion_type[0], "green_qty" : potion.potion_type[1], "blue_qty" : potion.potion_type[2], "dark_qty" : potion.potion_type[3], "qty" : potion.quantity}])
            connection.execute(sqlalchemy.text("UPDATE tems SET qty = qty + :qty WHERE red_qty = :red_qty AND green_qty = :green_qty AND blue_qty = :blue_qty AND dark_qty = :dark_qty") ,[{"qty" : potion.quantity, "red_qty" : potion.potion_type[0], "green_qty" : potion.potion_type[1], "blue_qty" : potion.potion_type[2], "dark_qty" : potion.potion_type[3]}])
            transaction_id = connection.execute(sqlalchemy.text("INSERT INTO account_transactions (description) VALUES ('Me recieving :qty potions with :red_ml red_mls :green_ml green_mls :blue_ml blue mls :dark_ml dark mls') RETURNING id"), [{"qty" : potion.quantity, "red_ml" : potion.potion_type[0], "green_ml" : potion.potion_type[1], "blue_ml" : potion.potion_type[2], "dark_ml" : potion.potion_type[3]}]).first()[0]
            connection.execute(sqlalchemy.text("INSERT INTO account_ledger_entries (account_id, account_transaction_id, change, transaction_type) VALUES (:my_account_id, :transaction_id, :red_ml, 'red_ml'), (:my_account_id, :transaction_id, :green_ml, 'green_ml'), (:my_account_id, :transaction_id, :blue_ml, 'blue_ml'), (:my_account_id, :transaction_id, :dark_ml, 'dark_ml')"), [{"my_account_id" : 1, "transaction_id" : transaction_id, "qty" : potion.quantity, "red_ml" : potion.potion_type[0], "green_ml" : potion.potion_type[1], "blue_ml" : potion.potion_type[2], "dark_ml" : potion.potion_type[3]}])


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