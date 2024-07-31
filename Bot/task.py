from .dbfile import select, update, insert, create_tables, delete, send_query


class Task:
    def __init__(self, task_id: int):
        self.task_id = task_id

    def get_info(self):
        task_data = select(table="tasks", conditions=f"id = {self.task_id}")
        if task_data:
            return {
                "task_id": task_data[0][0],
                "price_per_completion": float(task_data[0][1]),
                "channels": task_data[0][2].split(","),
                "completions": task_data[0][3],
                "description": task_data[0][4],
                "max_completions": task_data[0][5],
                "users_completed": task_data[0][6].split(","),
            }
        else:
            return None

    def add_task(
        self,
        id,
        price_per_completion: float,
        channels: list,
        completions: int,
        description: str,
        max_completions: int,
    ):
        channels_str = ",".join(channels)
        insert(
            table="tasks",
            columns="id, price_per_completion, channels, completions, description, max_completions, users_completed",
            values=f"{id}, {price_per_completion}, '{channels_str}', {completions}, '{description}', {max_completions}, ''",
        )

    def get_price(self):
        task = self.get_info()
        if task:
            return task["price_per_completion"]
        else:
            return None

    def set_price(self, new_price: float):
        if self.get_info():
            update(
                table="tasks",
                value=f"price_per_completion = {new_price}",
                conditions=f"id = {self.task_id}",
            )

    def get_channels(self):
        task = self.get_info()
        if task:
            return task["channels"]
        else:
            return None

    def set_channels(self, new_channels: list):
        channels_str = ",".join(new_channels)
        if self.get_info():
            update(
                table="tasks",
                value=f"channels = '{channels_str}'",
                conditions=f"id = {self.task_id}",
            )

    def get_completions(self):
        task = self.get_info()
        if task:
            return task["completions"]
        else:
            return None

    def set_completions(self, new_completions: int):
        if self.get_info():
            update(
                table="tasks",
                value=f"completions = {new_completions}",
                conditions=f"id = {self.task_id}",
            )

    def get_max_completions(self):
        task = self.get_info()
        if task:
            return task["max_completions"]
        else:
            return None

    def set_max_completions(self, new_max_completions: int):
        if self.get_info():
            update(
                table="tasks",
                value=f"max_completions = {new_max_completions}",
                conditions=f"id = {self.task_id}",
            )

    def get_description(self):
        task = self.get_info()
        if task:
            return task["description"]
        else:
            return None

    def set_description(self, new_description: str):
        if self.get_info():
            update(
                table="tasks",
                value=f"description = '{new_description}'",
                conditions=f"id = {self.task_id}",
            )

    def get_users_completed(self):
        task = self.get_info()
        if task:
            return task["users_completed"]
        else:
            return None

    def add_user_completed(self, user_id: int):
        task = self.get_info()
        if task:
            users_completed = task["users_completed"]
            if str(user_id) not in users_completed:
                users_completed.append(str(user_id))
                users_completed_str = ",".join(users_completed)
                update(
                    table="tasks",
                    value=f"users_completed = '{users_completed_str}'",
                    conditions=f"id = {self.task_id}",
                )

    @staticmethod
    def select_all_tasks():
        return select(table="tasks")

    @staticmethod
    def delete_task(task_id: int):
        delete(table="tasks", conditions=f"id = {task_id}")

    @staticmethod
    def drop_all():
        send_query("DROP TABLE IF EXISTS tasks")
