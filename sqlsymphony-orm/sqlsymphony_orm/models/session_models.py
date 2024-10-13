from pathlib import Path
from typing import List, Any, Dict, Tuple, Callable
from uuid import uuid4
from abc import ABC, abstractmethod
from collections import OrderedDict

from loguru import logger

from sqlsymphony_orm.database.manager import SQLiteMultiManager
from sqlsymphony_orm.constants import RESTRICTIED_FIELDS
from sqlsymphony_orm.datatypes.fields import BaseDataType, IntegerField
from sqlsymphony_orm.exceptions import (
	PrimaryKeyError,
	FieldValidationError,
	NullableFieldError,
	FieldNamingError,
)
from sqlsymphony_orm.utils.auditing import (
	AuditManager,
	InMemoryAuditStorage,
	BasicChangeObserver,
)
from sqlsymphony_orm.utils.auditing import (
	AuditManager,
	InMemoryAuditStorage,
	BasicChangeObserver,
)


class MetaSessionModel(type):
	"""
	This class describes a meta session model.
	"""

	__tablename__ = None

	def __new__(cls, class_object: "SessionModel", parents: tuple, attributes: dict):
		"""
		Magic method for creating instances and classes

		:param		cls:		   The cls
		:type		cls:		   cls
		:param		class_object:  The class object
		:type		class_object:  Model
		:param		parents:	   The parents
		:type		parents:	   tuple
		:param		attributes:	   The attributes
		:type		attributes:	   dict

		:returns:	new class
		:rtype:		model
		"""
		new_class = super(MetaSessionModel, cls).__new__(
			cls, class_object, parents, attributes
		)
		fields = OrderedDict()

		setattr(new_class, "_model_name", attributes["__qualname__"].lower())

		if new_class.__tablename__ is None:
			setattr(new_class, "table_name", attributes["__qualname__"].lower())
		else:
			setattr(new_class, "table_name", new_class.__tablename__)

		for k, v in attributes.items():
			if isinstance(v, BaseDataType):
				fields[k] = v
				attributes[k] = None

		setattr(new_class, "_original_fields", fields)

		return new_class


class SessionModel(metaclass=MetaSessionModel):
	"""
	This class describes a ORM model.
	"""

	__tablename__ = None
	_ids = 0

	def __init__(self, **kwargs):
		"""
		Constructs a new instance.

		:param		kwargs:	 The keywords arguments
		:type		kwargs:	 dictionary
		"""
		self.fields = {}

		self.unique_id = str(uuid4())

		for field_name, field in self._original_fields.items():
			value = kwargs.get(field_name, None)

			if field_name in RESTRICTIED_FIELDS:
				raise FieldNamingError(
					f"The field named {field_name} is prohibited to avoid naming errors. Please try a different name. List of restricted names: {RESTRICTIED_FIELDS}"
				)

			if not kwargs.get("manager", False):
				if not field.null and value is None and field.default is None:
					raise NullableFieldError(
						f"Field {field_name} is set to NOT NULL, but it is empty"
					)

			if value is not None and field.validate(value):
				setattr(self, field_name, field.to_db_value(value))
				self.fields[field_name] = getattr(self, field_name)
			else:
				if value is not None and not field.validate(value):
					raise FieldValidationError(
						f'Validate error: field {field}; field name "{field_name}"; value "{value}"'
					)

				if isinstance(field, IntegerField):
					if field.primary_key:
						self.__class__._ids += 1
						setattr(
							self,
							"_primary_key",
							{
								"field": field,
								"field_name": field_name,
								"value": self.__class__._ids,
							},
						)

				setattr(self, field_name, field.default)
				self.fields[field_name] = getattr(self, field_name)

		if not getattr(self, "_primary_key"):
			raise PrimaryKeyError()

		self._last_action = {}

	@property
	def pk(self) -> Any:
		"""
		Get primary key value

		:returns:	primary key value
		:rtype:		primary key
		"""
		return self._primary_key["value"]

	def view_table_info(self):
		"""
		View info about Model in table
		"""
		table = Table(title=f"Model {self._model_name} (table {self.table_name})")

		table.add_column("Field name", style="blue")
		table.add_column("Field class", style="cyan")
		table.add_column("SQL Field", style="magenta")
		table.add_column("Value", style="green")

		for k, v in self.get_formatted_sql_fields().items():
			table.add_row(
				str(k), str(self._original_fields[k]), str(v), str(self.fields[str(k)])
			)

		console = Console()
		console.print(table)

	def get_formatted_sql_fields(self) -> dict:
		"""
		Gets the formatted sql fields.

		:returns:	The formatted sql fields.
		:rtype:		dict
		"""
		model_fields = {}

		for field_name, field in self._original_fields.items():
			model_fields[field_name] = field.to_sql_type()
			if field.primary_key:
				model_fields[field_name] = f"{field.to_sql_type()} PRIMARY KEY"
			else:
				if not field.null:
					try:
						model_fields[field_name] += " NOT NULL"
					except KeyError:
						model_fields[field_name] = f"{field.to_sql_type()} NOT NULL"
				if field.unique:
					try:
						model_fields[field_name] += " UNIQUE"
					except KeyError:
						model_fields[field_name] = f"{field.to_sql_type()} UNIQUE"
				if field.default is not None:
					try:
						model_fields[field_name] += f" DEFAULT {field.default}"
					except KeyError:
						model_fields[field_name] = (
							f"{field.to_sql_type()} DEFAULT {field.default}"
						)

		return model_fields


