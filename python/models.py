from datetime import date
import sqlite3 as sql
import os
from hashlib import md5
from validators import check_password_format, check_email_format

DATABASE_FILENAME = "mydb"


CREATE_TABLE_QUERIES = [
    """

        CREATE TABLE IF NOT EXISTS user (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            username           TEXT NOT NULL,
            email              TEXT UNIQUE NOT NULL,
            password           TEXT NOT NULL,
            date_joined        DATE NOT NULL,
            last_logged_in     DATE NULL,
            is_admin           INTEGER DEFAULT 0
        );
    """,
    """
        CREATE TABLE IF NOT EXISTS item (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name          TEXT UNIQUE NOT NULL,
            unit_price         REAL NOT NULL,
            items_in_stock     INTEGER NOT NULL
        );
    """,
    """
        CREATE TABLE IF NOT EXISTS `order` (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            date_ordered       DATE NOT NULL,
            item_id            INTEGER NOT NULL,
            number_ordered     INTEGER NOT NULL,
            user_id            INTEGER NOT NULL,
            date_completed     DATE DEFAULT NULL,
            
            FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE RESTRICT,
            FOREIGN KEY (item_id) REFERENCES item(id) ON DELETE RESTRICT
        );
    """
]


def execute_query(query: str) -> int:
    db = sql.connect(os.path.join(os.path.abspath(os.path.dirname(__file__)), f"{DATABASE_FILENAME}.sqlite3"))
    cursor = db.cursor()
    
    cursor.execute(query)
    lastrowid = cursor.lastrowid
    
    db.commit()
    cursor.close()
    db.close()
    
    return lastrowid
    
    
def fetch_one_query(query: str):
    db = sql.connect(os.path.join(os.path.abspath(os.path.dirname(__file__)), f"{DATABASE_FILENAME}.sqlite3"))
    cursor = db.cursor()
    
    cursor.execute(query)
    
    result = cursor.fetchone()
    
    cursor.close()
    db.close()
    return result


def fetch_all_query(query: str):
    db = sql.connect(os.path.join(os.path.abspath(os.path.dirname(__file__)), f"{DATABASE_FILENAME}.sqlite3"))
    cursor = db.cursor()
    
    cursor.execute(query)
    
    result = cursor.fetchall()
    
    cursor.close()
    db.close()
    return result
    


def create_tables():
    global CREATE_TABLE_QUERIES
    
    db = sql.connect(os.path.join(os.path.abspath(os.path.dirname(__file__)), f"{DATABASE_FILENAME}.sqlite3"))
    cursor = db.cursor()
    
    for each_query in CREATE_TABLE_QUERIES:
        cursor.execute(each_query)
        
    db.commit()
    cursor.close()
    db.close()
    
    
class BaseModel:
    class DoesNotExist(Exception):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)


