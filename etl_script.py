import contextlib
import os
import sqlite3


DB_NAME = os.environ.get("DB_NAME", "db.sqlite")


def etl_script(self):
    with contextlib.closing(sqlite3.connect(DB_NAME)) as connection:
        with connection as cursor:
            data = cursor.execute("SELECT 1, SQLITE_VERSION()").fetchone()
            print(data)  # (1, "3.39.3")


if __name__ == "__main__":
    etl_script()
