from pathlib import Path
from typing import List, Any, Union, Callable
from uuid import uuid4
from abc import ABC, abstractmethod
from collections import OrderedDict

from loguru import logger

from sqlsymphony_orm.database.manager import SQLiteMultiManager
from sqlsymphony_orm.constants import RESTRICTED_FIELDS
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
from sqlsymphony_orm.queries import QueryBuilder


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

				if isinstance(v, IntegerField):
					if v.primary_key:
						setattr(new_class, "_pk_name", k)

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
		self.hooks = {}

		self.unique_id = str(uuid4())

		for field_name, field in self._original_fields.items():
			value = kwargs.get(field_name, None)

			if field_name in RESTRICTED_FIELDS:
				raise FieldNamingError(
					f"The field named {field_name} is prohibited to avoid naming errors. Please try a different name. List of restricted names: {RESTRICTED_FIELDS}"
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

	def add_hook(self, before_action: str, func: Callable, func_args: tuple = ()):
		"""
		Adds a hook.

		:param		before_action:	The before action
		:type		before_action:	str
		:param		func:			The function
		:type		func:			Callable
		:param		func_args:		The function arguments
		:type		func_args:		tuple

		:raises		ValueError:		unknown before action
		"""
		actions = ["save", "delete", "update"]

		if before_action.lower() not in actions:
			raise ValueError(
				f"Unknown action: {before_action}. Supported actions: {actions}"
			)

		logger.info(
			f"[{self.table_name}] Add Model Hook: before {before_action} execute {func.__name__}"
		)

		self.hooks[before_action.lower()] = {"function": func, "args": func_args}

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

	@classmethod
	def _class_get_formatted_sql_fields(cls, skip_primary_key: bool = False) -> dict:
		"""
		Gets the formatted sql fields.

		:returns:	The formatted sql fields.
		:rtype:		dict
		"""
		model_fields = {}

		for field_name, field in cls._original_fields.items():
			if field.primary_key and skip_primary_key:
				continue

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

	def get_formatted_sql_fields(self, skip_primary_key: bool = False) -> dict:
		"""
		Gets the formatted sql fields.

		:returns:	The formatted sql fields.
		:rtype:		dict
		"""
		model_fields = {}

		for field_name, field in self._original_fields.items():
			if field.primary_key and skip_primary_key:
				continue

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
	"""
	This class describes a session.
	"""

	@abstractmethod
	def reconnect(self):
		"""
		reconnect to database
		"""
		raise NotImplementedError

	@abstractmethod
	def get_all(self):
		"""
		Gets all models
		"""
		raise NotImplementedError

	@abstractmethod
	def get_all_by_model(self, needed_model: SessionModel):
		"""
		Gets all models by module.

		:param		needed_model:  The needed model
		:type		needed_model:  SessionModel
		"""
		raise NotImplementedError

	@abstractmethod
	def drop_table(self, table_name: str):
		"""
		drop table

		:param		table_name:	 The table name
		:type		table_name:	 str
		"""
		raise NotImplementedError

	@abstractmethod
	def filter(self, query: "QueryBuilder", first: bool = False):
		"""
		Filter and get models by query

		:param		query:	The query
		:type		query:	QueryBuilder
		:param		first:	The first
		:type		first:	bool
		"""
		raise NotImplementedError

	@abstractmethod
	def update(self, model: SessionModel, **kwargs):
		"""
		Update model

		:param		model:	 The model
		:type		model:	 SessionModel
		:param		kwargs:	 The keywords arguments
		:type		kwargs:	 dictionary
		"""
		raise NotImplementedError

	@abstractmethod
	def add(self, model: SessionModel, ignore: bool = False):
		"""
		Add model

		:param		model:	 The model
		:type		model:	 SessionModel
		:param		ignore:	 The ignore
		:type		ignore:	 bool
		"""
		raise NotImplementedError

	@abstractmethod
	def delete(self, model: SessionModel):
		"""
		Deletes the given model.

		:param		model:	The model
		:type		model:	SessionModel
		"""
		raise NotImplementedError

	@abstractmethod
	def commit(self):
		"""
		Commit changes
		"""
		raise NotImplementedError

	@abstractmethod
	def close(self):
		"""
		Close connection
		"""
		raise NotImplementedError


class SQLiteSession(Session):
	"""
	This class describes a sqlite session.
	"""

	def __init__(self, database_file: str):
		"""
		Constructs a new instance.

		:param		database_file:	The database file
		:type		database_file:	str
		"""
		self.database_file = Path(database_file)
		self.models = {}
		self.manager = SQLiteMultiManager(self.database_file)
		self.audit_manager = AuditManager(InMemoryAuditStorage())
		self.audit_manager.attach(BasicChangeObserver())

	def reconnect(self, database_file: str = None):
		"""
		Reconnecto to database
		"""
		if database_file is not None:
			self.database_file = Path(database_file)
		logger.info(f"Session {self.database_file}: reconnect")
		self.manager.reconnect(database_file)

	def execute(
		self, raw_sql_query: str, values: tuple = (), get_cursor: bool = False
	) -> list:
		"""
		Execute raw sql query

		:param		raw_sql_query:	The raw sql query
		:type		raw_sql_query:	str
		:param		values:			The values
		:type		values:			tuple
		:param		get_cursor:		The get cursor
		:type		get_cursor:		bool

		:returns:	list with output data
		:rtype:		list
		"""
		return self.manager.execute(raw_sql_query, values, get_cursor)

	def get_all(self) -> List[SessionModel]:
		"""
		Gets all.

		:returns:	All.
		:rtype:		List[SessionModel]
		"""
		models_instances = [self.models[model]["model"] for model in self.models.keys()]
		return models_instances

	def get_all_by_model(self, needed_model: SessionModel) -> List[SessionModel]:
		"""
		Gets all by module.

		:param		needed_model:  The needed model
		:type		needed_model:  SessionModel

		:returns:	All by module.
		:rtype:		List[SessionModel]
		"""
		all_instances = [self.models[model]["model"] for model in self.models.keys()]
		needed_instances = []
		model_name = needed_model._model_name

		for model in all_instances:
			if model._model_name == model_name:
				needed_instances.append(model)

		if len(needed_instances) < 1:
			models_tuple = self.manager.filter(
				str(QueryBuilder().SELECT("*").FROM(needed_model.table_name))
			)
			if len(models_tuple) < 1:
				return
			fields = [
				{
					f"{field_name}": models_tuple[i][num]
					if not needed_model._original_fields[field_name].primary_key
					else "<PRIMARYKEY>"
					for num, field_name in enumerate(
						needed_model._original_fields.keys()
					)
				}
				for i in range(len(models_tuple))
			]
			models = []

			for i in range(len(fields)):
				prim_key = [
					field if field_val == "<PRIMARYKEY>" else False
					for field, field_val in fields[i].items()
				]
				if prim_key[0]:
					del fields[i][prim_key[0]]
				models.append(needed_model(**fields[i]))

			return models

		return needed_instances

	def drop_table(self, table_name: str):
		"""
		Drop table

		:param		table_name:	 The table name
		:type		table_name:	 str
		"""
		logger.info(f"Session {self.database_file}: drop table {table_name}")
		self.manager.drop_table(table_name)

	def filter(
		self, query: "QueryBuilder", first: bool = False
	) -> Union[List[SessionModel], SessionModel]:
		"""
		Filter and get model by query

		:param		query:	The query
		:type		query:	QueryBuilder
		:param		first:	The first
		:type		first:	bool

		:returns:	list with SessionModel or SessionModel
		:rtype:		Union[List[SessionModel], SessionModel]
		"""
		db_results = self.manager.filter(str(query))
		results = []
		fields = {}

		for unique_id, curr_model in self.models.items():
			model = curr_model["model"]
			fields[unique_id] = {
				"keys": model._original_fields.keys(),
				"values": [
					getattr(model, value)
					if model._primary_key["field_name"] != value
					else model.pk
					for value in model._original_fields.keys()
				],
			}

		for result in db_results:
			for unique_id, data in fields.items():
				if len(data["keys"]) == len(result):
					if tuple(data["values"]) == result:
						results.append(self.models[unique_id]["model"])

		if results:
			return results[0] if first else results
		else:
			return None

	def update(self, model: SessionModel, **kwargs):
		"""
		Update model

		:param		model:	 The model
		:type		model:	 SessionModel
		:param		kwargs:	 The keywords arguments
		:type		kwargs:	 dictionary
		"""
		current_model = self.models.get(model.unique_id, None)

		if current_model is None:
			self.add(model)

		logger.info(f"Session {self.database_file}: update model {model.unique_id}")

		if model.hooks:
			func = model.hooks["update"]["function"]
			logger.debug(f"Exec Model Hook[update]: {func.__name__}")
			func(*model.hooks["update"]["args"])

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

		self.models[model.unique_id]["model"] = model

	def add(self, model: SessionModel, ignore: bool = False):
		"""
		Add new model

		:param		model:	 The model
		:type		model:	 SessionModel
		:param		ignore:	 The ignore
		:type		ignore:	 bool
		"""
		if self.models.get(model.unique_id, None) is not None:
			logger.warning(f"Model {model.unique_id} already added")
			return

		if model.hooks:
			func = model.hooks["save"]["function"]
			logger.debug(f"Exec Model Hook[save]: {func.__name__}")
			func(*model.hooks["save"]["args"])

		self.models[model.unique_id] = {"model": model}

		self.audit_manager.track_changes(
			model._model_name,
			model.table_name,
			model.unique_id,
			"save",
			"NONE",
			model._model_name,
		)

		formatted_fields = model.get_formatted_sql_fields(skip_primary_key=True)

		self.manager.create_table(model.table_name, model.get_formatted_sql_fields())

		self.manager.insert(model.table_name, formatted_fields, model.pk, model, ignore)

		last_pk = self.execute(
			f'SELECT max({model._primary_key["field_name"]}) FROM {model.table_name}'
		)

		model._primary_key["value"] = int(last_pk[0][0])

		logger.info(
			f"Session {self.database_file}: insert new model: {model.unique_id}"
		)

	def delete(self, model: SessionModel):
		"""
		Deletes the given model.

		:param		model:	The model
		:type		model:	SessionModel
		"""
		current_model = self.models.get(model.unique_id, None)

		if current_model is None:
			logger.error(f"Model {model.unique_id} does not exists")
			return

		if model.hooks:
			func = model.hooks["delete"]["function"]
			logger.debug(f"Exec Model Hook[delete]: {func.__name__}")
			func(*model.hooks["delete"]["args"])

		self.audit_manager.track_changes(
			current_model["model"]._model_name,
			current_model["model"].table_name,
			current_model["model"].pk,
			current_model["model"].table_name,
			current_model["model"]._model_name,
			"<DELETED>",
		)

		self.manager.delete(
			current_model["model"].table_name,
			current_model["model"]._primary_key["field_name"],
			current_model["model"].pk,
		)

		logger.info(f"Session {self.database_file}: delete model: {model.unique_id}")

	def commit(self):
		"""
		Commit changes
		"""
		self.manager.commit()

	def close(self):
		"""
		Close connection
		"""
		self.manager.close_connection()
