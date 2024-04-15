from fastapi import APIRouter
import sqlalchemy
from src import database as db
from src.api.inventory import INVENTORY

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    with db.engine.begin() as connection:
        green_potions_table = connection.execute(sqlalchemy.text(f"SELECT num_green_potions FROM {INVENTORY}"))
        for row in green_potions_table:
            green_potions = row[0]
        red_potions_table = connection.execute(sqlalchemy.text(f"SELECT num_red_potions FROM {INVENTORY}"))
        for row in red_potions_table:
            red_potions = row[0]
        blue_potions_table = connection.execute(sqlalchemy.text(f"SELECT num_blue_potions FROM {INVENTORY}"))
        for row in blue_potions_table:
            blue_potions = row[0]
        result = []
        print(f'green: {green_potions}\nred: {red_potions}\nblue: {blue_potions}')
        if green_potions > 0:
            result.append([
                    {
                        "sku": "GREEN_POTION_0",
                        "name": "green potion",
                        "quantity": green_potions,
                        "price": 25,
                        "potion_type": [0, 100, 0, 0]
                    }
                ]
            )
        if red_potions > 0:
            result.append([
                    {
                        "sku": "RED_POTION_0",
                        "name": "red potion",
                        "quantity": red_potions,
                        "price": 25,
                        "potion_type": [100, 0, 0, 0]
                    }
                ]
            )
        if blue_potions > 0:
            result.append([
                    {
                        "sku": "BLUE_POTION_0",
                        "name": "blue potion",
                        "quantity": blue_potions,
                        "price": 30,
                        "potion_type": [100, 0, 0, 0]
                    }
                ]
            )
        return result
