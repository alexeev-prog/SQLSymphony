from abc import ABC, abstractmethod
from typing import Any
from loguru import logger

from sqlsymphony_orm.queries import QueryBuilder
from sqlsymphony_orm.database.connection import DBConnector, SQLiteDBConnector


class DatabaseSession(ABC):
	"""
	This class describes a database session.
	"""

	def __init__(self, connector: DBConnector):
		"""
		Constructs a new instance.

		:param		connector:	The connector
		:type		connector:	DBConnector
		"""
		self.connector = connector

	@abstractmethod
	async def __enter__(self):
		"""
		Enter to context manager

		:returns:	database connector
		:rtype:		DBConnector
		"""
		logger.debug("Start DatabaseSession")
		return self.connector

	@abstractmethod
	async def __exit__(self):
		"""
		Exit from context manager
		"""
		logger.debug("Stop DatabaseSession")
		await self.connector.close_connection()


class SQLiteDatabaseSession(DatabaseSession):
	"""
	This class describes a sqlite database session.
	"""

	def __init__(self, connector: SQLiteDBConnector, commit: bool = False):
		"""
		Constructs a new instance.

		:param		connector:	The connector
		:type		connector:	SQLiteDBConnector
		:param		commit:		The commit
		:type		commit:		bool
		"""
		self.connector = connector
		self.commit = commit

	async def __enter__(self):
		"""
		Enter to context manager

		:returns:	connector
		:rtype:		SQLiteDBConnector
		"""
		logger.info("Create SQLiteDatabaseSession")
		return self.connector

	async def __exit__(self, type, value, traceback):
		"""
		Exit from context manager

		:param		type:		The type
		:param		value:		The value
		:param		traceback:	The traceback
		"""
		if self.commit:
			logger.debug("Commit changes...")

			try:
				await self.connector.commit()
			except Exception as ex:
				logger.error(f"Error commit changes: {ex}")

		await self.connector.close_connection()


class ModelManager(ABC):
	"""
	This class describes a db manager.
	"""

	def __init__(self, model_class: "Model"):
		"""
		Constructs a new instance.

		:param		model_class:  The model class
		:type		model_class:  Model
		"""
		self.model_class = model_class
		self._model_fields = model_class._original_fields.keys()

		q = QueryBuilder()

		self.q = await q.SELECT(*self._model_fields).FROM(model_class._table_name)
		self.connector = DBConnector()

	@abstractmethod
	async def filter(self, *args, **kwargs):
		"""
		Filter method

		:param		args:				  The arguments
		:type		args:				  list
		:param		kwargs:				  The keywords arguments
		:type		kwargs:				  dictionary

		:raises		NotImplementedError:  Abstract method
		"""
		raise NotImplementedError()

	@abstractmethod
	async def fetch(self):
		"""
		Fetches the object.

		:raises		NotImplementedError:  Abstract method
		"""
		raise NotImplementedError()


