from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from rich.console import Console
from rich.table import Table


class BaseDataType(ABC):
	"""
	This class describes a base data type.
	"""

	def __init__(
		self,
		primary_key: bool = False,
		unique: bool = False,
		null: bool = True,
		default: Any = None,
	):
		"""
		Constructs a new instance.

		:param		primary_key:  The primary key
		:type		primary_key:  bool
		:param		unique:		  The unique
		:type		unique:		  bool
		:param		null:		  The null
		:type		null:		  bool
		:param		default:	  The default
		:type		default:	  Any
		"""
		self.primary_key: bool = primary_key
		self.unique: bool = unique
		self.null: bool = null
		self.default: Any = default

	@abstractmethod
	def validate(self, value: Any) -> bool:
		"""
		Validate value for current datatype

		:param		value:	The value
		:type		value:	Any

		:returns:	if the value is verified then True, otherwise False
		:rtype:		bool
		"""
		raise NotImplementedError()

	@abstractmethod
	def to_db_value(self, value: Any) -> Any:
		"""
		convert to db value

		:param		value:	The value
		:type		value:	Any

		:returns:	db value
		:rtype:		Any
		"""
		raise NotImplementedError()

	@abstractmethod
	def from_db_value(self, value: Any) -> Any:
		"""
		convert from db value

		:param		value:	The value
		:type		value:	Any

		:returns:	db value
		:rtype:		Any
		"""
		raise NotImplementedError()

	@abstractmethod
	def view_table_info(self):
		"""
		View info in table view
		"""
		table = Table(title="SQLSymphonyORM BaseDataType")
		table.add_column("Parameters", style="blue")
		table.add_column("Parameters values", style="green")

		table.add_row("UNIQUE", str(self.unique))
		table.add_row("NULL", str(self.null))
		table.add_row("DEFAULT", str(self.default))
		table.add_row("FIELD", str(self.field))
		table.add_row("PRIMARY KEY", str(self.primary_key))

		console = Console()
		console.print(table)

	@abstractmethod
	def to_sql_type(self) -> str:
		raise NotImplementedError()

	def __str__(self):
		return "<BaseDataType>"


@dataclass
class IntegerField(BaseDataType):
	"""
	This class describes an integer field.
	"""

	def __init__(
		self,
		auto_increment: bool = False,
		max_value: int = None,
		min_value: int = None,
		primary_key: bool = False,
		unique: bool = False,
		null: bool = True,
		default: int = None,
	):
		"""
		Constructs a new instance.

		:param		primary_key:  The primary key
		:type		primary_key:  bool
		:param		unique:		  The unique
		:type		unique:		  bool
		:param		null:		  The null
		:type		null:		  bool
		:param		default:	  The default
		:type		default:	  int
		"""
		self.primary_key = primary_key
		self.unique: bool = unique
		self.null: bool = null
		self.default: int = default
		self.auto_increment: bool = auto_increment

		self.min_value = min_value
		self.max_value = max_value

		if self.primary_key and self.default is not None:
			self.value = default
		elif self.primary_key and self.default is None:
			self.value = 0
			self.default = 0

	def validate(self, value: Any) -> bool:
		"""
		Validate value

		:param		value:	The value
		:type		value:	Any

		:returns:	if the value is verified then True, otherwise False
		:rtype:		bool
		"""
		if self.primary_key and self.auto_increment and value is None:
			return True
		if value is None and self.null:
			return True
		if self.min_value is not None and value < self.min_value:
			return False
		if self.max_value is not None and value > self.max_value:
			return False

		return True

	def to_db_value(self, value: Any) -> int:
		"""
		Convert to db value

		:param		value:	The value
		:type		value:	Any

		:returns:	db value
		:rtype:		int
		"""
		if self.primary_key and self.auto_increment and value is None:
			return 0

		return int(value) if value is not None else self.default

	def from_db_value(self, value: Any) -> int:
		"""
		Convert from db value

		:param		value:	The value
		:type		value:	Any

		:returns:	db value
		:rtype:		int
		"""
		return int(value) if value is not None else None

	def view_table_info(self):
		"""
		View info in table view
		"""
		table = Table(title="SQLSymphonyORM IntegerField")
		table.add_column("Parameters", style="blue")
		table.add_column("Parameters values", style="green")

		table.add_row("UNIQUE", str(self.unique))
		table.add_row("NULL", str(self.null))
		table.add_row("DEFAULT", str(self.default))
		table.add_row("PRIMARY KEY", str(self.primary_key))
		table.add_row("MIN VALUE", str(self.min_value))
		table.add_row("MAX VALUE", str(self.max_value))

		console = Console()
		console.print(table)

	def to_sql_type(self) -> str:
		return "INTEGER"

	def __str__(self):
		return "<IntegerField>"


