import sqlite3
from abc import ABC, abstractmethod
from typing import Tuple

from rich import print

from loguru import logger


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
	async def connect(self, database_name: str):
		"""
		Connect to database

		:param		database_name:		  The database name
		:type		database_name:		  str

		:raises		NotImplementedError:  Abstract method
		"""
		raise NotImplementedError()

	@abstractmethod
	async def commit(self):
		"""
		Commit changes to database

		:raises		NotImplementedError:  Abstract method
		"""
		raise NotImplementedError()

	@abstractmethod
	async def fetch(self, query: str):
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

	async def close_connection(self):
		"""
		Closes a connection.
		"""
		await self._connection.close()
		print("[bold]Connection has been closed[/bold]")
		logger.info("Close Database Connection")

	async def connect(self, database_name: str = "database.db"):
		"""
		Connect to database

		:param		database_name:	The database name
		:type		database_name:	str
		"""
		pragmas = ["PRAGMA foreign_keys = 1"]
		self._connection = sqlite3.connect(database_name)
		self.database_name = database_name
		logger.info(f"[{database_name}] Connect database...")

		for pragma in pragmas:
			await self._connection.execute(pragma)
			logger.debug(f"Set sqlite3 pragma: {pragma}")

	async def commit(self):
		"""
		Commit changes to database
		"""
		logger.info("Commit changes to database")
		await await self._connection.commit()

	async def fetch(self, query: str, values: Tuple = (), get_cursor: bool = False) -> list:
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
		await self.commit()

		logger.debug(f"Fetch query: {query} {values}")

		try:
			cursor.execute(query, values)
		except Exception as ex:
			logger.error(f"An exception occurred while executing the request: {ex}")
			raise ex

		return [cursor, cursor.fetchall()] if get_cursor else cursor.fetchall()
