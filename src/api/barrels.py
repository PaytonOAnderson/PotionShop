from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from src.api.db_variables import CARTS, CUSTOMER, INVENTORY, ITEMS, CAPACITY
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
            elif barrels.potion_type == [1, 0, 0, 0]:
                connection.execute(sqlalchemy.text(f"Update {INVENTORY} SET gold = gold - {barrels.price}"))
                connection.execute(sqlalchemy.text(f"Update {INVENTORY} SET num_red_ml = num_red_ml + {barrels.quantity * barrels.ml_per_barrel}"))
            elif barrels.potion_type == [0, 0, 1, 0]:
                connection.execute(sqlalchemy.text(f"Update {INVENTORY} SET gold = gold - {barrels.price}"))
                connection.execute(sqlalchemy.text(f"Update {INVENTORY} SET num_blue_ml = num_blue_ml + {barrels.quantity * barrels.ml_per_barrel}"))
            elif barrels.potion_type == [0, 0, 0, 1]:
                connection.execute(sqlalchemy.text(f"Update {INVENTORY} SET gold = gold - {barrels.price}"))
                connection.execute(sqlalchemy.text(f"Update {INVENTORY} SET num_dark_ml = num_dark_ml + {barrels.quantity * barrels.ml_per_barrel}"))

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    #TODO make sure ml purchased is within limits
    with db.engine.begin() as connection:
        ml_limit = connection.execute(sqlalchemy.text(f"SELECT ml_capacity FROM {CAPACITY}")).fetchone()[0]
        red_ml = connection.execute(sqlalchemy.text(f"SELECT num_red_ml FROM {INVENTORY}")).fetchone()[0]
        green_ml = connection.execute(sqlalchemy.text(f"SELECT num_green_ml FROM {INVENTORY}")).fetchone()[0]
        blue_ml = connection.execute(sqlalchemy.text(f"SELECT num_blue_ml FROM {INVENTORY}")).fetchone()[0]
        dark_ml = connection.execute(sqlalchemy.text(f"SELECT num_dark_ml FROM {INVENTORY}")).fetchone()[0]
        total_ml = red_ml + green_ml + blue_ml + dark_ml
        result = []
        print(wholesale_catalog)
        gold_table = connection.execute(sqlalchemy.text(f"SELECT gold FROM {INVENTORY}"))
        for row in gold_table:
            gold = row[0]
        print(f'result {gold}')
        if ml_limit // total_ml <= 4:
            return result
        if gold >= 400: 
            barrel_type = 1
            if gold >= 500: barrel_type = random.randint(1, 2)
            if gold >= 600: barrel_type = random.randint(1, 3)
            if min(red_ml, green_ml, blue_ml, dark_ml) == green_ml:
                barrel_type = 1
            elif min(red_ml, green_ml, blue_ml, dark_ml) == red_ml:
                barrel_type = 2
            elif min(red_ml, green_ml, blue_ml, dark_ml) == blue_ml:
                barrel_type = 3
            # elif min(red_ml, green_ml, blue_ml, dark_ml) == dark_ml:
            #     barrel_type = 4
            #TODO create and implement better barrel buying logic
            # buy up to 1/4 of max ml for each ml type
            # or buy the percentage of ml in all items being bought/sold
            for barrel in wholesale_catalog:
                qty = gold // barrel.price
                if qty > barrel.quantity: qty = barrel.quantity
                if qty >= 1 and barrel.ml_per_barrel < ml_limit - total_ml:
                    if barrel_type == 1 and barrel.sku == "LARGE_GREEN_BARREL":
                        result.append(
                            {
                                "sku": "LARGE_GREEN_BARREL",
                                "quantity": qty
                            }
                        )
                    if barrel_type == 2 and barrel.sku == "LARGE_RED_BARREL":
                        result.append(
                            {
                                "sku": "LARGE_RED_BARREL",
                                "quantity": qty
                            }
                        )
                    if barrel_type == 3 and barrel.sku == "LARGE_BLUE_BARREL":
                        result.append(
                            {
                                "sku": "LARGE_BLUE_BARREL",
                                "quantity": qty
                            }
                        )

        if gold >= 250:
            if gold >= 300 :
                barrel_type = random.randint(1, 3)
            else: barrel_type = random.randint(1, 2)
            if min(red_ml, green_ml, blue_ml, dark_ml) == green_ml:
                barrel_type = 1
            elif min(red_ml, green_ml, blue_ml, dark_ml) == red_ml:
                barrel_type = 2
            elif min(red_ml, green_ml, blue_ml, dark_ml) == blue_ml:
                barrel_type = 3
            # elif min(red_ml, green_ml, blue_ml, dark_ml) == dark_ml:
            #     barrel_type = 4
            for barrel in wholesale_catalog:
                qty = gold // barrel.price
                if qty > barrel.quantity: qty = barrel.quantity
                if qty >= 1 and barrel.ml_per_barrel < ml_limit - total_ml:
                    if barrel_type == 1 and barrel.sku == "MEDIUM_GREEN_BARREL":
                        result.append(
                            {
                                "sku": "MEDIUM_GREEN_BARREL",
                                "quantity": qty
                            }
                        )
                    if barrel_type == 2 and barrel.sku == "MEDIUM_RED_BARREL":
                        result.append(
                            {
                                "sku": "MEDIUM_RED_BARREL",
                                "quantity": qty
                            }
                        )
                    if barrel_type == 3 and barrel.sku == "MEDIUM_BLUE_BARREL":
                        result.append(
                            {
                                "sku": "MEDIUM_BLUE_BARREL",
                                "quantity": qty
                            }
                        )
        if gold >= 100:
            barrel_type = random.randint(1, 2)
            if gold >= 120: barrel_type = random.randint(1, 3)
            if min(red_ml, green_ml, blue_ml, dark_ml) == green_ml:
                barrel_type = 1
            elif min(red_ml, green_ml, blue_ml, dark_ml) == red_ml:
                barrel_type = 2
            elif min(red_ml, green_ml, blue_ml, dark_ml) == blue_ml:
                barrel_type = 3
            # elif min(red_ml, green_ml, blue_ml, dark_ml) == dark_ml:
            #     barrel_type = 4
            for barrel in wholesale_catalog:
                qty = gold // barrel.price
                if qty > barrel.quantity: qty = barrel.quantity
                if qty >= 1 and barrel.ml_per_barrel < ml_limit - total_ml:
                    if barrel_type == 1 and barrel.sku == "SMALL_GREEN_BARREL":
                        result.append(
                            {
                                "sku": "SMALL_GREEN_BARREL",
                                "quantity": qty
                            }
                        )
                    if barrel_type == 2 and barrel.sku == "SMALL_RED_BARREL":
                        result.append(
                            {
                                "sku": "SMALL_RED_BARREL",
                                "quantity": qty
                            }
                        )
                    if barrel_type == 3 and barrel.sku == "SMALL_BLUE_BARREL":
                        result.append(
                            {
                                "sku": "SMALL_BLUE_BARREL",
                                "quantity": qty
                            }
                        )
    return result
        