class User(BaseModel):
    __id: int
    __username: str
    __email: str
    __password: str
    __date_joined: date
    __last_logged_in: date = None
    is_admin: bool = False

    
    def __init__(self, username: str, email: str):
        self.__username = username
        self.__email = check_email_format(email)
        
    def get_id(self) -> int:
        return self.__id
        
    def get_username(self) -> str:
        return self.__username
    
    def set_username(self, username: str) -> str:
        self.__username = username
        
    def get_email(self) -> str:
        return self.__email
    
    def set_email(self, email: str):
        self.__email = check_email_format(email)
        
    def check_password(self, password: str) -> bool:
        return md5(password.encode("utf-8")).hexdigest() == self.__password
    
    def set_password(self, password: str):
        self.__password = md5(check_password_format(password).encode("utf-8")).hexdigest()
        
    def get_date_joined(self) -> date:
        return self.__date_joined
    
    def set_date_joined(self, date_joined: date):
        self.__date_joined = date_joined
        
    def save_new(self):
        
        self.__date_joined = date.today()

        SAVE_QUERY = f"""
            INSERT INTO user (
                username,
                email,
                password,
                date_joined,
                is_admin
            )
            VALUES (
                "{self.__username}",
                "{self.__email}",
                "{self.__password}",
                "{str(self.__date_joined)}",
                {int(self.is_admin)}
            );
        """

        self.__id = execute_query(SAVE_QUERY)
        
    def update(self):
        UPDATE_QUERY = f"""
        UPDATE user
        SET
            username = "{self.__username}",
            email = "{self.__email}",
            password = "{self.__password}",
            last_logged_in = "{str(self.__last_logged_in)}",
            is_admin = {int(self.is_admin)}
        WHERE
            id = {self.__id}
        ;
        """
        
        execute_query(UPDATE_QUERY)
        
    def load_by_email(email: str) -> 'User':
        FETCH_QUERY = f"""
            SELECT * FROM user WHERE email = "{check_email_format(email)}"
        """
        
        db = sql.connect(os.path.join(os.path.abspath(os.path.dirname(__file__)), f"{DATABASE_FILENAME}.sqlite3"))
        cursor = db.cursor()
        cursor.execute(FETCH_QUERY)
        
        dbrow = cursor.fetchone()
        
        if dbrow is None:
            raise User.DoesNotExist("User with given email does not exist")
        
        load_user = User(dbrow[1], dbrow[2])
        load_user.__id = dbrow[0]
        load_user.__password = dbrow[3]
        load_user.__date_joined = date(*map(int, dbrow[4].split("-")))
        load_user.__last_logged_in = date(*map(int, dbrow[5].split("-"))) if dbrow[5] is not None else None
        load_user.is_admin = bool(dbrow[6])
        
        return load_user
    
    def load_by_id(id: int) -> 'User':
        FETCH_QUERY = f"""
            SELECT * FROM user WHERE id = {id}
        """
        
        db = sql.connect(os.path.join(os.path.abspath(os.path.dirname(__file__)), f"{DATABASE_FILENAME}.sqlite3"))
        cursor = db.cursor()
        cursor.execute(FETCH_QUERY)
        
        dbrow = cursor.fetchone()
        
        if dbrow is None:
            raise User.DoesNotExist("User with given ID does not exist")
        
        load_user = User(dbrow[1], dbrow[2])
        load_user.__id = dbrow[0]
        load_user.__password = dbrow[3]
        load_user.__date_joined = date(*map(int, dbrow[4].split("-")))
        load_user.__last_logged_in = date(*map(int, dbrow[5].split("-"))) if dbrow[5] is not None else None
        load_user.is_admin = bool(dbrow[6])
        
        return load_user
    
    def load_all() -> list['User']:
        results = fetch_all_query("SELECT * FROM user")
        
        all_users: list[User] = list()
        
        for each_result in results:
            user = User(each_result[1], each_result[2])
            user.__id = each_result[0]
            user.__password = each_result[3]
            user.__date_joined = date(*tuple(map(int, each_result[4].split("-"))))
            user.__last_logged_in = date(*tuple(map(int, each_result[5].split("-"))))
            user.is_admin = bool(each_result[6])
            
            all_users.append(user)
            
        return all_users
            
    
    def get_date_joined(self) -> date:
        return self.__date_joined
    
    def get_last_logged_in(self) -> date:
        return self.__last_logged_in
    
    def set_last_logged_in(self, last_logged_in: date):
        self.__last_logged_in = last_logged_in
    
    def __str__(self) -> str:
        return self.__username
    
    