@dataclass
class RealField(BaseDataType):
	"""
	This class describes an real field.
	"""

	def __init__(
		self,
		min_value: float = None,
		max_value: float = None,
		primary_key: bool = False,
		unique: bool = False,
		null: bool = True,
		default: float = None,
	):
		"""
		Constructs a new instance.

		:param		primary_key:  The primary key
		:type		primary_key:  bool
		:param		unique:		  The unique
		:type		unique:		  bool
		:param		null:		  The null
		:type		null:		  bool
		:param		default:	  The default
		:type		default:	  float
		"""
		self.primary_key = primary_key
		self.unique: bool = unique
		self.null: bool = null
		self.default: float = default

		self.min_value = min_value
		self.max_value = max_value

	def validate(self, value: Any) -> bool:
		"""
		Validate value

		:param		value:	The value
		:type		value:	Any

		:returns:	if the value is verified then True, otherwise False
		:rtype:		bool
		"""
		if value is None and self.null:
			return True
		if not isinstance(value, float):
			return False
		if self.min_value is not None and value < self.min_value:
			return False
		if self.max_value is not None and value > self.max_value:
			return False

		return True

	def to_db_value(self, value: Any) -> float:
		"""
		Convert to db value

		:param		value:	The value
		:type		value:	Any

		:returns:	db value
		:rtype:		float
		"""
		return float(value) if value is not None else self.default

	def from_db_value(self, value: Any) -> float:
		"""
		Convert from db value

		:param		value:	The value
		:type		value:	Any

		:returns:	db value
		:rtype:		float
		"""
		return float(value) if value is not None else None

	def view_table_info(self):
		"""
		View info in table view
		"""
		table = Table(title="SQLSymphonyORM RealField")
		table.add_column("Parameters", style="blue")
		table.add_column("Parameters values", style="green")

		table.add_row("UNIQUE", str(self.unique))
		table.add_row("NULL", str(self.null))
		table.add_row("DEFAULT", str(self.default))
		table.add_row("PRIMARY KEY", str(self.primary_key))
		table.add_row("MIN VALUE", str(self.min_value))
		table.add_row("MAX VALUE", str(self.max_value))

		console = Console()
		console.print(table)

	def to_sql_type(self) -> str:
		return "REAL"

	def __str__(self):
		return "<RealField>"


class CharField(BaseDataType):
	"""
	This class describes a character field.
	"""

	def __init__(
		self,
		max_length: int = 64,
		primary_key: bool = False,
		unique: bool = False,
		null: bool = True,
		default: Any = None,
	):
		"""
		Constructs a new instance.

		:param		primary_key:  The primary key
		:type		primary_key:  bool
		:param		unique:		  The unique
		:type		unique:		  bool
		:param		null:		  The null
		:type		null:		  bool
		:param		default:	  The default
		:type		default:	  Any
		"""
		self.primary_key: bool = primary_key
		self.unique: bool = unique
		self.null: bool = null
		self.default: Any = default

		self.max_length = max_length

	def to_sql_type(self) -> str:
		return f"VARCHAR({self.max_length})"

	def validate(self, value: Any) -> bool:
		"""
		Validate value

		:param		value:	The value
		:type		value:	Any

		:returns:	if the value is verified then True, otherwise False
		:rtype:		bool
		"""
		if value is None and self.null:
			return True

		if not isinstance(value, str):
			return False

		return len(value) <= self.max_length

	def to_db_value(self, value: Any) -> str:
		"""
		Convert value to db

		:param		value:	The value
		:type		value:	Any

		:returns:	db value
		:rtype:		str
		"""
		return str(value) if value is not None else self.default

	def from_db_value(self, value: Any) -> str:
		"""
		Convert value from db

		:param		value:	The value
		:type		value:	Any

		:returns:	db value
		:rtype:		str
		"""
		return str(value) if value is not None else self.default

	def view_table_info(self):
		"""
		View info in table view
		"""
		table = Table(title="SQLSymphonyORM CharField")
		table.add_column("Parameters", style="blue")
		table.add_column("Parameters values", style="green")

		table.add_row("UNIQUE", str(self.unique))
		table.add_row("NULL", str(self.null))
		table.add_row("DEFAULT", str(self.default))
		table.add_row("PRIMARY KEY", str(self.primary_key))
		table.add_row("MAX LENGTH", str(self.max_length))

		console = Console()
		console.print(table)

	def __str__(self):
		return "<CharField>"