class SQLiteModelManager(ModelManager):
	"""
	This class describes a sqlite db manager.
	"""

	def __init__(self, model_class: "Model", database_name: str = "database.db"):
		"""
		Constructs a new instance.

		:param		model_class:	The model class
		:type		model_class:	Model
		:param		database_name:	The database name
		:type		database_name:	str
		"""
		self.model_class = model_class
		self._model_fields = model_class._original_fields.keys()

		q = QueryBuilder()

		self.q = await q.SELECT(*self._model_fields).FROM(self.model_class.table_name)
		self._connector = SQLiteDBConnector()

		if self.model_class.table_name != "model":
			await self._connector.connect(database_name)

	async def drop_table(self, table_name: str = None):
		if table_name is None:
			table_name = self.model_class.table_name

		query = f"DROP TABLE IF EXISTS {table_name}"

		logger.warning(f"Drop table: {table_name}")

		await self._connector.fetch(query)
		await self._connector.commit()

	async def close_connection(self):
		await self._connector.close_connection()

	async def insert(
		self,
		table_name: str,
		formatted_fields: dict,
		pk: int,
		model_class: "Model",
		ignore: bool = False,
	):
		"""
		Insert a fields to database

		:param		table_name:	 The table name
		:type		table_name:	 str
		:param		columns:	 The columns
		:type		columns:	 str
		:param		count:		 The count
		:type		count:		 str
		:param		values:		 The values
		:type		values:		 tuple
		"""
		fields = []
		values = []

		for k, v in formatted_fields.items():
			fields.append(k)
			if "PRIMARY KEY" in v:
				values.append(pk)
			else:
				values.append(getattr(model_class, k))

		columns = ", ".join(fields)
		count = ", ".join(["?" for _ in values])

		query = "INSERT "

		if ignore:
			query += "OR IGNORE "

		query += f"INTO {table_name} ({columns}) VALUES ({count})"

		logger.info(
			f'[{table_name}] Insert {"(or ignore)" if ignore else ""} new model into database'
		)

		await self._connector.fetch(query, values)

	async def update(self, table_name: str, key: str, orig_field: str, new_value: str):
		"""
		Update fields in database table

		:param		table_name:	 The table name
		:type		table_name:	 str
		:param		key:		 The key
		:type		key:		 str
		:param		orig_field:	 The original field
		:type		orig_field:	 str
		:param		new_value:	 The new value
		:type		new_value:	 str
		"""
		query = f"UPDATE {table_name} SET {key} = ? WHERE {key} = ?"

		logger.info(f"[{table_name}] Update model: {key}={new_value}")

		await self._connector.fetch(query, (new_value, orig_field))

	async def filter(self, first: bool = False, *args, **kwargs) -> list:
		"""
		Filter models (WHERE sql query)

		:param		args:	 The arguments
		:type		args:	 list
		:param		kwargs:	 The keywords arguments
		:type		kwargs:	 dictionary

		:returns:	list of models
		:rtype:		list
		"""
		self.q = await self.q.WHERE(*args, **kwargs)

		result = self.fetch()

		if first and result:
			return result[0]
		else:
			return result

	async def commit(self):
		"""
		Commits changes.
		"""
		await self._connector.commit()

	async def create_table(self, table_name: str, fields: dict):
		"""
		Creates a table.

		:param		table_name:	 The table name
		:type		table_name:	 str
		:param		fields:		 The fields
		:type		fields:		 dict
		"""
		columns = [f"{k} {v}" for k, v in fields.items()]

		query = f"CREATE TABLE IF NOT EXISTS {table_name} ("

		for column in columns:
			query += f"{column},"

		query = query[:-1]
		query += ")"

		logger.info(f"Create new table: {table_name}")

		await self._connector.fetch(query)
		await self._connector.commit()

	async def delete(self, table_name: str, field_name: str, field_value: Any):
		"""
		Delete model from database

		:param		table_name:	  The table name
		:type		table_name:	  str
		:param		field_name:	  The field name
		:type		field_name:	  str
		:param		field_value:  The field value
		:type		field_value:  Any
		"""
		query = f"DELETE FROM {table_name} WHERE {field_name} = ?"
		logger.info(f"[{table_name}] Delete model ({field_name}={field_value})")

		await self._connector.fetch(query, (field_value,))

	async def fetch(self) -> list:
		"""
		Fetches the object.

		:returns:	list of objects
		:rtype:		list
		"""
		q = str(self.q)
		db_results = await self._connector.fetch(q)

		results = []

		for row in db_results:
			model = self.model_class(manager=True)

			for field, val in zip(self._model_fields, row):
				setattr(model, field, val)

			results.append(model)

		self.q = (
			await QueryBuilder()
			.SELECT(*self._model_fields)
			.FROM(self.model_class.table_name)
		)

		return results


class MultiModelManager(ABC):
	"""
	This class describes a multi model manager.
	"""

	def __init__(self, database_name: str):
		"""
		Constructs a new instance.

		:param		database_name:	The database name
		:type		database_name:	str
		"""
		self.models = {}
		self.database_name = database_name

	@abstractmethod
	async def add_model(self, model: "Model"):
		"""
		Adds a model.

		:param		model:	The model
		:type		model:	Model
		"""
		self.models[model._model_name] = {
			"model": model,
			"manager": ModelManager(model, self.database_name),
		}

	@abstractmethod
	async def remove_model_by_name(self, model_name: str):
		"""
		Removes a model by name.

		:param		model_name:	 The model name
		:type		model_name:	 str
		"""
		try:
			del self.models[model_name]
		except KeyError:
			logger.error(f'Not found model "{model_name}"')

	@abstractmethod
	async def model_manager(self, model_name: str) -> "ModelManager":
		"""
		Get model manager

		:param		model_name:	 The model name
		:type		model_name:	 str

		:returns:	Model manager
		:rtype:		ModelManager
		"""
		model = self.models.get(model_name, None)

		if model is None:
			logger.error(f'Not found model "{model_name}"')
			return

		return model["manager"]

	@abstractmethod
	async def model(self, model_name: str) -> "Model":
		"""
		Model

		:param		model_name:	 The model name
		:type		model_name:	 str

		:returns:	Model
		:rtype:		Model
		"""
		model = self.models.get(model_name, None)

		if model is None:
			logger.error(f'Not found model "{model_name}"')
			return

		return model["model"]


