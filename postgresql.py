import os
import sqlalchemy

from dotenv import load_dotenv, find_dotenv
from sqlalchemy import or_, func

load_dotenv(find_dotenv(), override=True)


class PostgreSQL:
    def __init__(self):
        self.con, self.meta = self._connect()
        self.users_table = self.meta.tables['users']
        self.orders_table = self.meta.tables['orders']
        self.menus_table = self.meta.tables['menus']
        self.stocks_table = self.meta.tables['stocks']
        self.schedules_table = self.meta.tables['schedules']

    @staticmethod
    def _connect():
        url = os.environ['DATABASE_URL']
        con = sqlalchemy.create_engine(url, client_encoding='utf8')
        meta = sqlalchemy.MetaData(bind=con, reflect=True)

        return con, meta

    # Menus
    def get_menus(self):
        raw_menus = self.con.execute(self.menus_table.select()).fetchall()
        if raw_menus is None:
            return None
        menus = []
        for raw_menu in raw_menus:
            type_menu, name = raw_menu
            menu = {
                'type_menu': type_menu,
                'name': name
            }
            menus.append(menu)
        return menus

    def get_type_from_name(self, name):
        menus = self.get_menus()
        for menu in menus:
            if name in menu['name']:
                return menu['type_menu']
        return 'X'

    def get_name_from_type(self, type_menu):
        menus = self.get_menus()
        for menu in menus:
            if type_menu == menu['type_menu']:
                return menu['name']
        return 'X'

    # Orders
    def get_order_order(self, searched_user_id):
        clause = self.orders_table.select().where(
            or_(self.orders_table.c.status == 0, self.orders_table.c.status == 1)
        ).order_by(
            self.orders_table.c.timestamp
        )
        raw_orders = self.con.execute(clause).fetchall()
        if raw_orders is None:
            return None
        order = 1
        for raw_order in raw_orders:
            _, _, _, _, user_id = raw_order
            if user_id == searched_user_id:
                return order
            order += 1
        return None

    def get_daily_successful_orders(self, selected_date):
        clause = self.orders_table.select().where(
            self.orders_table.c.status == 2
        ).where(
            func.date(self.orders_table.c.timestamp) == selected_date
        ).order_by(
            self.orders_table.c.timestamp
        ).with_only_columns(
            [func.count()]
        ).order_by(
            None
        )
        num_successful_orders = self.con.execute(clause).scalar()
        return num_successful_orders

    def get_daily_unsuccessful_orders(self, selected_date):
        clause = self.orders_table.select().where(
            self.orders_table.c.status != 2
        ).where(
            func.date(self.orders_table.c.timestamp) == selected_date
        ).order_by(
            self.orders_table.c.timestamp
        ).with_only_columns(
            [func.count()]
        ).order_by(
            None
        )
        num_unsuccessful_orders = self.con.execute(clause).scalar()
        return num_unsuccessful_orders

    def get_orders_leaderboard(self):
        clause = self.orders_table.select().where(
            self.orders_table.c.status == 2
        ).with_only_columns(
            [self.orders_table.c.user_id,
            func.count(self.orders_table.c.timestamp)]
        ).group_by(
            self.orders_table.c.user_id
        )
        leaderboard = self.con.execute(clause).fetchall()
        return leaderboard

    def get_unprocessed_orders(self, type_menu):
        clause = self.orders_table.select().where(
            self.orders_table.c.status == -1
        ).where(
            self.orders_table.c.type_menu == type_menu
        ).order_by(
            self.orders_table.c.timestamp
        )
        raw_orders = self.con.execute(clause).fetchall()
        if raw_orders is None:
            return None
        list_unprocessed_orders = []
        for raw_order in raw_orders:
            _, _, _, _, user_id = raw_order
            list_unprocessed_orders.append(user_id)
        return list_unprocessed_orders

    def has_unprocessed_order(self, user_id, type_menu):
        clause = self.orders_table.select().where(
            self.orders_table.c.user_id == user_id
        ).where(
            self.orders_table.c.type_menu == type_menu
        ).where(
            self.orders_table.c.status == -1
        )
        order = self.con.execute(clause).fetchone()
        return order is not None

    def insert_order(self, user_id, type_menu, status):
        clause = self.orders_table.insert().values(
            user_id=user_id,
            type_menu=type_menu,
            status=status
        )
        result = self.con.execute(clause)
        return str(result.inserted_primary_key[0])

    def get_order(self, order_id):
        clause = self.orders_table.select().where(
            self.orders_table.c.id == order_id
        )
        order = self.con.execute(clause).fetchone()
        return order

    def update_status_order(self, order_id, status):
        clause =  self.orders_table.update().where(
                        self.orders_table.c.id==order_id
                    ).values(
                        status=status
                    )

        self.con.execute(clause)
    # Schedules
    def get_schedule(self):
        schedule = self.con.execute(self.schedules_table.select()).fetchone()
        if schedule is None:
            return None
        _, close_hour, open_hour = schedule
        return {
            'open_hour': open_hour,
            'close_hour': close_hour
        }

    def set_schedule(self, what_to_set, time):
        clause = None

        if(what_to_set == 'open_hour'):
            clause = self.schedules_table.update().where(
                self.schedules_table.c.id == 1
            ).values(
                open_hour=time
            )
        elif(what_to_set == 'close_hour'):
            clause = self.schedules_table.update().where(
                self.schedules_table.c.id == 1
            ).values(
                close_hour=time
            )

        if clause is not None:
            self.con.execute(clause)

    # Stocks
    def get_stock(self, type_menu):
        clause = self.stocks_table.select().where(
            self.stocks_table.c.type_menu == type_menu
        )
        stock = self.con.execute(clause).fetchone()
        if stock is None:
            return None
        type_menu, quantity = stock
        return {
            'type_menu': type_menu,
            'quantity': quantity
        }

    def restock(self, type_menu, added_quantity):
        clause = self.stocks_table.update().where(
            self.stocks_table.c.type_menu == type_menu
        ).values(
            quantity=self.stocks_table.c.quantity+added_quantity
        )
        self.con.execute(clause)

    #Users
    def get_user(self, id):
        clause = self.users_table.select().where(
            self.users_table.c.id == id
        )
        user = self.con.execute(clause).fetchone()
        if user is None:
            return None
        role, id = user
        return {
            'id': id,
            'role': role
        }

    def get_user_ids(self, user_type):
        clause = self.users_table.select().where(
            self.users_table.c.role == user_type
        )
        raw_users = self.con.execute(clause).fetchall()
        if raw_users is None:
            return None
        users = []
        for raw_user in raw_users:
            id = raw_user['id']
            users.append(id)
        return users

    def is_abang(self, id):
        if(id in self.get_user_ids('abang')):
            return True
        else:
            return False

    def is_hr(self, id):
        if(id in self.get_user_ids('hr')):
            return True
        else:
            return False

    def add_abang_id(self, id):
        clause = self.users_table.insert().values(
            id=id,
            role='abang'
        )
        self.con.execute(clause)

    def add_hr_id(self, id):
        clause = self.users_table.insert().values(
            id=id,
            role='hr'
        )
        self.con.execute(clause)

    def del_abang_id(self, id):
        clause = self.users_table.delete().where(
            self.users_table.c.id==id
        ).where(
            self.users_table.c.role=='abang'
        )
        self.con.execute(clause)

    def del_hr_id(self, id):
        clause = self.users_table.delete().where(
            self.users_table.c.id==id
        ).where(
            self.users_table.c.role=='hr'
        )
        self.con.execute(clause)