class TextField(BaseDataType):
	"""
	This class describes a character field.
	"""

	def __init__(
		self,
		primary_key: bool = False,
		unique: bool = False,
		null: bool = True,
		default: Any = None,
	):
		"""
		Constructs a new instance.

		:param		primary_key:  The primary key
		:type		primary_key:  bool
		:param		unique:		  The unique
		:type		unique:		  bool
		:param		null:		  The null
		:type		null:		  bool
		:param		default:	  The default
		:type		default:	  Any
		"""
		self.primary_key = primary_key
		self.unique: bool = unique
		self.null: bool = null
		self.default: Any = default

	def to_sql_type(self) -> str:
		return "TEXT"

	def validate(self, value: Any) -> bool:
		"""
		Validate value

		:param		value:	The value
		:type		value:	Any

		:returns:	if the value is verified then True, otherwise False
		:rtype:		bool
		"""
		if value is None and self.null:
			return True

		return isinstance(value, str)

	def to_db_value(self, value: Any) -> str:
		"""
		Convert to db value

		:param		value:	The value
		:type		value:	Any

		:returns:	db value
		:rtype:		str
		"""
		return str(value) if value is not None else self.default

	def from_db_value(self, value: Any) -> str:
		"""
		Convert from db value

		:param		value:	The value
		:type		value:	Any

		:returns:	db value
		:rtype:		str
		"""
		return str(value) if value is not None else None

	def view_table_info(self):
		"""
		View info in table view
		"""
		table = Table(title="SQLSymphonyORM TextField")
		table.add_column("Parameters", style="blue")
		table.add_column("Parameters values", style="green")

		table.add_row("UNIQUE", str(self.unique))
		table.add_row("NULL", str(self.null))
		table.add_row("DEFAULT", str(self.default))
		table.add_row("PRIMARY KEY", str(self.primary_key))

		console = Console()
		console.print(table)

	def __str__(self):
		return "<TextField>"


@dataclass
class BlobField(BaseDataType):
	"""
	This class describes a blob field.
	"""

	def __init__(
		self,
		max_size_in_bytes: int = None,
		primary_key: bool = False,
		unique: bool = False,
		null: bool = True,
		default: Any = None,
	):
		"""
		Constructs a new instance.

		:param		primary_key:  The primary key
		:type		primary_key:  bool
		:param		unique:		  The unique
		:type		unique:		  bool
		:param		null:		  The null
		:type		null:		  bool
		:param		default:	  The default
		:type		default:	  Any
		"""
		self.primary_key = primary_key
		self.unique: bool = unique
		self.null: bool = null
		self.default: Any = default

		self.max_size_in_bytes = max_size_in_bytes

	def to_sql_type(self) -> str:
		return "BLOB"

	def validate(self, value: Any) -> bool:
		"""
		Validate value

		:param		value:	The value
		:type		value:	Any

		:returns:	if the value is verified then True, otherwise False
		:rtype:		bool
		"""
		if value is None and self.null:
			return True

		if len(value) > self.max_size_in_bytes:
			return False

		return isinstance(value, bytes)

	def to_db_value(self, value: Any) -> bytes:
		"""
		Convert to db value

		:param		value:	The value
		:type		value:	Any

		:returns:	db value
		:rtype:		bytes
		"""
		return bytes(value) if value is not None else self.default

	def from_db_value(self, value: Any) -> bytes:
		"""
		Convert from db value

		:param		value:	The value
		:type		value:	Any

		:returns:	db value
		:rtype:		bytes
		"""
		return bytes(value) if value is not None else None

	def view_table_info(self):
		"""
		View info in table view
		"""
		table = Table(title="SQLSymphonyORM BlobField")
		table.add_column("Parameters", style="blue")
		table.add_column("Parameters values", style="green")

		table.add_row("UNIQUE", str(self.unique))
		table.add_row("NULL", str(self.null))
		table.add_row("DEFAULT", str(self.default))
		table.add_row("PRIMARY KEY", str(self.primary_key))
		table.add_row("MAX SIZE BYTES", str(self.max_size_in_bytes))

		console = Console()
		console.print(table)

	def __str__(self):
		return "<BlobField>"


class FieldMeta(type):
	"""
	This class describes a field meta.
	"""

	def __new__(cls, name, bases, attrs):
		"""
		New 'magic' func

		:param		cls:	The cls
		:param		name:	The name
		:param		bases:	The bases
		:param		attrs:	The attributes

		:returns:	class
		"""
		fields = {}
		primary_key = None

		for key, value in attrs.items():
			if isinstance(value, BaseDataType):
				fields[key] = value

				if value.primary_key:
					if primary_key:
						raise ValueError("Multiple primary keys are not allowed")

					primary_key = key

					if value.auto_increment:
						value.default = 1

		attrs["_fields"] = fields
		attrs["_primary_key"] = primary_key

		return super().__new__(cls, name, bases, attrs)

	def __str__(self):
		return "<FieldMeta>"
