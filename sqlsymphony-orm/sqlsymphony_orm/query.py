from typing import Tuple, Dict, Any
from sqlsymphony_orm.connections.database import DatabaseRepository


class Query:
	def __init__(self, database_repository: DatabaseRepository, table_name: str):
		self._database_repository = database_repository
		self._table_name = table_name
		self._filters = {}
		self._order_by = None
		self._limit = None
		self._offset = None

	def filter(self, **kwargs) -> 'Query':
		self._filters.update(kwargs)
		return self

	def order_by(self, field: str) -> 'Query':
		self._order_by = field
		return self

	def limit(self, limit: int) -> 'Query':
		self._limit = limit
		return self

	def offset(self, offset: int) -> 'Query':
		self._offset = offset
		return self

	def get(self) -> Tuple[Dict[str, Any]]:
		return self._database_repository.read(
			table_name=self._table_name,
			filters=self._filters,
			order_by=self._order_by,
			limit=self._limit,
			offset=self._offset
		)

	def create(self, data: Dict[str, Any]) -> None:
		self._database_repository.create(
			table_name=self._table_name,
			data=data
		)

	def update(self, pk: Any, data: Dict[str, Any]) -> None:
		self._database_repository.update(
			table_name=self._table_name,
			pk=pk,
			data=data
		)

	def delete(self, pk: Any) -> None:
		self._database_repository.delete(
			table_name=self._table_name,
			pk=pk
		)

	def count(self) -> int:
		return self._database_repository.count(
			table_name=self._table_name,
			filters=self._filters
		)
