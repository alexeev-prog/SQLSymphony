from typing import Optional, Union
from abc import ABC, abstractmethod
import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from sqlsymphony_orm.models.session_models import SQLiteSession
from sqlsymphony_orm.exceptions import MigrationError
from loguru import logger


class MigrationManager(ABC):
	@abstractmethod
	def get_current_table_columns(self, table_name: str):
		raise NotImplementedError()

	@abstractmethod
	def get_table_columns_from_model(self, model: "Model"):
		raise NotImplementedError()

	@abstractmethod
	def revert_migration(self, index_key: int = -1):
		raise NotImplementedError()


class SQLiteMigrationManager(MigrationManager):
	"""
	This class describes a sqlite migration manager.
	"""

	def __init__(self, session: SQLiteSession, migrations_dir: str = "migrations"):
		"""
		Constructs a new instance.

		:param		session:		 The session
		:type		session:		 SQLiteSession
		:param		migrations_dir:	 The migrations dir
		:type		migrations_dir:	 str
		"""
		self.session = session
		self.migrations_dir = migrations_dir
		os.makedirs(self.migrations_dir, exist_ok=True)
		self.migrations = {}
		self.migrations_file = "sqlsymphony_migrates.json"

	def get_current_table_columns(self, table_name: str) -> list:
		"""
		Gets the current table columns.

		:param		table_name:	 The table name
		:type		table_name:	 str

		:returns:	The current table columns.
		:rtype:		list
		"""
		data = self.session.execute(f"SELECT * FROM {table_name}", get_cursor=True)
		cursor = data[0]
		fieldnames = [field[0] for field in cursor.description]

		return fieldnames

	def get_table_columns_from_model(self, model: "Model") -> list:
		"""
		Gets the table columns from model.

		:param		model:	The model
		:type		model:	Model

		:returns:	The table columns from model.
		:rtype:		list
		"""
		return [key for key in model._original_fields.keys()]

	def migrate_from_model(
		self,
		old_model: Union["SessionModel", "Model"],
		new_model: Union["SessionModel", "Model"],
		original_table_name: str,
		new_table_name: Optional[str] = None,
	):
		"""
		Migrate from old model to new model

		:param		old_model:			  The old model
		:type		old_model:			  Union["SessionModel", "Model"]
		:param		new_model:			  The new model
		:type		new_model:			  Union["SessionModel", "Model"]
		:param		original_table_name:  The original table name
		:type		original_table_name:  str
		:param		new_table_name:		  The new table name
		:type		new_table_name:		  Optional[str]

		:raises		MigrationError:		  fields error
		"""
		sql_queries = []

		logger.info("Start database migrating")

		if new_table_name is not None:
			sql_queries.append(
				f"ALTER TABLE {original_table_name} RENAME TO {new_table_name};"
			)
			logger.debug(
				f"Change table name: {original_table_name} -> {new_table_name}"
			)
			new_model.table_name = new_table_name
			original_table_name = new_table_name

		old_fields = set(
			[
				f"{field_name} {field_params}"
				for field_name, field_params in old_model._class_get_formatted_sql_fields(
					skip_primary_key=False
				).items()
			]
		)
		new_fields = set(
			[
				f"{field_name} {field_params}"
				for field_name, field_params in new_model._class_get_formatted_sql_fields(
					skip_primary_key=False
				).items()
			]
		)
		added = new_fields - old_fields
		dropped = old_fields - new_fields

		for field_name in dropped:
			logger.debug(
				f'Drop column {field_name.split(" ")[0]} from table {original_table_name}'
			)
			sql_queries.append(
				f"ALTER TABLE {original_table_name} DROP COLUMN {field_name.split(" ")[0]};"
			)

		for field in added:
			if "NOT NULL" in field and "DEFAULT" not in field:
				raise MigrationError(
					f'Cannot script a "not null" field without default value in field "{field}"'
				)
			logger.debug(f"Add column {field} to {original_table_name}")
			sql_queries.append(f"ALTER TABLE {original_table_name} ADD COLUMN {field};")

		migrationfile = os.path.join(
			self.migrations_dir,
			f'{datetime.now().strftime("backup_%Y%m%d%H%M%S")}_{self.session.database_file}',
		)
		logger.debug(f"Create migraton file: {migrationfile}")
		shutil.copyfile(self.session.database_file, migrationfile)

		if Path(self.migrations_file).exists():
			logger.debug(f"Load JSON migrations history file: {self.migrations_file}")
			with open(self.migrations_file, "r") as read_file:
				self.migrations = json.load(read_file)

		self.migrations[str(len(self.migrations) + 1)] = {
			"migrationfile": migrationfile,
			"tablename": original_table_name,
			"description": f"from {old_model._model_name} to {new_model._model_name}",
			"sql_queries": list(sql_queries),
			"new_fields": list(new_fields),
			"old_fields": list(old_fields),
			"added": list(added),
			"dropped": list(dropped),
		}

		with open(self.migrations_file, "w") as write_file:
			logger.debug(f"Update JSON migrations history file: {self.migrations_file}")
			json.dump(self.migrations, write_file, indent=4)

		for sql_query in sql_queries:
			logger.debug(f"[Migration] Execute sql query: {sql_query}")
			self.session.execute(sql_query)

	def revert_migration(self, index_key: int = -1):
		"""
		Revert migration

		:param		index_key:	The index key
		:type		index_key:	int
		"""
		with open(self.migrations_file, "r") as read_file:
			logger.debug(f"Load JSON migrations history file: {self.migrations_file}")
			self.migrations = json.load(read_file)

		if index_key == -1:
			index_key = [k for k in self.migrations.keys()][-1]

		try:
			migration = self.migrations[str(index_key)]
		except KeyError as ke:
			logger.error(f"Cannot get migration by index {index_key}: {ke}")

		logger.info("Rollback database from new to old.")
		shutil.copyfile(migration["migrationfile"], self.session.database_file)