class SQLiteMultiModelManager(MultiModelManager):
	"""
	This class describes a sq lite multi model manager.
	"""

	def __init__(self, database_name: str):
		"""
		Constructs a new instance.

		:param		database_name:	The database name
		:type		database_name:	str
		"""
		self.models = {}
		self.database_name = database_name

	async def add_model(self, model: "Model"):
		"""
		Adds a model.

		:param		model:	The model
		:type		model:	Model
		"""
		logger.info(f"[SQLiteMultiModelManager] New model added: {model._model_name}")
		self.models[model._model_name] = {
			"model": model,
			"manager": SQLiteModelManager(model, self.database_name),
		}

	async def remove_model_by_name(self, model_name: str):
		"""
		Removes a model by name.

		:param		model_name:	 The model name
		:type		model_name:	 str
		"""
		logger.info(f"[SQLiteMultiModelManager] Remove model: {model_name}")
		try:
			del self.models[model_name]
		except KeyError:
			logger.error(f'Not found model "{model_name}"')

	async def model_manager(self, model_name: str) -> "ModelManager":
		"""
		Get model manager

		:param		model_name:	 The model name
		:type		model_name:	 str

		:returns:	Model manager
		:rtype:		ModelManager
		"""
		model = self.models.get(model_name, None)

		if model is None:
			logger.error(f'Not found model "{model_name}"')
			return

		return model["manager"]

	async def model(self, model_name: str) -> "Model":
		"""
		Get model

		:param		model_name:	 The model name
		:type		model_name:	 str

		:returns:	Model
		:rtype:		Model
		"""
		model = self.models.get(model_name, None)

		if model is None:
			logger.error(f'Not found model "{model_name}"')
			return

		return model["model"]


class MultiManager(ABC):
	"""
	This class describes a multi manager.
	"""

	@abstractmethod
	async def reconnect(self):
		"""
		reconnect to db

		:raises		NotImplementedError:  abstract method
		"""
		raise NotImplementedError()

	@abstractmethod
	async def drop_table(self, table_name: str):
		"""
		Drop sql table

		:param		table_name:			  The table name
		:type		table_name:			  str

		:raises		NotImplementedError:  abstract method
		"""
		raise NotImplementedError()

	@abstractmethod
	async def close_connection(self):
		"""
		Closes a connection.

		:raises		NotImplementedError:  abstract method
		"""
		raise NotImplementedError()

	@abstractmethod
	async def insert(
		self,
		table_name: str,
		formatted_fields: dict,
		pk: int,
		model_class: "Model",
		ignore: bool = False,
	):
		"""
		insert new model to database

		:param		table_name:			  The table name
		:type		table_name:			  str
		:param		formatted_fields:	  The formatted fields
		:type		formatted_fields:	  dict
		:param		pk:					  primary key value
		:type		pk:					  int
		:param		model_class:		  The model class
		:type		model_class:		  Model
		:param		ignore:				  The ignore
		:type		ignore:				  bool

		:raises		NotImplementedError:  { exception_description }
		"""
		raise NotImplementedError()

	@abstractmethod
	async def update(self, table_name: str, key: str, orig_field: str, new_value: str):
		"""
		update model

		:param		table_name:			  The table name
		:type		table_name:			  str
		:param		key:				  The key
		:type		key:				  str
		:param		orig_field:			  The original field
		:type		orig_field:			  str
		:param		new_value:			  The new value
		:type		new_value:			  str

		:raises		NotImplementedError:  abstract method
		"""
		raise NotImplementedError()

	@abstractmethod
	async def filter(self, query: QueryBuilder):
		"""
		filter and get model by query

		:param		query:				  The query
		:type		query:				  QueryBuilder

		:raises		NotImplementedError:  abstract method
		"""
		raise NotImplementedError()

	@abstractmethod
	async def commit(self):
		"""
		Commit changes

		:raises		NotImplementedError:  abstract method
		"""
		raise NotImplementedError()

	@abstractmethod
	async def create_table(self, table_name: str, fields: dict):
		"""
		Creates a table.

		:param		table_name:			  The table name
		:type		table_name:			  str
		:param		fields:				  The fields
		:type		fields:				  dict

		:raises		NotImplementedError:  abstract method
		"""
		raise NotImplementedError()

	@abstractmethod
	async def delete(self, table_name: str, field_name: str, field_value: Any):
		"""
		delete model

		:param		table_name:			  The table name
		:type		table_name:			  str
		:param		field_name:			  The field name
		:type		field_name:			  str
		:param		field_value:		  The field value
		:type		field_value:		  Any

		:raises		NotImplementedError:  abstract method
		"""
		raise NotImplementedError()


