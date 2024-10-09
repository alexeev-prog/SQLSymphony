from abc import ABC, abstractmethod
from typing import Any

from sqlsymphony_orm.queries import QueryBuilder
from sqlsymphony_orm.database.connection import DBConnector, SQLiteDBConnector


class DBManager(ABC):
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

		self.q = q.SELECT(*self._model_fields).FROM(model_class._table_name)
		self.connector = DBConnector()

	@abstractmethod
	def filter(self, *args, **kwargs):
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
	def fetch(self):
		"""
		Fetches the object.

		:raises		NotImplementedError:  Abstract method
		"""
		raise NotImplementedError()


class SQLiteDBManager(DBManager):
	"""
	This class describes a sq lite db manager.
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

		self.q = q.SELECT(*self._model_fields).FROM(model_class._table_name)
		self._connector = SQLiteDBConnector()

		if model_class._table_name != "model":
			self._connector.connect(database_name)

	def insert(self, table_name: str, columns: str, count: str, values: tuple):
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
		query = f"INSERT INTO {table_name} ({columns}) VALUES ({count})"

		self._connector.fetch(query, values)
		self._connector.commit()

	def update(self, table_name: str, key: str, orig_field: str, new_value: str):
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

		self._connector.fetch(query, (new_value, orig_field))
		self._connector.commit()

	def filter(self, *args, **kwargs) -> list:
		"""
		Filter models (WHERE sql query)

		:param		args:	 The arguments
		:type		args:	 list
		:param		kwargs:	 The keywords arguments
		:type		kwargs:	 dictionary

		:returns:	list of models
		:rtype:		list
		"""
		self.q = self.q.WHERE(*args, **kwargs)
		return self.fetch()

	def commit_changes(self):
		"""
		Commits changes.
		"""
		self._connector.commit()

	def create_table(self, table_name: str, fields: dict):
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

		self._connector.fetch(query)

	def delete(self, table_name: str, field_name: str, field_value: Any):
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

		self._connector.fetch(query, (field_value,))
		self._connector.commit()

	def fetch(self) -> list:
		"""
		Fetches the object.

		:returns:	list of objects
		:rtype:		list
		"""
		q = str(self.q)
		db_results = self._connector.fetch(q)
		self.q = (
			QueryBuilder()
			.SELECT(*self._model_fields)
			.FROM(self.model_class._table_name)
		)
		results = []

		for row in db_results:
			model = self.model_class(manager=True)

			for field, val in zip(self._model_fields, row):
				setattr(model, field, val)

			results.append(model)

		return results
