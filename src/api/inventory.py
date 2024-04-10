from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/audit")
def get_inventory():
    """ """
    with db.engine.begin() as connection:
        gold_table = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))
        for row in gold_table:
            gold = row[0]
        green_potions_table = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))
        for row in green_potions_table:
            green_potions = row[0]
        green_ml_table = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory"))
        for row in green_ml_table:
            green_ml = row[0]
        print(f'potions: {green_potions}\n ml: {green_ml}\ngold: {gold}')
    return {"number_of_potions": green_potions, "ml_in_barrels": green_ml, "gold": gold}

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return {
        "potion_capacity": 0,
        "ml_capacity": 0
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

    return "OK"