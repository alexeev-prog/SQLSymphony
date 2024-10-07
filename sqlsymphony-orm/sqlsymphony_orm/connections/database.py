import sqlite3
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple, Dict, Any


class DatabaseConnection(ABC):
	@abstractmethod
	def connect(self) -> None:
		pass

	@abstractmethod
	def execute(self, query: str, params: Tuple = ()) -> Tuple:
		pass

	@abstractmethod
	def commit(self) -> None:
		pass

	@abstractmethod
	def close(self) -> None:
		pass


class SQLiteDatabaseConnection(DatabaseConnection):
	def __init__(self, database_file: str = 'database.db'):
		self.database_file = database_file
		self._connection = sqlite3.connect(self.database_file)

	def connect(self) -> None:
		self._connection = sqlite3.connect(self.database_file)

	def execute(self, query: str, params: Tuple = ()) -> Tuple:
		message = "%-*s ::: %-*s" % (
			90,
		    query,
		    90,
		    params
		)
		print(message)
		cursor = self._connection.cursor()

		cursor.execute(query, params)

		return cursor.fetchall()

	def commit(self) -> None:
		self._connection.commit()

	def close(self) -> None:
		self._connection.close()


class DatabaseRepository(ABC):
	def __init__(self, connection: DatabaseConnection):
		self._connection = connection

	@abstractmethod
	def create(self, table_name: str, data: Dict[str, Any]) -> None:
		pass

	@abstractmethod
	def read(self, table_name: str, filters: Dict[str, Any], order_by: str = None, limit: int = None, offset: int = None) -> Tuple[Dict[str, Any]]:
		pass

	@abstractmethod
	def update(self, table_name: str, pk: Any, data: Dict[str, Any]) -> None:
		pass

	@abstractmethod
	def delete(self, table_name: str, pk: Any) -> None:
		pass

	@abstractmethod
	def count(self, table_name: str, filters: Dict[str, Any]) -> int:
		pass


@dataclass
class SQLiteDatabaseRepository(DatabaseRepository):
	def __init__(self, connection: DatabaseConnection):
		self._connection = connection

	def create_table(self, table_name: str, data: Dict[str, Any]):
		query = f'CREATE TABLE IF NOT EXISTS {table_name} ('
		columns = ''

		for field, field_val in data.items():
			columns += f'{field} {field_val}, '

		columns = columns[:-2]

		query += f'{columns}'
		query += ')'
		

		self._connection.execute(query)
		self._connection.commit()
		
	def create(self, table_name: str, data: Dict[str, Any]) -> None:
		columns = ', '.join(data.keys())
		values = ', '.join(['?' for _ in data])
		query = f"INSERT OR IGNORE INTO {table_name} ({columns}) VALUES ({values})"
		
		self._connection.execute(query, tuple(data.values()))
		self._connection.commit()

	def read(self, table_name: str, filters: Dict[str, Any], order_by: str = None, limit: int = None, offset: int = None) -> Tuple[Dict[str, Any]]:
		filters_str = ' AND '.join([f"{field} = ?" for field in filters])
		query = f"SELECT * FROM {table_name} WHERE {filters_str}"
		if order_by:
			query += f" ORDER BY {order_by}"
		if limit:
			query += f" LIMIT {limit}"
		if offset:
			query += f" OFFSET {offset}"
		
		rows = self._connection.execute(query, tuple(filters.values()))
		return tuple(dict(zip(filters.keys(), row)) for row in rows)

	def update(self, table_name: str, pk: Any, data: Dict[str, Any]) -> None:
		updates = ', '.join([f"{field} = ?" for field in data])
		query = f"UPDATE {table_name} SET {updates} WHERE id = ?"
		
		self._connection.execute(query, (*tuple(data.values()), pk))
		self._connection.commit()

	def update_field(self, table_name: str, primary_key_value: Any, field_name: str, new_value: Any):
		query = f'UPDATE {table_name} SET {field_name} = ? WHERE id = ?'
		self._connection.execute(query, (new_value, primary_key_value,))
		self._connection.commit()

	def delete(self, table_name: str, pk: Any) -> None:
		query = f"DELETE FROM {table_name} WHERE id = ?"
		
		self._connection.execute(query, (pk,))
		self._connection.commit()

	def count(self, table_name: str, filters: Dict[str, Any]=None) -> int:
		if filters is not None:
			filters_str = ' AND '.join([f"{field} = ?" for field in filters])
			query = f"SELECT COUNT(*) FROM {table_name} WHERE {filters_str}"
			
			return self._connection.execute(query, tuple(filters.values()))[0][0]
		else:
			query = f'SELECT COUNT(*) FROM {table_name}'
			return self._connection.execute(query)[0][0]
