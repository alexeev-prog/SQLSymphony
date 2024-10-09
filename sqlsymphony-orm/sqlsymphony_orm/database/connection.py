import sqlite3
from abc import ABC, abstractmethod
from typing import Tuple

from rich.console import Console
from rich.table import Table
from rich import print

from sqlsymphony_orm.performance.cache import cached, SingletonCache, InMemoryCache


class DBConnector(ABC):
	"""
	This class describes a db connector.
	"""

	def __new__(cls, *args, **kwargs):
		"""
		New class

		:param		cls:	 The cls
		:type		cls:	 list
		:param		args:	 The arguments
		:type		args:	 list
		:param		kwargs:	 The keywords arguments
		:type		kwargs:	 dictionary

		:returns:	cls instance
		:rtype:		self
		"""
		if not hasattr(cls, "instance"):
			cls.instance = super(DBConnector, cls).__new__(cls, *args, **kwargs)

		return cls.instance

	@abstractmethod
	def connect(self, database_name: str):
		"""
		Connect to database

		:param		database_name:		  The database name
		:type		database_name:		  str

		:raises		NotImplementedError:  Abstract method
		"""
		raise NotImplementedError()

	@abstractmethod
	def commit(self):
		"""
		Commit changes to database

		:raises		NotImplementedError:  Abstract method
		"""
		raise NotImplementedError()

	@abstractmethod
	def fetch(self, query: str):
		"""
		Fetches the given query.

		:param		query:				  The query
		:type		query:				  str

		:raises		NotImplementedError:  Abstract method
		"""
		raise NotImplementedError()


class SQLiteDBConnector(DBConnector):
	"""
	This class describes a sqlite db connector.
	"""

	def __new__(cls, *args, **kwargs):
		"""
		New class

		:param		cls:	 The cls
		:type		cls:	 list
		:param		args:	 The arguments
		:type		args:	 list
		:param		kwargs:	 The keywords arguments
		:type		kwargs:	 dictionary

		:returns:	cls instance
		:rtype:		self
		"""
		if not hasattr(cls, "instance"):
			cls.instance = super(SQLiteDBConnector, cls).__new__(cls, *args, **kwargs)

		return cls.instance

	def close_connection(self):
		"""
		Closes a connection.
		"""
		self._connection.close()
		print("[bold]Connection has been closed[/bold]")

	def connect(self, database_name: str = "database.db"):
		"""
		Connect to database

		:param		database_name:	The database name
		:type		database_name:	str
		"""
		self._connection = sqlite3.connect(database_name)

	def commit(self):
		"""
		Commit changes to database
		"""
		self._connection.commit()

	@cached(SingletonCache(InMemoryCache, max_size=1000, ttl=60))
	def fetch(self, query: str, values: Tuple = ()) -> list:
		"""
		Fetch SQL query

		:param		query:	 The query
		:type		query:	 str
		:param		values:	 The values
		:type		values:	 Tuple

		:returns:	list with fetched results
		:rtype:		list
		"""
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
