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
                transaction_id = connection.execute(sqlalchemy.text("INSERT INTO account_transactions (description) VALUES ('Me paying Barrel salesperson :price for :qty green barrels with :ml mls') RETURNING id"), [{"price" : barrels.price, "qty" : barrels.quantity, "ml" : barrels.ml_per_barrel}]).first()[0]
                connection.execute(sqlalchemy.text("INSERT INTO account_ledger_entries (account_id, account_transaction_id, change, transaction_type) VALUES (:my_account_id, :transaction_id, :gold, 'gold'), (:my_account_id, :transaction_id, :ml, 'green_ml')"), [{"my_account_id" : 1, "transaction_id" : transaction_id, "gold" : - (barrels.quantity * barrels.price), "ml" : (barrels.quantity * barrels.ml_per_barrel)}])
            elif barrels.potion_type == [1, 0, 0, 0]:
                connection.execute(sqlalchemy.text(f"Update {INVENTORY} SET gold = gold - {barrels.quantity * barrels.price}"))
                connection.execute(sqlalchemy.text(f"Update {INVENTORY} SET num_red_ml = num_red_ml + {barrels.quantity * barrels.ml_per_barrel}"))
                transaction_id = connection.execute(sqlalchemy.text("INSERT INTO account_transactions (description) VALUES ('Me paying Barrel salesperson :price for :qty red barrels with :ml mls') RETURNING id"), [{"price" : barrels.price, "qty" : barrels.quantity, "ml" : barrels.ml_per_barrel}]).first()[0]
                connection.execute(sqlalchemy.text("INSERT INTO account_ledger_entries (account_id, account_transaction_id, change, transaction_type) VALUES (:my_account_id, :transaction_id, :gold, 'gold'), (:my_account_id, :transaction_id, :ml, 'red_ml')"), [{"my_account_id" : 1, "transaction_id" : transaction_id, "gold" : - (barrels.quantity * barrels.price), "ml" : (barrels.quantity * barrels.ml_per_barrel)}])
            elif barrels.potion_type == [0, 0, 1, 0]:
                connection.execute(sqlalchemy.text(f"Update {INVENTORY} SET gold = gold - {barrels.quantity * barrels.price}"))
                connection.execute(sqlalchemy.text(f"Update {INVENTORY} SET num_blue_ml = num_blue_ml + {barrels.quantity * barrels.ml_per_barrel}"))
                transaction_id = connection.execute(sqlalchemy.text("INSERT INTO account_transactions (description) VALUES ('Me paying Barrel salesperson :price for :qty blue barrels with :ml mls') RETURNING id"), [{"price" : barrels.price, "qty" : barrels.quantity, "ml" : barrels.ml_per_barrel}]).first()[0]
                connection.execute(sqlalchemy.text("INSERT INTO account_ledger_entries (account_id, account_transaction_id, change, transaction_type) VALUES (:my_account_id, :transaction_id, :gold, 'gold'), (:my_account_id, :transaction_id, :ml, 'blue_ml')"), [{"my_account_id" : 1, "transaction_id" : transaction_id, "gold" : - (barrels.quantity * barrels.price), "ml" : (barrels.quantity * barrels.ml_per_barrel)}])
            elif barrels.potion_type == [0, 0, 0, 1]:
                connection.execute(sqlalchemy.text(f"Update {INVENTORY} SET gold = gold - {barrels.quantity * barrels.price}"))
                connection.execute(sqlalchemy.text(f"Update {INVENTORY} SET num_dark_ml = num_dark_ml + {barrels.quantity * barrels.ml_per_barrel}"))
                transaction_id = connection.execute(sqlalchemy.text("INSERT INTO account_transactions (description) VALUES ('Me paying Barrel salesperson :price for :qty dark barrels with :ml mls') RETURNING id"), [{"price" : barrels.price, "qty" : barrels.quantity, "ml" : barrels.ml_per_barrel}]).first()[0]
                connection.execute(sqlalchemy.text("INSERT INTO account_ledger_entries (account_id, account_transaction_id, change, transaction_type) VALUES (:my_account_id, :transaction_id, :gold, 'gold'), (:my_account_id, :transaction_id, :ml, 'dark_ml')"), [{"my_account_id" : 1, "transaction_id" : transaction_id, "gold" : - (barrels.quantity * barrels.price), "ml" : (barrels.quantity * barrels.ml_per_barrel)}])
            #TODO insert update statement that is general here

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    #TODO make sure ml purchased is within limits
    with db.engine.begin() as connection:
        ml_limit = connection.execute(sqlalchemy.text(f"SELECT ml_capacity FROM {CAPACITY}")).fetchone()[0]
        result =  connection.execute(sqlalchemy.text(f"SELECT num_red_ml, num_green_ml, num_blue_ml, num_dark_ml FROM {INVENTORY}")).fetchone()
        red_ml = result[0]
        green_ml = result[1]
        blue_ml = result[2]
        dark_ml = result[3]
        total_ml = red_ml + green_ml + blue_ml + dark_ml
        result = []
        print(f'result: {result}')
        return result
        print(wholesale_catalog)
        gold_table = connection.execute(sqlalchemy.text(f"SELECT gold FROM {INVENTORY}"))
        for row in gold_table:
            gold = row[0]
        print(f'gold {gold}')
        # if ml_limit // total_ml <= 4:
        #     return result
        # if gold >= 400: 
        #     barrel_type = 1
        #     if gold >= 500: barrel_type = random.randint(1, 2)
        #     if gold >= 600: barrel_type = random.randint(1, 3)
        #     if min(red_ml, green_ml, blue_ml) == green_ml:
        #         barrel_type = 1
        #     elif min(red_ml, green_ml, blue_ml) == blue_ml and gold > 600:
        #         barrel_type = 3
        #     elif min(red_ml, green_ml, blue_ml) == red_ml and gold > 500:
        #         barrel_type = 2
        #     # elif min(red_ml, green_ml, blue_ml) == dark_ml:
        #     #     barrel_type = 4
        #     #TODO create and implement better barrel buying logic
        #     # buy up to 1/4 of max ml for each ml type
        #     # or buy the percentage of ml in all items being bought/sold
        #     for barrel in wholesale_catalog:
        #         total_ml = red_ml + green_ml + blue_ml + dark_ml
        #         qty = gold // barrel.price
        #         qty = min (qty, (ml_limit - total_ml) // barrel.ml_per_barrel, barrel.quantity)

        #         if qty > (ml_limit // barrel.ml_per_barrel)//2:
        #             qty = (ml_limit // barrel.ml_per_barrel)//2
        #         if qty >= 1:
        #             if barrel_type == 1 and barrel.sku == "LARGE_GREEN_BARREL":
        #                 result.append(
        #                     {
        #                         "sku": "LARGE_GREEN_BARREL",
        #                         "quantity": qty
        #                     }
        #                 )
        #                 green_ml += barrel.ml_per_barrel * qty
        #                 gold -= barrel.price * qty
        #                 print(f'gold {gold}')
        #             if barrel_type == 2 and barrel.sku == "LARGE_RED_BARREL":
        #                 result.append(
        #                     {
        #                         "sku": "LARGE_RED_BARREL",
        #                         "quantity": qty
        #                     }
        #                 )
        #                 red_ml += barrel.ml_per_barrel * qty
        #                 gold -= barrel.price * qty
        #                 print(f'gold {gold}')
        #             if barrel_type == 3 and barrel.sku == "LARGE_BLUE_BARREL":
        #                 result.append(
        #                     {
        #                         "sku": "LARGE_BLUE_BARREL",
        #                         "quantity": qty
        #                     }
        #                 )
        #                 blue_ml += barrel.ml_per_barrel * qty
        #                 gold -= barrel.price * qty
        #                 print(f'gold {gold}')
        #             if barrel_type == 4 and barrel.sku == "LARGE_DARK_BARREL":
        #                 result.append(
        #                     {
        #                         "sku": "LARGE_DARK_BARREL",
        #                         "quantity": qty
        #                     }
        #                 )
        #                 dark_ml += barrel.ml_per_barrel * qty
        #                 gold -= barrel.price * qty
        #                 print(f'gold {gold}')

        # if gold >= 250:
        #     if gold >= 300 :
        #         barrel_type = random.randint(1, 3)
        #     else:
        #         if min(red_ml, green_ml, blue_ml) == green_ml:
        #             barrel_type = 1
        #         elif min(red_ml, green_ml, blue_ml) == blue_ml and gold > 300:
        #             barrel_type = 3
        #         elif min(red_ml, green_ml, blue_ml) == red_ml:
        #             barrel_type = 2
        #         # elif min(red_ml, green_ml, blue_ml) == dark_ml:
        #         #     barrel_type = 4
        #     for barrel in wholesale_catalog:
        #         total_ml = red_ml + green_ml + blue_ml + dark_ml
        #         qty = gold // barrel.price
        #         qty = min (qty, (ml_limit - total_ml) // barrel.ml_per_barrel, barrel.quantity)

        #         if qty > (ml_limit // barrel.ml_per_barrel)//2:
        #             qty = (ml_limit // barrel.ml_per_barrel)//2
        #         if qty >= 1:
        #             if barrel_type == 1 and barrel.sku == "MEDIUM_GREEN_BARREL":
        #                 result.append(
        #                     {
        #                         "sku": "MEDIUM_GREEN_BARREL",
        #                         "quantity": qty
        #                     }
        #                 )
        #                 gold -= barrel.price * qty
        #                 print(f'gold {gold}')
        #                 green_ml += barrel.ml_per_barrel * qty
        #             if barrel_type == 2 and barrel.sku == "MEDIUM_RED_BARREL":
        #                 result.append(
        #                     {
        #                         "sku": "MEDIUM_RED_BARREL",
        #                         "quantity": qty
        #                     }
        #                 )
        #                 red_ml += barrel.ml_per_barrel * qty
        #                 gold -= barrel.price * qty
        #                 print(f'gold {gold}')
        #             if barrel_type == 3 and barrel.sku == "MEDIUM_BLUE_BARREL":
        #                 result.append(
        #                     {
        #                         "sku": "MEDIUM_BLUE_BARREL",
        #                         "quantity": qty
        #                     }
        #                 )
        #                 gold -= barrel.price * qty
        #                 print(f'gold {gold}')
        #                 blue_ml += barrel.ml_per_barrel * qty
        #             if barrel_type == 4 and barrel.sku == "MEDIUM_DARK_BARREL":
        #                 result.append(
        #                     {
        #                         "sku": "MEDIUM_DARK_BARREL",
        #                         "quantity": qty
        #                     }
        #                 )
        #                 gold -= barrel.price * qty
        #                 print(f'gold {gold}')
        #                 dark_ml += barrel.ml_per_barrel * qty
        
        # if gold >= 100:
        #     barrel_type = random.randint(1, 2)
        #     if gold >= 120: barrel_type = random.randint(1, 3)
        #     if min(red_ml, green_ml, blue_ml) == green_ml:
        #         barrel_type = 1
        #     elif min(red_ml, green_ml, blue_ml) == blue_ml and gold >= 120:
        #         barrel_type = 3
        #     elif min(red_ml, green_ml, blue_ml) == red_ml:
        #         barrel_type = 2
        #     # elif min(red_ml, green_ml, blue_ml) == dark_ml:
        #     #     barrel_type = 4
        #     for barrel in wholesale_catalog:
        #         total_ml = red_ml + green_ml + blue_ml + dark_ml
        #         qty = gold // barrel.price
        #         qty = min (qty, (ml_limit - total_ml) // barrel.ml_per_barrel, barrel.quantity)
        #         if qty > (ml_limit // barrel.ml_per_barrel)//2:
        #             qty = (ml_limit // barrel.ml_per_barrel)//2
        #         if qty >= 1 and barrel.ml_per_barrel * qty < ml_limit - total_ml:
        #             if barrel_type == 1 and barrel.sku == "SMALL_GREEN_BARREL":
        #                 result.append(
        #                     {
        #                         "sku": "SMALL_GREEN_BARREL",
        #                         "quantity": qty
        #                     }
        #                 )
        #                 gold -= barrel.price * qty
        #                 print(f'gold {gold}')
        #                 green_ml += barrel.ml_per_barrel * qty
        #             if barrel_type == 2 and barrel.sku == "SMALL_RED_BARREL":
        #                 result.append(
        #                     {
        #                         "sku": "SMALL_RED_BARREL",
        #                         "quantity": qty
        #                     }
        #                 )
        #                 gold -= barrel.price * qty
        #                 print(f'gold {gold}')
        #                 red_ml += barrel.ml_per_barrel * qty
        #             if barrel_type == 3 and barrel.sku == "SMALL_BLUE_BARREL":
        #                 result.append(
        #                     {
        #                         "sku": "SMALL_BLUE_BARREL",
        #                         "quantity": qty
        #                     }
        #                 )
        #                 blue_ml += barrel.ml_per_barrel * qty
        #                 gold -= barrel.price * qty
        #                 print(f'gold {gold}')
        #             if barrel_type == 4 and barrel.sku == "SMALL_DARK_BARREL":
        #                 result.append(
        #                     {
        #                         "sku": "SMALL_DARK_BARREL",
        #                         "quantity": qty
        #                     }
        #                 )
        #                 dark_ml += barrel.ml_per_barrel * qty
        #                 gold -= barrel.price * qty
        #                 print(f'gold {gold}')

        #LARGE barrel looping
        loop = False
        dark = False
        for barrel in wholesale_catalog:
            if "LARGE" in barrel.sku:
                loop = True
            if "LARGE_DARK_BARREL" in barrel.sku:
                dark = True
        i = 0
        types = [0,0,0,0]
        while gold >= 400 and loop and total_ml + 10000 <= ml_limit:
            print(f"loop: {i}")
            i += 1
            print(f"min(red_ml, green_ml, blue_ml): {min(red_ml, green_ml, blue_ml)}\nred: {red_ml}\ngreen: {green_ml}\nblue: {blue_ml}\ngold: {gold}\ntypes: {types}")
            if dark_ml < 10000 and gold >= 750 and types[3] < 30:
                types[3] += 1
                gold -= 750
                dark_ml += 10000
            elif min(red_ml, green_ml, blue_ml) == green_ml and gold >= 400 and types[1] < 30:
                types[1] += 1
                gold -= 400
                green_ml += 10000
            elif min(red_ml, green_ml, blue_ml) == blue_ml and gold >= 600 and types[2] < 30:
                types[2] += 1
                gold -= 600
                blue_ml += 10000
            elif min(red_ml, green_ml, blue_ml) == red_ml and gold >= 500 and types[0] < 30:
                types[0] += 1
                gold -= 500
                red_ml += 10000
            else:
                loop = False
            total_ml = green_ml + red_ml + blue_ml + dark_ml
        if types[0] > 0:
            result.append(
                {
                    "sku": "LARGE_RED_BARREL",
                    "quantity": types[0]
                }
            )
        if types[1] > 0:
            result.append(
                {
                    "sku": "LARGE_GREEN_BARREL",
                    "quantity": types[1]
                }
            )
        if types[2] > 0:
            result.append(
                {
                    "sku": "LARGE_BLUE_BARREL",
                    "quantity": types[2]
                }
            )
        if types[3] > 0:
            result.append(
                {
                    "sku": "LARGE_DARK_BARREL",
                    "quantity": types[3]
                }
            )

        #medium barrel looping
        loop = False
        for barrel in wholesale_catalog:
            if "MEDIUM" in barrel.sku:
                loop = True
                print("medium in a barrel sku")
                break
        i = 0
        types = [0,0,0,0]
        while gold >= 250 and loop and total_ml + 2500 <= ml_limit:
            if min(red_ml, green_ml, blue_ml) > ml_limit/16:
                loop = False
            i += 1
            print(f"min(red_ml, green_ml, blue_ml): {min(red_ml, green_ml, blue_ml)}\nred: {red_ml}\ngreen: {green_ml}\nblue: {blue_ml}\ngold: {gold}\ntypes: {types}")
            if min(red_ml, green_ml, blue_ml) == green_ml and gold >= 250 and types[1] < 10:
                types[1] += 1
                gold -= 250
                green_ml += 2500
            elif min(red_ml, green_ml, blue_ml) == blue_ml and gold >= 300 and types[2] < 10:
                types[2] += 1
                gold -= 300
                blue_ml += 2500
            elif min(red_ml, green_ml, blue_ml) == red_ml and gold >= 250 and types[0] < 10:
                types[0] += 1
                gold -= 250
                red_ml += 2500
            else:
                loop = False
            total_ml = green_ml + red_ml + blue_ml + dark_ml
        if types[0] > 0:
            result.append(
                {
                    "sku": "MEDIUM_RED_BARREL",
                    "quantity": types[0]
                }
            )
        if types[1] > 0:
            result.append(
                {
                    "sku": "MEDIUM_GREEN_BARREL",
                    "quantity": types[1]
                }
            )
        if types[2] > 0:
            result.append(
                {
                    "sku": "MEDIUM_BLUE_BARREL",
                    "quantity": types[2]
                }
            )


        #small barrel looping
        loop = False
        for barrel in wholesale_catalog:
            if "SMALL" in barrel.sku:
                loop = True
                print("small in a barrel sku")
                break
        i = 0
        types = [0,0,0,0]
        while gold >= 100 and loop and total_ml + 500 <= ml_limit:
            
            if min(red_ml, green_ml, blue_ml) > ml_limit/16:
                loop = False
            print(f"loop: {i}")
            i += 1
            print(f"min(red_ml, green_ml, blue_ml): {min(red_ml, green_ml, blue_ml)}\nred: {red_ml}\ngreen: {green_ml}\nblue: {blue_ml}\ngold: {gold}\ntypes: {types}")
            if min(red_ml, green_ml, blue_ml) == green_ml and gold >= 100 and types[1] < 10:
                types[1] += 1
                gold -= 100
                green_ml += 500
            elif min(red_ml, green_ml, blue_ml) == blue_ml and gold >= 120 and types[2] < 10:
                types[2] += 1
                gold -= 120
                blue_ml += 500
            elif min(red_ml, green_ml, blue_ml) == red_ml and gold >= 100 and types[0] < 10:
                types[0] += 1
                gold -= 100
                red_ml += 500
            else:
                loop = False
            total_ml = green_ml + red_ml + blue_ml + dark_ml
        if types[0] > 0:
            result.append(
                {
                    "sku": "SMALL_RED_BARREL",
                    "quantity": types[0]
                }
            )
        if types[1] > 0:
            result.append(
                {
                    "sku": "SMALL_GREEN_BARREL",
                    "quantity": types[1]
                }
            )
        if types[2] > 0:
            result.append(
                {
                    "sku": "SMALL_BLUE_BARREL",
                    "quantity": types[2]
                }
            )



    print(f'result: {result}')
    return result
        