class Item(BaseModel):
    __id: int
    __item_name: str
    __unit_price: float
    __items_in_stock: int
    
    def __init__(self, item_name: str, unit_price: float, items_in_stock: int):
        self.__item_name = item_name
        self.__unit_price = unit_price
        self.__items_in_stock = items_in_stock
        
    def get_id(self) -> int:
        return self.__id
        
    def get_item_name(self) -> str:
        return self.__item_name
    
    def set_item_name(self, item_name: str):
        self.__item_name = item_name
        
    def get_unit_price(self) -> float:
        return self.__unit_price
    
    def set_unit_price(self, unit_price: float):
        self.__unit_price = unit_price
        
    def get_items_in_stock(self) -> int:
        return self.__items_in_stock
    
    def set_items_in_stock(self, items_in_stock: int):
        self.__items_in_stock = items_in_stock
        
    def load_by_item_name(item_name: str) -> 'Item':
        select_query = f"SELECT * FROM item WHERE item_name = \"{item_name}\";"
        dbrow = fetch_one_query(select_query)
        
        if dbrow:
            loaded_item = Item(*dbrow[1:])
            loaded_item.__id = dbrow[0]
            
            return loaded_item
        else:
            raise Item.DoesNotExist("Item with given name does not exist")
        
    def load_all() -> list['Item']:
        results = fetch_all_query("SELECT * FROM item")
        
        all_items = list()
        for each_result in results:
            loaded_item = Item(*each_result[1:])
            loaded_item.__id = each_result[0]
            
            all_items.append(loaded_item)
            
        return all_items
    
    def load_by_id(id: int) -> 'Item':
        result = fetch_one_query(f"SELECT * FROM `item` WHERE `id` = {id}")
        
        if result:
            item = Item(result[1], result[2], result[3])
            item.__id = result[0]
            
            return item
        else:
            raise Item.DoesNotExist("Item with given ID does not exist")
        
    def save_new(self):

        SAVE_QUERY = f"""
            INSERT INTO item (
                item_name,
                unit_price,
                items_in_stock
            )
            VALUES (
                "{self.__item_name}",
                {self.__unit_price},
                {self.__items_in_stock}
            );
        """

        self.__id = execute_query(SAVE_QUERY)
        
    def update(self):
        UPDATE_QUERY = f"""
        UPDATE item
        SET
            item_name = "{self.__item_name}",
            unit_price = {self.__unit_price},
            items_in_stock = {self.__items_in_stock}
        WHERE
            id = {self.__id}
        ;
        """
        
        execute_query(UPDATE_QUERY)
        
    def delete(self):
        DELETE_QUERY = f"DELETE FROM item WHERE id={self.__id}"
        
        execute_query(DELETE_QUERY)
        
    def __str__(self) -> str:
        return f"<Item: {self.__id}, {self.__item_name}, {self.__unit_price}, {self.__items_in_stock}>"
        
    def __repr__(self) -> str:
        return str(self)
        

if __name__ == "__main__":
    print(Item.load_all())


class ShoppingCartItem:
    __item: Item
    __quantity: int

    def __init__(self, item: Item, quantity: int):
        self.__item = item
        self.__quantity = quantity

    def get_item(self) -> Item:
        return self.__item

    def get_quantity(self) -> int:
        return self.__quantity

    def set_quantity(self, quantity: int):
        self.__quantity = quantity

    def calculate_total_price(self) -> float:
        return self.__item.get_unit_price() * self.__quantity

    def __str__(self) -> str:
        return f"<ShoppingCartItem: item={self.__item}, quantity={self.__quantity}>"

    def __repr__(self) -> str:
        return str(self)


class ShoppingCart:
    __cart_items: list[ShoppingCartItem]
    __user: User

    def __init__(self, user: User):
        self.__user = user
        self.__cart_items = list()

    def find_item_by_id(self, id: int) -> ShoppingCartItem | None:
        for each_item in self.__cart_items:
            if each_item.get_item().get_id() == id:
                return each_item
        return None

    def update_item(self, item: Item, quantity: int):
        existing_item = self.find_item_by_id(item.get_id())

        if existing_item is None:
            new_item = ShoppingCartItem(item, quantity)
            self.__cart_items.append(new_item)
        else:
            existing_item.set_quantity(quantity)

    def remove_item(self, cart_item: ShoppingCartItem):
        if cart_item in self.__cart_items:
            self.__cart_items.remove(cart_item)

    def get_user(self) -> User:
        return self.__user

    def get_cart_items(self) -> list[ShoppingCartItem]:
        return list(self.__cart_items)

    def calculate_overall_total(self) -> float:
        return sum((x.calculate_total_price() for x in self.__cart_items))

    def count_items(self) -> int:
        return len(self.__cart_items)

    def __str__(self) -> str:
        return f"<ShoppingCart__Items: {self.__cart_items}>"

    def __repr__(self) -> str:
        return str(self)
    
    
