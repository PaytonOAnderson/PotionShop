from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    with db.engine.begin() as connection:
    
        print(wholesale_catalog)
        gold_table = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory WHERE gold >= 0"))
        for row in gold_table:
            gold = row[0]
        print(f'result {gold}')
        green_potions_table = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))
        for row in green_potions_table:
            green_potions = row[0]
        if green_potions < 10:
            for barrel in wholesale_catalog:
                if barrel.sku == "SMALL_GREEN_BARREL" and gold >= barrel.price:
                    return [
                        {
                            "sku": "SMALL_GREEN_BARREL",
                            "quantity": 1,
                        }
                    ]
    return [
        {
            "sku": "BARREL",
            "quantity": 1,
        }
    ]
        

