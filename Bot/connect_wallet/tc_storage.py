from pytonconnect.storage import IStorage, DefaultStorage
import sqlite3

con = sqlite3.connect("temp/tc_storage.db")
cur = con.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS items (key TEXT, value TEXT)")
con.commit()


class TcStorage(IStorage):

    def __init__(self, chat_id: int):
        self.chat_id = chat_id

    def _get_key(self, key: str):
        return str(self.chat_id) + key

    async def set_item(self, key: str, value: str):
        cur.execute(
            "INSERT INTO items (key, value) VALUES (?, ?)", (self._get_key(key), value)
        )
        con.commit()

    async def get_item(self, key: str, default_value: str = None):
        cur.execute("SELECT value FROM items WHERE key = ?", (self._get_key(key),))
        value = cur.fetchone()
        return value[0] if value else default_value

    async def remove_item(self, key: str):
        cur.execute("DELETE FROM items WHERE key = ?", (self._get_key(key),))
        con.commit()
