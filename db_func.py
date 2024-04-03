import sqlite3


def create_db(path: str):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE if not exists detail (id int, nickname text, points int)""")


def get_db(path: str):
    pass
