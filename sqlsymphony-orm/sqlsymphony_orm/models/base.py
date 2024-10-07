from dataclasses import dataclass, field
from typing import Any, Tuple, Type, Dict

from rich.console import Console
from rich.table import Table

from sqlsymphony_orm.datatypes.base import FieldMeta
from sqlsymphony_orm.connections.database import DatabaseConnection, DatabaseRepository, SQLiteDatabaseConnection, SQLiteDatabaseRepository
from sqlsymphony_orm.datatypes.base import FieldMeta


class ProxyObjectMeta(FieldMeta):
	def __new__(cls, name, bases, attrs):
		model_class = super().__new__(cls, name, bases, attrs)
		model_class.database_connection = None
		model_class._model_manager = None
		return model_class


@dataclass
class Object:
	_model_class: Type['Model']
	_model_manager: 'ModelManager'

	def get(self, **kwargs) -> 'Model':
		return self._model_manager.get(self._model_class, **kwargs)

	def filter(self, **kwargs) -> Tuple['Model']:
		return self._model_manager.filter(self._model_class, **kwargs)

	def all(self) -> Tuple['Model']:
		return self._model_manager.all(self._model_class)

	def save(self, instance: 'Model') -> None:
		instance.save()

	def delete(self, instance: 'Model') -> None:
		instance.delete()


def sqlsymphony_table(table_name: str):
	def decorator(cls):
		cls.__name__ = table_name
		cls = ProxyObjectMeta(cls.__name__, (cls,), {})
		cls._proxy_object = Object(cls)
		return cls
	return decorator


# @dataclass
class ModelManager:
	_database_connection: DatabaseConnection = None
	_database_repository: DatabaseRepository = None
	_models: Dict[Type['Model'], Object] = {}

	def __init__(self, database_connection):
		self._database_connection = database_connection
		self._database_repository = SQLiteDatabaseRepository(self._database_connection)

	def register_model(self, model_class: Type['Model']):
		if model_class not in self._models:
			self._models[model_class] = Object(model_class, self)
			model_class.database_connection = self._database_connection
			model_class._model_manager = self
		
		self._create_table(model_class)

		return model_class

	def _get_table_name(self, instance: 'Model'):
		if instance.__tablename__ is None:
			instance.__tablename__ = instance.__name__

		return instance.__tablename__

	def _create_table(self, instance: 'Model'):
		fields = {}

		table_name = self._get_table_name(instance)

		for field_name, field in instance._fields.items():
			fields[field_name] = field.to_sql_type()
			if field.primary_key:
				fields[field_name] = f'{field.to_sql_type()} PRIMARY KEY'
			else:
				if not field.null:
					try:
						fields[field_name] += ' NOT NULL'
					except KeyError:
						fields[field_name] = f'{field.to_sql_type()} NOT NULL'
				elif field.unique:
					try:
						fields[field_name] += ' UNIQUE'
					except KeyError:
						fields[field_name] = f'{field.to_sql_type()} UNIQUE'
				elif field.default is not None:
					try:
						fields[field_name] += f' DEFAULT {field.default}'
					except KeyError:
						fields[field_name] = f'{field.to_sql_type()} DEFAULT {field.default}'
				else:
					fields[field_name] = f'{field.to_sql_type()}'

		self._database_repository.create_table(instance.__tablename__, fields)

	def get(self, model_class: Type['Model'], **kwargs) -> 'Model':
		table_name = self._get_table_name(model_class)
		result = self._database_repository.read(table_name, kwargs)

		if result:
			return model_class(database_connection=self._database_repository._connection, **result[0])
		else:
			return None

	def filter(self, model_class: Type['Model'], **kwargs) -> Tuple['Model']:
		table_name = self._get_table_name(model_class)
		results = self._database_repository.read(table_name, kwargs)
		return tuple(model_class(database_connection=self._database_repository._connection, **row) for row in results)

	def all(self, model_class: Type['Model']) -> Tuple['Model']:
		table_name = self._get_table_name(model_class)
		results = self._database_repository.read(table_name, {})
		return tuple(model_class(database_connection=self._database_repository._connection, **row) for row in results)

	def create(self, instance: 'Model'):
		table_name = self._get_table_name(instance)
		data = {field: getattr(instance, field) for field in instance._fields if field != instance._primary_key}
		self._database_repository.create(table_name, data)

	def update(self, instance: 'Model') -> None:
		table_name = self._get_table_name(instance)
		data = {field: getattr(instance, field) for field in instance._fields if field != instance._primary_key}

	def save(self, instance: 'Model') -> None:
		table_name = self._get_table_name(instance)
		data = {field: getattr(instance, field) for field in instance._fields}
		self._database_repository.create(table_name, data)

	def delete(self, instance: 'Model') -> None:
		table_name = self._get_table_name(instance)
		self._database_repository.delete(table_name, getattr(instance, instance._primary_key))

	def update_field(self, instance, field_name, new_value):
		table_name = self._get_table_name(instance)
		self._database_repository.update_field(table_name, getattr(instance, instance._primary_key), field_name, new_value)
		self.update(instance)


class Model(metaclass=ProxyObjectMeta):
	database_connection: DatabaseConnection = None
	_model_manager: ModelManager = None
	__tablename__: str = None

	def __new__(cls, *args, **kwargs):
		instance = super().__new__(cls)
		instance.database_connection = kwargs.get('database_connection')
		instance.model_manager = kwargs.get('model_manager')

		return instance

	def __init__(self, database_connection, **kwargs):
		self.database_connection: DatabaseConnection = None
		self._model_manager: 'ModelManager' = ModelManager(database_connection)

		for field_name, field in self._fields.items():
			value = kwargs.get(field_name, None)

			if field_name == self._primary_key:
				if field.auto_increment and value is None:
					value = field.default;

			if value is not None and field.validate(value):
				setattr(self, field_name, field.to_db_value(value))
			else:
				setattr(self, field_name, field.default)

	def save(self) -> None:
		self._model_manager.create(self)

	def update_field(self, field_name: str, new_value: Any):
		setattr(self, field_name, new_value)
		self._model_manager.update_field(self, field_name, new_value)

	def delete(self) -> None:
		self._model_manager.delete(self)

	@property
	def pk(self) -> Any:
		return getattr(self, self._primary_key)

	@classmethod
	def get(cls, **kwargs) -> 'Model':
		return cls.object.get(**kwargs)

	@classmethod
	def filter(cls, **kwargs) -> Tuple['Model']:
		return cls.object.filter(**kwargs)

	@classmethod
	def all(cls) -> Tuple['Model']:
		return cls.object.all()

	@property
	def object(self) -> 'Object':
		return self.__class__._proxy_object

	def view_table_info(self):
		table = Table(title=f'Model {self}')

		table.add_column("Field name", style="blue")
		table.add_column('Field', style='green')

		for field_name, field in self._fields.items():
			table.add_row(str(field_name), str(field))

		console = Console()
		console.print(table)
