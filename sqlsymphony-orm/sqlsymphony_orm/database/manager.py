import sqlite3
from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any

from sqlsymphony_orm.queries import QueryBuilder
from sqlsymphony_orm.database.connection import DBConnector, SQLiteDBConnector


class DBManager(ABC):
	def __init__(self, model_class: 'Model'):
		self.model_class = model_class
		self._model_fields = model_class._original_fields.keys()

		q = QueryBuilder()

		self.q = q.SELECT(*self._model_fields).FROM(model_class._table_name)
		self.connector = DBConnector()

	@abstractmethod
	def filter(self, *args, **kwargs):
		raise NotImplementedError()

	@abstractmethod
	def fetch(self):
		raise NotImplementedError()


class SQLiteDBManager(DBManager):
	def __init__(self, model_class: 'Model', database_name: str='database.db'):
		self.model_class = model_class
		self._model_fields = model_class._original_fields.keys()

		q = QueryBuilder()

		self.q = q.SELECT(*self._model_fields).FROM(model_class._table_name)
		self._connector = SQLiteDBConnector()

		if model_class._table_name != 'model':
			self._connector.connect(database_name)

	def insert(self, table_name, columns, count, values):
		query = f'INSERT INTO {table_name} ({columns}) VALUES ({count})'

		self._connector.fetch(query, values)
		self._connector.commit()

	def filter(self, *args, **kwargs):
		self.q = self.q.WHERE(*args, **kwargs)
		return self

	def create_table(self, table_name: str, fields: dict):
		columns = [f'{k} {v}' for k, v in fields.items()]

		query = f'CREATE TABLE IF NOT EXISTS {table_name} ('

		for column in columns:
			query += f'{column},'

		query = query[:-1]
		query += ')'

		self._connector.fetch(query)

	def fetch(self):
		q = str(self.q)
		db_results = self._connector.fetch(q)
		results = []

		for row in db_results:
			model = self.model_class()

			for field, val in zip(self._model_fields, row):
				setattr(model, field, val)

			results.append(model)

		return results
