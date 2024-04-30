from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum
import sqlalchemy
from src import database as db
from src.api.db_variables import CARTS, CUSTOMER, INVENTORY, ITEMS



router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """

    return {
        "previous": "",
        "next": "",
        "results": [
            {
                "line_item_id": 1,
                "item_sku": "1 oblivion potion",
                "customer_name": "Scaramouche",
                "line_item_total": 50,
                "timestamp": "2021-01-01T00:00:00Z",
            }
        ],
    }


class Customer(BaseModel):
    customer_name: str
    character_class: str
    level: int

@router.post("/visits/{visit_id}")
def post_visits(visit_id: int, customers: list[Customer]):
    """
    Which customers visited the shop today?
    """
    print(f"customers::\n{customers}")

    return "OK"


@router.post("/")
def create_cart(new_cart: Customer):
    """ """
    with db.engine.begin() as connection:
        id = connection.execute(sqlalchemy.text(f"INSERT INTO {CUSTOMER} (customer_name, character_class, level) VALUES ('{new_cart.customer_name}', '{new_cart.character_class}', {new_cart.level}) RETURNING id")).fetchone()[0]
        return {"cart_id": id}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    with db.engine.begin() as connection:
        item_id = connection.execute(sqlalchemy.text(f"SELECT id FROM {ITEMS} WHERE sku = '{item_sku}'")).fetchone()[0]
        connection.execute(sqlalchemy.text(f"INSERT INTO {CARTS} (id, character_id, item_qty, item_id) VALUES ({cart_id}, {cart_id}, {cart_item.quantity}, '{item_id}')"))
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    #TODO update database based on what was sold
    with db.engine.begin() as connection:
        potions_bought = 0
        gold_paid = 0
        cart_items = connection.execute(sqlalchemy.text(f"SELECT * FROM {CARTS} WHERE id = {cart_id}"))
        for item in cart_items:
            item_qty = item.item_qty
            item_id = item.item_id
            cost = connection.execute(sqlalchemy.text(f"SELECT cost FROM {ITEMS} WHERE id = {item_id}")).fetchone()[0]
            gold_paid += cost * item_qty
            potions_bought += item_qty
            connection.execute(sqlalchemy.text(f"UPDATE {INVENTORY} SET gold = gold + {cost * item_qty}"))
            connection.execute(sqlalchemy.text(f"UPDATE {ITEMS} SET qty = qty - {item_qty} WHERE id = {item_id}"))
            connection.execute(sqlalchemy.text(f"UPDATE {INVENTORY} SET num_potions = num_potions - {item_qty}"))
            print(f"item_id: {item_id}, item qty: {item_qty}")
        return {"total_potions_bought": potions_bought, "total_gold_paid": gold_paid}