class Order(BaseModel):
    __id: int = None
    __item_id: int = None
    __item_instance: Item = None
    __number_ordered: int = None
    __user_id: int = None
    __user_instance: User = None
    __date_ordered: date = None
    __date_completed: date = None
    
    def __init__(self):
        super().__init__()

    def from_cart_item(self, cart_item: ShoppingCartItem, user: User, date_ordered: date=None):
        self.__item_id = cart_item.get_item().get_id()
        self.__number_ordered = cart_item.get_quantity()
        self.__user_id = user.get_id()
        self.__date_ordered = date_ordered if date_ordered is not None else date.today()
        
    def save_new(self):

        SAVE_QUERY = f"""
            INSERT INTO `order` (
                item_id,
                number_ordered,
                user_id,
                date_ordered
            )
            VALUES (
                "{self.__item_id}",
                {self.__number_ordered},
                {self.__user_id},
                "{str(self.__date_ordered)}"
            );
        """

        self.__id = execute_query(SAVE_QUERY)
        
    def load_orders() -> list['Order']:
        
        
        pending_orders: list[Order] = list()
        completed_orders: list[Order] = list()
        
        orders: list[Order] = list()
        
        date_ordered: str
        date_completed: str
        
        rows = fetch_all_query("SELECT DISTINCT `order`.`date_ordered`, `user`.`id`, `order`.`date_completed` FROM `order`, `user` WHERE `order`.`user_id` = `user`.`id` AND `order`.`date_completed` IS NULL;")
        print("pending_order_rows:", rows)
        
        for each_row in rows:
            new_order = Order()
            date_ordered, new_order.__user_id, date_completed = each_row
            
            new_order.__date_ordered = date(*tuple(map(int, date_ordered.split("-"))))
            new_order.__date_completed = date(*tuple(map(int, date_completed.split("-")))) if date_completed else None
            
            pending_orders.append(new_order)
            
        pending_orders = sorted(pending_orders, key=lambda x: x.__date_ordered, reverse=True)
        print("pending_orders:", pending_orders)
            
        rows = fetch_all_query("SELECT DISTINCT `order`.`date_ordered`, `user`.`id`, `order`.`date_completed` FROM `order`, `user` WHERE `order`.`user_id` = `user`.`id` AND `order`.`date_completed` NOT NULL;")
        print("completed_order_rows:", rows)
        for each_row in rows:
            new_order = Order()
            date_ordered, new_order.__user_id, date_completed = each_row
            
            new_order.__date_ordered = date(*tuple(map(int, date_ordered.split("-"))))
            new_order.__date_completed = date(*tuple(map(int, date_completed.split("-")))) if date_completed else None
            
            completed_orders.append(new_order)
        
        completed_orders = sorted(completed_orders, key=lambda x: x.__date_ordered, reverse=True)
        print("completed_orders:", completed_orders)
        orders = list(pending_orders) + list(completed_orders)
            
        return orders
    
    def get_orders(date_ordered: date, ordered_by: User, pending: bool) -> list['Order']:
        query = f"SELECT * FROM `order` WHERE `order`.`date_ordered` = \"{date_ordered}\" AND `order`.`user_id` = {ordered_by.get_id()} AND `order`.`date_completed` {'IS' if pending else 'NOT'} NULL;"
        print("query:", query)
        rows = fetch_all_query(query)
        
        dateOrdered: str
        date_completed: str
        
        orders: list[Order] = list()
        
        for each_row in rows:
            order = Order()
            
            order.__id, dateOrdered, order.__item_id, order.__number_ordered, order.__user_id, date_completed = each_row
            
            order.__date_ordered = date(*tuple(map(int, dateOrdered.split("-"))))
            order.__date_completed = date(*tuple(map(int, date_completed.split("-")))) if date_completed else None
            
            orders.append(order)
            
        return orders
    
    def get_date_ordered(self) -> date:
        return self.__date_ordered
    
    def get_date_completed(self) -> date | None:
        return self.__date_completed
    
    def set_date_completed(self, date_completed: date):
        return self.__date_completed
    
    def get_user(self) -> User:
        if self.__user_instance is None:
            self.__user_instance = User.load_by_id(self.__user_id)
        
        return self.__user_instance
    
    def get_item(self) -> Item:
        if self.__item_instance is None:
            self.__item_instance = Item.load_by_id(self.__item_id)
        
        return self.__item_instance
    
    def get_number_ordered(self) -> int:
        return self.__number_ordered
    
    def update(self):
        UPDATE_QUERY = f"""
            UPDATE `order` SET
                `date_ordered` = \"{self.__date_ordered}\",
                `item_id` = {self.__item_id},
                `number_ordered` = {self.__number_ordered},
                `user_id` = {self.__user_id},
                `date_completed` = \"{self.__date_completed}\"
            WHERE 
                `id` = {self.__id}
            ;
        """
        
        execute_query(UPDATE_QUERY)
        
    def delete(self):
        execute_query(f"DELETE FROM `order` WHERE `id` = {self.__id}")
    
    def __str__(self) -> str:
        return f"<Order: id={self.__id}, date_ordered={self.__date_ordered}, item_id={self.__item_id}, number_ordered={self.__number_ordered}, user_id={self.__user_id}, date_completed={self.__date_completed}"
    
    def __repr__(self) -> str:
        return str(self)