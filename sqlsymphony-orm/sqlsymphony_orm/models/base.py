from dataclasses import dataclass
from typing import Any, Tuple


from rich.console import Console
from rich.table import Table

from sqlsymphony_orm.datatypes.base import FieldMeta


@dataclass
class Model(metaclass=FieldMeta):
	def __init__(self, **kwargs):
		self._last_pk_value: int = 0

		for field_name, field in self._fields.items():
			value = kwargs.get(field_name, None)

			if field_name == self._primary_key:
				if field.auto_increment and value is None:
					value = self._get_next_pk_value()

			if value is not None and field.validate(value):
				setattr(self, field_name, field.to_db_value(value))
			else:
				setattr(self, field_name, field.default)

	def save(self):
		pass

	def delete(self):
		pass

	@classmethod
	def get(cls, **kwargs) -> 'Model':
		pass

	@classmethod
	def all(cls) -> Tuple['Model']:
		pass

	@property
	def pk(self):
		return getattr(self, self._primary_key)

	def _get_next_pk_value(self) -> Any:
		self._last_pk_value += 1
		return self._last_pk_value

	def view_table_info(self):
		table = Table(title=f'Model {self}')

		table.add_column("Field name", style="blue")
		table.add_column('Field', style='green')

		for field_name, field in self._fields.items():
			table.add_row(str(field_name), str(field))

		console = Console()
		console.print(table)
