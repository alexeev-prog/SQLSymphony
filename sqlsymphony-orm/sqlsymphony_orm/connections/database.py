import sqlite3
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple


class DatabaseConnection(ABC):
	@abstractmethod
	def connect(self):
		pass

	@abstractmethod
	def execute(self, query: str, params: Tuple = ()) -> Tuple:
		pass

	@abstractmethod
	def commit(self):
		pass

	@abstractmethod
	def close(self):
		pass


@dataclass
class SQLiteDatabaseConnection(DatabaseConnection):
	database_file: str = 'database.db'

	def connect(self):
		self._connection = sqlite3.connect(self.database_file)

	def execute(self, query: str, params: Tuple = ()) -> Tuple:
		cursor = self._connection.cursor()
		cursor.execute(query, params)

		return cursor.fetchall()

	def commit(self):
		self._connection.commit()

	def close(self):
		self._connection.close()


class DatabaseRepository(ABC):
	def __init__(self, connection: DatabaseConnection):
		self._connection = connection

	@abstractmethod
	def create_table(self, table_name: str, data: dict):
		pass

	@abstractmethod
	def update_table(self, table_name: str, pk: Any, data: dict)
