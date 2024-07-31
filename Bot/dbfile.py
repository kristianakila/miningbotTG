import sqlite3


def create_tables(table_name, columns):
    conn = sqlite3.connect("temp/database.db")
    conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} {columns}")
    conn.commit()
    conn.close()


def insert(table, columns, values):
    conn = sqlite3.connect("temp/database.db")
    conn.execute(f"INSERT INTO {table} ({columns}) VALUES ({values})")
    conn.commit()
    conn.close()


def select(table, conditions=None):
    conn = sqlite3.connect("temp/database.db")
    query = f"SELECT * FROM {table}"
    if conditions:
        query += f" WHERE {conditions}"
    result = conn.execute(query).fetchall()
    conn.close()
    return result


def update(table, value, conditions=None):
    conn = sqlite3.connect("temp/database.db")
    query = f"UPDATE {table} SET {value}"
    if conditions:
        query += f" WHERE {conditions}"
    conn.execute(query)
    conn.commit()
    conn.close()


def delete(table, conditions=None):
    conn = sqlite3.connect("temp/database.db")
    query = f"DELETE FROM {table}"
    if conditions:
        query += f" WHERE {conditions}"
    conn.execute(query)
    conn.commit()
    conn.close()


def send_query(q):
    conn = sqlite3.connect("temp/database.db")
    result = conn.execute(q).fetchall()
    conn.commit()
    conn.close()
    return result
