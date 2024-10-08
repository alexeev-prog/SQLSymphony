from typing import Any, Tuple, Type, Dict
from collections import OrderedDict

from rich.console import Console
from rich.table import Table

from sqlsymphony_orm.datatypes.fields import BaseDataType
from sqlsymphony_orm.database.manager import SQLiteDBManager


class MetaModel(type):
	"""
	This class describes a meta model.
	"""

	__tablename__ = None
	__database__ = None

	def __new__(cls, class_object: 'Model', parents: tuple, attributes: dict):
		"""
		Magic method for creating instances and classes

		:param      cls:           The cls
		:type       cls:           cls
		:param      class_object:  The class object
		:type       class_object:  Model
		:param      parents:       The parents
		:type       parents:       tuple
		:param      attributes:    The attributes
		:type       attributes:    dict

		:returns:   new class
		:rtype:     model
		"""
		new_class = super(MetaModel, cls).__new__(cls, class_object, parents, attributes)
		fields = OrderedDict()

		setattr(new_class, '_model_name', attributes['__qualname__'].lower())

		if new_class.__tablename__ is None:
			setattr(new_class, '_table_name', attributes['__qualname__'].lower())
		else:
			setattr(new_class, '_table_name', new_class.__tablename__)

		if new_class.__database__ is None:
			setattr(new_class, '_database_name', f"{attributes['__qualname__'].lower()}.db")
		else:
			setattr(new_class, "_database_name", new_class.__database__)

		for k, v in attributes.items():
			if isinstance(v, BaseDataType):
				fields[k] = v
				attributes[k] = None

		setattr(new_class, '_original_fields', fields)

		setattr(new_class, 'objects', SQLiteDBManager(new_class, new_class._database_name))

		return new_class


class Model(metaclass=MetaModel):
	"""
	This class describes a ORM model.
	"""

	__tablename__ = None
	__database__ = None

	def __init__(self, **kwargs):
		"""
		Constructs a new instance.

		:param      kwargs:  The keywords arguments
		:type       kwargs:  dictionary
		"""
		self.objects.create_table(self._table_name, self._get_formatted_sql_fields())

		for field_name, field in self._original_fields.items():
			value = kwargs.get(field_name, None)

			if value is not None and field.validate(value):
				setattr(self, field_name, field.to_db_value(value))
			else:
				setattr(self, field_name, field.default)

	def save(self):
		"""
		CRUD function: save
		"""
		fields = []
		values = []

		for k, v in self._get_formatted_sql_fields().items():
			if 'PRIMARY KEY' in v:
				continue
			else:
				fields.append(k)
				values.append(getattr(self, k))

		columns = ', '.join(fields)
		count = ', '.join(['?' for _ in values])

		self.objects.insert(self._table_name, columns, count, tuple(values))

	def _get_formatted_sql_fields(self) -> dict:
		"""
		Gets the formatted sql fields.

		:returns:   The formatted sql fields.
		:rtype:     dict
		"""
		model_fields = {}

		for field_name, field in self._original_fields.items():
			model_fields[field_name] = field.to_sql_type()
			if field.primary_key:
				model_fields[field_name] = f'{field.to_sql_type()} PRIMARY KEY'
			else:
				if not field.null:
					try:
						model_fields[field_name] += ' NOT NULL'
					except KeyError:
						model_fields[field_name] = f'{field.to_sql_type()} NOT NULL'
				elif field.unique:
					try:
						model_fields[field_name] += ' UNIQUE'
					except KeyError:
						model_fields[field_name] = f'{field.to_sql_type()} UNIQUE'
				elif field.default is not None:
					try:
						model_fields[field_name] += f' DEFAULT {field.default}'
					except KeyError:
						model_fields[field_name] = f'{field.to_sql_type()} DEFAULT {field.default}'
				else:
					model_fields[field_name] = f'{field.to_sql_type()}'

		return model_fields
