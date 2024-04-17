from fastapi import APIRouter
import sqlalchemy
from src import database as db
from src.api.db_variables import CARTS, CUSTOMER, INVENTORY, ITEMS

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    with db.engine.begin() as connection:
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
        return result
