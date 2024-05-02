from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
import sqlalchemy
from src import database as db
from src.api.db_variables import CARTS, CUSTOMER, INVENTORY, ITEMS, CAPACITY


router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/audit")
def get_inventory():
    """ """
    with db.engine.begin() as connection:
        gold_table = connection.execute(sqlalchemy.text(f"SELECT gold FROM {INVENTORY}"))
        for row in gold_table:
            gold = row[0]
        potions = connection.execute(sqlalchemy.text(f"SELECT num_potions FROM {INVENTORY}")).fetchone()[0]
        red_ml = connection.execute(sqlalchemy.text(f"SELECT num_red_ml FROM {INVENTORY}")).fetchone()[0]
        green_ml = connection.execute(sqlalchemy.text(f"SELECT num_green_ml FROM {INVENTORY}")).fetchone()[0]
        blue_ml = connection.execute(sqlalchemy.text(f"SELECT num_blue_ml FROM {INVENTORY}")).fetchone()[0]
        dark_ml = connection.execute(sqlalchemy.text(f"SELECT num_dark_ml FROM {INVENTORY}")).fetchone()[0]
        total_ml = red_ml + green_ml + blue_ml + dark_ml

        my_account = connection.execute(sqlalchemy.text("SELECT gold, ml, potions FROM accounts WHERE name = 'me' ")).fetchone()
        gold = connection.execute(sqlalchemy.text('''SELECT COALESCE(SUM(change), 0) AS balance
                                                FROM account_ledger_entries
                                                WHERE account_id = :my_account_id
                                                AND transaction_type = 'gold' '''), [{"my_account_id" : 1}]).fetchone()[0] + my_account.gold
        potions = connection.execute(sqlalchemy.text('''SELECT COALESCE(SUM(change), 0) AS balance
                                                FROM account_ledger_entries
                                                WHERE account_id = :my_account_id
                                                AND transaction_type = 'potion' '''), [{"my_account_id" : 1}]).fetchone()[0] + my_account.potions
        total_ml = connection.execute(sqlalchemy.text('''SELECT COALESCE(SUM(change), 0) AS balance
                                                FROM account_ledger_entries
                                                WHERE account_id = :my_account_id
                                                AND transaction_type = 'red_ml'
                                                OR transaction_type = 'green_ml'
                                                OR transaction_type = 'blue_ml'
                                                OR transaction_type = 'dark_ml' '''), [{"my_account_id" : 1}]).fetchone()[0] + my_account.ml
        print(f'potions: {potions}\n ml: {my_account.ml}\ngold: {gold}')
    return {"number_of_potions": potions, "ml_in_barrels": total_ml, "gold": gold}

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """
    with db.engine.begin() as connection:
        gold = connection.execute(sqlalchemy.text(f"SELECT gold FROM {INVENTORY}")).fetchone()[0]
        current_potion_capacity = connection.execute(sqlalchemy.text(f"SELECT potion_capacity FROM {CAPACITY}")).fetchone()[0] // 50
        current_ml_capacity = connection.execute(sqlalchemy.text(f"SELECT ml_capacity FROM {CAPACITY}")).fetchone()[0] // 10000
        potion_capacity = 0
        ml_capacity = 0
        if gold >= 2100:
            potion_capacity = 1
            ml_capacity = 1
        if gold >= 1100:
            if current_ml_capacity >= current_potion_capacity:
                potion_capacity = 1
            else:
                ml_capacity = 1
        
        return {
            "potion_capacity": potion_capacity,
            "ml_capacity": ml_capacity
            }

class CapacityPurchase(BaseModel):
    potion_capacity: int
    ml_capacity: int

# Gets called once a day
@router.post("/deliver/{order_id}")
def deliver_capacity_plan(capacity_purchase : CapacityPurchase, order_id: int):
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(f"Update {CAPACITY} SET ml_capacity = ml_capacity + {10000 * capacity_purchase.ml_capacity}"))
        connection.execute(sqlalchemy.text(f"Update {CAPACITY} SET potion_capacity = potion_capacity + {50 * capacity_purchase.potion_capacity}"))
        connection.execute(sqlalchemy.text(f"Update {INVENTORY} SET gold = gold - {1000 * (capacity_purchase.ml_capacity + capacity_purchase.potion_capacity)}"))

    return "OK"