class SQLiteMultiManager(MultiManager):
	"""
	This class describes a sqlite multi manager.
	"""

	def __init__(self, database_name: str):
		"""
		Constructs a new instance.

		:param		database_name:	The database name
		:type		database_name:	str
		"""
		self._connector = SQLiteDBConnector()
		self.database_name = database_name
		await self._connector.connect(self.database_name)

	async def execute(
		self, raw_sql_query: str, values: tuple = (), get_cursor: bool = False
	):
		return await self._connector.fetch(raw_sql_query, values, get_cursor)

	async def reconnect(self, database_file: str = None):
		"""
		reconnect to database
		"""
		if database_file is not None:
			self.database_name = database_file
		await self._connector.connect(self.database_name)

	async def drop_table(self, table_name: str):
		"""
		drop table

		:param		table_name:	 The table name
		:type		table_name:	 str
		"""
		query = f"DROP TABLE IF EXISTS {table_name}"

		logger.warning(f"Drop table: {table_name}")

		await self._connector.fetch(query)
		await self._connector.commit()

	async def close_connection(self):
		"""
		Closes a connection.
		"""
		await self._connector.close_connection()

	async def insert(
		self,
		table_name: str,
		formatted_fields: dict,
		pk: int,
		model_class: "Model",
		ignore: bool = False,
	):
		"""
		Insert a fields to database

		:param		table_name:	 The table name
		:type		table_name:	 str
		:param		columns:	 The columns
		:type		columns:	 str
		:param		count:		 The count
		:type		count:		 str
		:param		values:		 The values
		:type		values:		 tuple
		"""
		fields = []
		values = []

		for k, v in formatted_fields.items():
			fields.append(k)
			if "PRIMARY KEY" in v:
				values.append(pk)
			else:
				values.append(getattr(model_class, k))

		columns = ", ".join(fields)
		count = ", ".join(["?" for _ in values])

		query = "INSERT "

		if ignore:
			query += "OR IGNORE "

		query += f"INTO {table_name} ({columns}) VALUES ({count})"

		logger.info(
			f'[{table_name}] Insert {"(or ignore)" if ignore else ""} new model into database'
		)

		await self._connector.fetch(query, values)

	async def update(self, table_name: str, key: str, orig_field: str, new_value: str):
		"""
		Update fields in database table

		:param		table_name:	 The table name
		:type		table_name:	 str
		:param		key:		 The key
		:type		key:		 str
		:param		orig_field:	 The original field
		:type		orig_field:	 str
		:param		new_value:	 The new value
		:type		new_value:	 str
		"""
		query = f"UPDATE {table_name} SET {key} = ? WHERE {key} = ?"

		logger.info(f"[{table_name}] Update model: {key}={new_value}")

		await self._connector.fetch(query, (new_value, orig_field))

	async def filter(self, query: str) -> list:
		"""
		filter and get model by query

		:param		query:	The query
		:type		query:	str

		:returns:	models
		:rtype:		list
		"""
		result = await self._connector.fetch(query)

		return result

	async def commit(self):
		"""
		Commits changes.
		"""
		await self._connector.commit()

	async def create_table(self, table_name: str, fields: dict):
		"""
		Creates a table.

		:param		table_name:	 The table name
		:type		table_name:	 str
		:param		fields:		 The fields
		:type		fields:		 dict
		"""
		columns = [f"{k} {v}" for k, v in fields.items()]

		query = f"CREATE TABLE IF NOT EXISTS {table_name} ("

		for column in columns:
			query += f"{column},"

		query = query[:-1]
		query += ")"

		logger.info(f"Create new table: {table_name}")

		await self._connector.fetch(query)
		await self._connector.commit()

	async def delete(self, table_name: str, field_name: str, field_value: Any):
		"""
		Delete model from database

		:param		table_name:	  The table name
		:type		table_name:	  str
		:param		field_name:	  The field name
		:type		field_name:	  str
		:param		field_value:  The field value
		:type		field_value:  Any
		"""
		query = f"DELETE FROM {table_name} WHERE {field_name} = ?"
		logger.info(f"[{table_name}] Delete model ({field_name}={field_value})")

		await self._connector.fetch(query, (field_value,))