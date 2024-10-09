import sqlite3
from abc import ABC, abstractmethod
from typing import Tuple

from rich.console import Console
from rich.table import Table


class DBConnector(ABC):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super(DBConnector, cls).__new__(cls, *args, **kwargs)

        return cls.instance

    @abstractmethod
    def connect(self, database_name: str):
        raise NotImplementedError()

    @abstractmethod
    def commit(self):
        raise NotImplementedError()

    @abstractmethod
    def fetch(self, query):
        raise NotImplementedError()


class SQLiteDBConnector(DBConnector):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super(SQLiteDBConnector, cls).__new__(cls, *args, **kwargs)

        return cls.instance

    def connect(self, database_name: str = "database.db"):
        self._connection = sqlite3.connect(database_name)

    def commit(self):
        self._connection.commit()

    def fetch(self, query, values: Tuple = ()):
        cursor = self._connection.cursor()

        try:
            cursor.execute(query, values)
        except sqlite3.IntegrityError as ex:
            try:
                if str(ex).split(":")[0] == "UNIQUE constraint failed":
                    table = Table(title="SQL Error: UNIQUE", title_style="bold red")

                    table.add_column("Error Type", style="red")
                    table.add_column("Full info", style="red")
                    table.add_column("Short explain", style="yellow")
                    table.add_column("SQL Query", style="green")

                    table.add_row(
                        "IntegrityError",
                        str(ex),
                        "Problem with UNIQUE fields in a table",
                        f"{query} {values}",
                    )

                    console = Console()
                    console.print(table)

                    raise ex
            except KeyError:
                raise ex

        return cursor.fetchall()