class Session(ABC):
	@abstractmethod
	def add(self, model: SessionModel):
		raise NotImplementedError()

	@abstractmethod
	def update(self, model: SessionModel, **kwargs):
		raise NotImplementedError()

	@abstractmethod
	def delete(self, model: SessionModel):
		raise NotImplementedError()

	@abstractmethod
	def commit(self):
		raise NotImplementedError()


class SQLiteSession(Session):
	def __init__(self, database_file: str):
		self.database_file = Path(database_file)
		self.models = {}
		self.manager = SQLiteMultiManager(self.database_file)
		self.audit_manager = AuditManager(InMemoryAuditStorage())
		self.audit_manager.attach(BasicChangeObserver())

	def reconnect(self):
		self.manager.reconnect()

	def get_all(self):
		models_instances = [self.models[model]['model'] for model in self.models.keys()]
		return models_instances

	def get_all_by_module(self, needed_model: SessionModel):
		all_instances = [self.models[model]['model'] for model in self.models.keys()]
		needed_instances = []
		model_name = needed_model._model_name

		for model in all_instances:
			if model._model_name == model_name:
				needed_instances.append(model)

		return needed_instances

	def drop_table(self, table_name: str):
		self.manager.drop_table(table_name)

	def filter(self, query: 'QueryBuilder', first: bool=False):
		db_results = self.manager.filter(str(query))
		results = []
		fields = {}

		for unique_id, curr_model in self.models.items():
			model = curr_model['model']
			fields[unique_id] = {
				'keys': model._original_fields.keys(),
				'values': [getattr(model, value) if model._primary_key['field_name'] != value else model.pk for value in model._original_fields.keys()]
			}

		for result in db_results:
			for unique_id, data in fields.items():
				if len(data['keys']) == len(result):
					if tuple(data['values']) == result:
						results.append(self.models[unique_id]['model'])

		return results[0] if first else results

	def update(self, model: SessionModel, **kwargs):
		current_model = self.models.get(model.unique_id, None)

		if current_model is None:
			self.add(model)

		for key, value in kwargs.items():
			if hasattr(model, key):
				if value is not None and model._original_fields[key].validate(value):
					orig_field = getattr(model, key)
					setattr(model, key, model._original_fields[key].to_db_value(value))
					self.audit_manager.track_changes(
						model._model_name,
						model.table_name,
						model.pk,
						key,
						orig_field,
						value,
					)
					self.manager.update(model.table_name, key, orig_field, value)
					self.audit_manager.track_changes(
						model._model_name,
						model.table_name,
						model.pk,
						key,
						orig_field,
						value,
					)
					logger.info(
						f"[{model.table_name}] Update {model._model_name}#{model.pk} {key}: {orig_field} -> {value}"
					)

		self.models[model.unique_id]['model'] = model

	def add(self, model: SessionModel, ignore: bool=False):
		if self.models.get(model.unique_id, None) is not None:
			logger.warning(f'Model {model.unique_id} already added')
			return

		self.models[model.unique_id] = {
			'model': model
		}

		self.audit_manager.track_changes(model._model_name, model.table_name, 
									model.unique_id, 'save', "NONE", model._model_name)

		self.manager.create_table(model.table_name, model.get_formatted_sql_fields())
		self.manager.insert(model.table_name, model.get_formatted_sql_fields(), model.pk, model, ignore)

	def delete(self, model: SessionModel):
		current_model = self.models.get(model.unique_id, None)

		if current_model is None:
			logger.error(f'Model {model.unique_id} does not exists')
			return

		self.audit_manager.track_changes(
			current_model['model']._model_name,
			current_model['model'].table_name,
			current_model['model'].pk,
			current_model['model'].table_name,
			current_model['model']._model_name,
			"<DELETED>",
		)

		self.manager.delete(current_model['model'].table_name, current_model['model']._primary_key["field_name"], current_model['model'].pk)

	def commit(self):
		for _, model in self.models.items():
			self.manager.commit()

	def close(self):
		for _, model in self.models.items():
			self.manager.close_connection()
