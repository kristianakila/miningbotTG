from .dbfile import select, update, insert, create_tables, send_query
from collections import Counter


class User:
    def __init__(self, user_id: int):
        self.user_id = user_id
        create_tables(
            table_name="users",
            columns="(id SERIAL PRIMARY KEY AUTOINCREMENT, user_id BIGINT, balance_bull TEXT, address TEXT, withdraw_state_bull INTEGER, mining_state TEXT, refferer_id TEXT, mining_result INTEGER, mining_hours INTEGER, name TEXT)",
        )
        create_tables(
            table_name="tasks",
            columns="(id BIGINT, price_per_completion REAL, channels TEXT, completions INTEGER, description TEXT, max_completions INTEGER, users_completed TEXT)",
        )

    def get_info(self):
        user_data = select(table="users", conditions=f"user_id = {self.user_id}")
        if user_data:
            return {
                "user_id": user_data[0][1],
                "balance": {
                    "bull": float(user_data[0][2]),
                },
                "address": user_data[0][3],
                "wstate": {
                    "bull": user_data[0][4],
                },
                "refferer": user_data[0][6],
                "mining": {
                    "result": user_data[0][7],
                    "hours": user_data[0][8],
                    "state": user_data[0][5],
                },
            }
        else:
            return None

    def add_user(self, refferer=None, username=None):
        ref = f"'not_active_{str(refferer)}'" if refferer else "''"

        if not self.get_info():
            insert(
                table="users",
                columns="user_id, balance_bull, withdraw_state_bull, refferer_id, mining_result, mining_hours, mining_state, name",
                values=f"{self.user_id}, '0.00', 0, {ref}, 80, 8, '', '{username}'",
            )
            return True
        return False

    def set_name(self, name):
        if self.get_info():
            update(
                table="users",
                value=f"name = '{name}'",
                conditions=f"user_id = {self.user_id}",
            )

    def get_balance(self):
        user = self.get_info()
        if user:
            return user["balance"]
        else:
            return None

    def set_balance(self, new_balance):
        if self.get_info():
            update(
                table="users",
                value=f"balance_bull = '{str(new_balance['bull'])}'",
                conditions=f"user_id = {self.user_id}",
            )

    def get_wstate(self):
        user = self.get_info()
        if user:
            return user["wstate"]
        else:
            return None

    def set_mining_state(self, mining_state):
        if self.get_info():
            update(
                table="users",
                value=f"mining_state = {mining_state}",
                conditions=f"user_id = {self.user_id}",
            )

    def get_mining_state(self):
        user = self.get_info()
        if user:
            return user["mining"]["state"]
        else:
            return None

    def set_wstate(self, wstate):
        if self.get_info():
            update(
                table="users",
                value=f"withdraw_state_bull = {wstate['bull']}",
                conditions=f"user_id = {self.user_id}",
            )

    def get_address(self):
        user = self.get_info()
        if user:
            return user["address"]
        else:
            return None

    def set_address(self, address: str):

        if self.get_info():
            update(
                table="users",
                value=f"address = {address}",
                conditions=f"user_id = {self.user_id}",
            )

    def get_ref_count(self):
        refferals = select(table="users", conditions=f"refferer_id = '{self.user_id}'")
        return len(refferals)

    def update_refferer(self):
        info = self.get_info()
        refferer: str = info["refferer"]
        if "not_active_" in refferer:
            update(
                table="users",
                value=f"refferer_id = {refferer.split('_')[2]}",
                conditions=f"user_id = {self.user_id}",
            )
            refferer_user = User(refferer.split("_")[2])
            ref_bonus = str(refferer_user.get_balance()["bull"] + 50)
            refferer_user.set_balance({"bull": ref_bonus})
            return refferer.split("_")[2]
        return None

    @staticmethod
    def get_top_10():
        q = """
        SELECT name, balance_bull
        FROM users
        ORDER BY CAST(balance_bull AS FLOAT) DESC
        LIMIT 10
        """

        result = send_query(q)
        if not result:
            return None
        top_users = [{"username": user[0], "bull": float(user[1])} for user in result]
        return top_users

    @staticmethod
    def get_top_10_referrers():
        refferer_data = select(table="users", conditions="refferer_id NOT LIKE '%_%'")

        if not refferer_data:
            return []

        refferer_ids = [ref[6] for ref in refferer_data if ref]

        ref_count = Counter(refferer_ids)

        top_10_refs = ref_count.most_common(10)

        top_10_ref_data = []
        for ref_id, count in top_10_refs:
            if str(ref_id).isdigit():
                name_data = select(table="users", conditions=f"user_id = {ref_id}")
                if name_data:
                    top_10_ref_data.append((name_data[0][9], count))

        return top_10_ref_data

    @staticmethod
    def get_users_count():
        q = """
        SELECT user_id
        FROM users
        """

        result = send_query(q)
        if not result:
            return None

        return len(result)

    @staticmethod
    def get_all():
        q = """
        SELECT user_id, name
        FROM users
        """

        result = send_query(q)
        if not result:
            return None
        top_users = [{"username": user[1], "user_id": user[0]} for user in result]
        return top_users
