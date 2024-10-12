from typing import Any, Callable
from uuid import uuid4
from collections import OrderedDict
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich import print

from loguru import logger

from sqlsymphony_orm.datatypes.fields import BaseDataType, IntegerField
from sqlsymphony_orm.database.manager import SQLiteModelManager
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

RESTRICTIED_FIELDS: list = [
	"__new__",
	"__init__",
	"__str__",
	"__repr__",
	"pk",
	"view_table_info",
	"save",
	"update",
	"delete",
	"_get_formatted_sql_fields",
	"objects",
	"_original_fields",
	"_database_name",
	"_model_name",
	"_table_name",
	"__tablename__",
	"__database__",
	"fields",
	"_unique_id",
]


class MetaModel(type):
	"""
	This class describes a meta model.
	"""

	__tablename__ = None
	__database__ = None

	def __new__(cls, class_object: "Model", parents: tuple, attributes: dict):
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
		new_class = super(MetaModel, cls).__new__(
			cls, class_object, parents, attributes
		)
		fields = OrderedDict()

		setattr(new_class, "_model_name", attributes["__qualname__"].lower())

		if new_class.__tablename__ is None:
			setattr(new_class, "_table_name", attributes["__qualname__"].lower())
		else:
			setattr(new_class, "_table_name", new_class.__tablename__)

		if new_class.__database__ is None:
			setattr(
				new_class, "_database_name", f"{attributes['__qualname__'].lower()}.db"
			)
		else:
			setattr(new_class, "_database_name", new_class.__database__)

		for k, v in attributes.items():
			if isinstance(v, BaseDataType):
				fields[k] = v
				attributes[k] = None

		setattr(new_class, "_original_fields", fields)

		setattr(
			new_class,
			"objects",
			SQLiteModelManager(new_class, new_class._database_name),
		)

		return new_class


class Model(metaclass=MetaModel):
	"""
	This class describes a ORM model.
	"""

	__tablename__ = None
	__database__ = None
	_ids = 0

	def __init__(self, **kwargs):
		"""
		Constructs a new instance.

		:param		kwargs:	 The keywords arguments
		:type		kwargs:	 dictionary
		"""
		self.fields = {}
		self.hooks = {}
		self.audit_manager = AuditManager(InMemoryAuditStorage())
		self.audit_manager.attach(BasicChangeObserver())

		self.objects.create_table(self._table_name, self._get_formatted_sql_fields())

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

		self.last_action = {}

	@property
	def pk(self) -> Any:
		"""
		Get primary key value

		:returns:   primary key value
		:rtype:     primary key
		"""
		return self._primary_key["value"]

	def commit(self):
		"""
		Commit changes
		"""
		logger.info(f"[{self._table_name}] Commit changes...")
		self.objects.commit()

	def get_audit_history(self) -> list:
		"""
		Get audit history

		:returns:   The audit history.
		:rtype:     List[AuditEntry]
		"""
		return self.audit_manager.get_audit_history(
			self._model_name, self._table_name, self.pk
		)

	def view_table_info(self):
		"""
		View info about Model in table
		"""
		table = Table(title=f"Model {self._model_name} (table {self._table_name})")

		table.add_column("Field name", style="blue")
		table.add_column("Field class", style="cyan")
		table.add_column("SQL Field", style="magenta")
		table.add_column("Value", style="green")

		for k, v in self._get_formatted_sql_fields().items():
			table.add_row(
				str(k), str(self._original_fields[k]), str(v), str(self.fields[str(k)])
			)

		console = Console()
		console.print(table)

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
			f"[{self._table_name}] Add Model Hook: before {before_action} execute {func.__name__}"
		)

		self.hooks[before_action.lower()] = {"function": func, "args": func_args}

	def save(self, ignore: bool = False):
		"""
		CRUD function: save
		"""
		fields = []
		values = []

		if self.hooks:
			func = self.hooks["save"]["function"]
			logger.debug(f"Exec Model Hook[save]: {func.__name__}")
			func(*self.hooks["save"]["args"])

		for k, v in self._get_formatted_sql_fields().items():
			fields.append(k)
			if "PRIMARY KEY" in v:
				values.append(self._primary_key["value"])
			else:
				values.append(getattr(self, k))

		columns = ", ".join(fields)
		count = ", ".join(["?" for _ in values])

		try:
			self.objects.insert(self._table_name, columns, count, tuple(values), ignore)
		except Exception as ex:
			print(
				f'An exception occurred: "{ex}". We save changes to the database using commit...'
			)
			raise ex

	def update(self, **kwargs):
		"""
		Update sql query

		:param		kwargs:	 The keywords arguments
		:type		kwargs:	 dictionary
		"""
		for key, value in kwargs.items():
			if hasattr(self, key):
				if value is not None and self._original_fields[key].validate(value):
					orig_field = getattr(self, key)
					setattr(self, key, self._original_fields[key].to_db_value(value))
					self.objects.update(self._table_name, key, orig_field, value)
					self.audit_manager.track_changes(
						self._model_name,
						self._table_name,
						self.pk,
						key,
						orig_field,
						value,
					)
					logger.info(
						f"[{self._table_name}] Update {self._model_name}#{self.pk} {key}: {orig_field} -> {value}"
					)

	def delete(self, field_name: str = None, field_value: Any = None):
		"""
		Delete model

		:param		field_name:	  The field name
		:type		field_name:	  str
		:param		field_value:  The field value
		:type		field_value:  Any
		"""
		if field_name is not None and field_value is not None:
			logger.info(
				f"[{self._table_name}] Delete model by {field_name}={field_value}"
			)
			self.objects.delete(self._table_name, field_name, field_value)
			return

		logger.info(
			f'[{self._table_name}] Delete model {self._primary_key["field_name"]}={self.pk}'
		)
		self.objects.delete(self._table_name, self._primary_key["field_name"], self.pk)
		self.audit_manager.track_changes(
			self._model_name,
			self._table_name,
			self.pk,
			self._table_name,
			self._model_name,
			"<DELETED>",
		)
		self.last_action["type"] = "DELETE"
		self.last_action["timestamp"] = datetime.now()

	def rollback_last_action(self):
		"""
		Rollback (revert) last action
		"""
		if not self.last_action:
			return

		if self.last_action["type"] == "DELETE":
			logger.info("Rollback last action: delete")
			self.audit_manager.revert_changes(
				self._model_name,
				self._table_name,
				self.pk,
				self._table_name,
				self.last_action["timestamp"],
			)
			self.save()
			self.last_action = {}
		else:
			logger.error(f'Unknown last action type: {self.last_action["type"]}')
			return

	def _get_formatted_sql_fields(self) -> dict:
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
