from fastapi import APIRouter
import sqlalchemy
from src import database as db
from db_variables import CARTS, CUSTOMER, INVENTORY, ITEMS

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    with db.engine.begin() as connection:
        green_potions_table = connection.execute(sqlalchemy.text(f"SELECT qty FROM {ITEMS} WHERE green_qty = 100"))
        for row in green_potions_table:
            green_potions = row[0]
        red_potions_table = connection.execute(sqlalchemy.text(f"SELECT qty FROM {ITEMS} WHERE red_qty = 100"))
        for row in red_potions_table:
            red_potions = row[0]
        blue_potions_table = connection.execute(sqlalchemy.text(f"SELECT qty FROM {ITEMS} WHERE blue_qty = 100"))
        for row in blue_potions_table:
            blue_potions = row[0]
        result = []
        potions_avaliable = connection.execute(sqlalchemy.text(f"SELECT * FROM {ITEMS} WHERE  qty > 0"))
        for potions in potions_avaliable:
            result.append(
                {
                    "sku": potions.sku,
                    "name": potions.sku,
                    "quantity": potions.qty,
                    "price": potions.cost,
                    "potion_type": [potions.red_qty, potions.green_qty, potions.blue_qty, potions.dark_qty]
                }
            )
        print(f'green: {green_potions}\nred: {red_potions}\nblue: {blue_potions}')
        return result
