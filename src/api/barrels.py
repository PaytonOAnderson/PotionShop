from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from db_variables import CARTS, CUSTOMER, INVENTORY, ITEMS
import random

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
    with db.engine.begin() as connection:
        for barrels in barrels_delivered:
            if barrels.potion_type == [0, 1, 0, 0]:
                connection.execute(sqlalchemy.text(f"Update {INVENTORY} SET gold = gold - {barrels.quantity * barrels.price}"))
                connection.execute(sqlalchemy.text(f"Update {INVENTORY} SET num_green_ml = num_green_ml + {barrels.quantity * barrels.ml_per_barrel}"))
            if barrels.potion_type == [1, 0, 0, 0]:
                connection.execute(sqlalchemy.text(f"Update {INVENTORY} SET gold = gold - {barrels.price}"))
                connection.execute(sqlalchemy.text(f"Update {INVENTORY} SET num_red_ml = num_red_ml + {barrels.quantity * barrels.ml_per_barrel}"))
            if barrels.potion_type == [0, 0, 1, 0]:
                connection.execute(sqlalchemy.text(f"Update {INVENTORY} SET gold = gold - {barrels.price}"))
                connection.execute(sqlalchemy.text(f"Update {INVENTORY} SET num_blue_ml = num_blue_ml + {barrels.quantity * barrels.ml_per_barrel}"))

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    #TODO make sure ml purchased is within limits
    with db.engine.begin() as connection:
        result = []
        print(wholesale_catalog)
        gold_table = connection.execute(sqlalchemy.text(f"SELECT gold FROM {INVENTORY}"))
        for row in gold_table:
            gold = row[0]
        print(f'result {gold}')
        if gold >= 400: 
            random_num = 1
            if gold >= 500: random_num = random.randint(1, 2)
            if gold >= 600: random_num = random.randint(1, 3)
            for barrel in wholesale_catalog:
                qty = gold // barrel.price
                if qty > barrel.quantity: qty = barrel.quantity
                if random_num == 1 and barrel.sku == "LARGE_GREEN_BARREL" and gold >= barrel.price:
                    return [
                        {
                            "sku": "LARGE_GREEN_BARREL",
                            "quantity": qty
                        }
                    ]
                if random_num == 2 and barrel.sku == "LARGE_RED_BARREL" and gold >= barrel.price:
                    return [
                        {
                            "sku": "LARGE_RED_BARREL",
                            "quantity": qty
                        }
                    ]
                if random_num == 3 and barrel.sku == "LARGE_BLUE_BARREL" and gold >= barrel.price:
                    return [
                        {
                            "sku": "LARGE_BLUE_BARREL",
                            "quantity": qty
                        }
                    ]

        if gold >= 250:
            if gold >= 300 :
                random_num = random.randint(1, 3)
            else: random_num = random.randint(1, 2)
            for barrel in wholesale_catalog:
                if random_num == 1 and barrel.sku == "MEDIUM_GREEN_BARREL" and gold >= barrel.price:
                    return [
                        {
                            "sku": "MEDIUM_GREEN_BARREL",
                            "quantity": 1
                        }
                    ]
                if random_num == 2 and barrel.sku == "MEDIUM_RED_BARREL" and gold >= barrel.price:
                    return [
                        {
                            "sku": "MEDIUM_RED_BARREL",
                            "quantity": 1
                        }
                    ]
                if random_num == 3 and barrel.sku == "MEDIUM_BLUE_BARREL" and gold >= barrel.price:
                    return [
                        {
                            "sku": "MEDIUM_BLUE_BARREL",
                            "quantity": 1
                        }
                    ]
        if gold >= 100:
            random_num = random.randint(1, 2)
            if gold >= 120: random_num = random.randint(1, 3)
            for barrel in wholesale_catalog:
                if random_num == 1 and barrel.sku == "SMALL_GREEN_BARREL" and gold >= barrel.price:
                    return [
                        {
                            "sku": "SMALL_GREEN_BARREL",
                            "quantity": 1
                        }
                    ]
                if random_num == 2 and barrel.sku == "SMALL_RED_BARREL" and gold >= barrel.price:
                    return [
                        {
                            "sku": "SMALL_RED_BARREL",
                            "quantity": 1
                        }
                    ]
                if random_num == 3 and barrel.sku == "SMALL_BLUE_BARREL" and gold >= barrel.price:
                    return [
                        {
                            "sku": "SMALL_BLUE_BARREL",
                            "quantity": 1
                        }
                    ]
    return result
        

