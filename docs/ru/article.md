# Создаем свою ORM на python с документацией
ORM, или объектно-реляционное отображение — это программная технология, которая позволяет взаимодействовать с базами данных с использованием объектно-ориентированной парадигмы. Вместо того чтобы писать SQL-запросы напрямую для работы с данными в базе данных, можно использовать ORM, чтобы взаимодействовать с данными, как если бы они были объектами в вашем коде.

ORM позволяет абстрагироваться от сырых SQL запросов путем абстракций.

В этой статье мы и рассмотрим создание своей ORM на Python с документацией и публикацией на PyPI. Данный проект очень интересен со стороны реализации: ведь требуется изучить большую часть ООП, принципов и паттернов.

Мы создадим сессии, модели баз данных, различные поля, миграции и другой вспомогательный функционал. Мы разберем изнутри, как работает такая концепция и как достигается удобство работы.

Некоторые из вас могут подумать что мы изобретаем велосипед. А я в ответ скажу - сможете ли вы прямо сейчас, без подсказок, только по памяти, нарисовать велосипед без ошибок?
	
---

Репозиторий доступен по [ссылке](https://github.com/alexeev-prog/SQLSymphony).

 > Ремарка: sqlite3 выбран из-за простоты, нетрудно заменить обращения к нему на обращения к любой удобной для вас базе данных. По синтаксису я ориентировался на джанго.

Базы данных - очень популярный метод хранения и организации доступа к данным.

Базы данных имеют следующие преимущества перед обычными таблицами или файлами:

 + Базы данных позволяют обрабатывать, хранить и структурировать намного большие объёмы информации, чем таблицы.

 + Удалённый доступ и система запросов позволяет множеству людей одновременно использовать базы данных. С электронными таблицами тоже можно работать онлайн всей командой, но системы управления базами данных делают этот процесс организованнее, быстрее и безопаснее.

 + Объём информации в базах данных может быть огромным и не влиять на скорость работы. А в Google Таблицах уже после нескольких сотен строк или тысяч символов страница будет загружаться очень медленно.

В основном работают с реляционными базами данных (также называют SQL). Записи и связи между ними организованы при помощи таблиц. В таблицах есть поле для внешнего ключа со ссылками на другие таблицы. Благодаря высокой организации и гибкости структуры реляционные БД применяются для многих типов данных.

Базы данных, где информация о реальных вещах представлена в виде объектов под уникальным идентификатором, называется ООБД. К ООБД обращаются на языке объектно-ориентированного программирования (ООП). Состояние объекта описывается атрибутами, а его поведение — набором методов. Объекты с одинаковыми атрибутами и методами образуют классы.
Объект в ООП создаётся как отдельная сущность со своими свойствами и методами работы. И как только объект создан, его можно вызвать по «имени», или коду, а не разрабатывать заново. То есть то что мы и будем создавать сегодня - ORM!

 > Свою библиотеку-orm я назвал SQLSymphony, так что вам иногда придется сменить название, или импорты в соответствии с вашей структурой.

## sqlite
SQLite3 - это простая реляционная база данных, созданная и поддерживаемая всего тремя людьми. Для работы с ней существует стандартная python-библиотека.

Почему SQLite?

SQLite - это компактная и легкая встраиваемая база данных, которая позволяет хранить и управлять данными прямо внутри вашего приложения. Её простота в использовании и широкая поддержка делают её прекрасным выбором для различных проектов, включая веб-приложения, мобильные приложения и многое другое.

Больше о нем можно прочитать [здесь](https://habr.com/ru/articles/754400/).

## Инициализация
ORM будет распространяться в виде python-модуля, поэтому создадим в директории проекта файл `__init__.py`:

```python
import logging
from typing import Union, List
from rich.traceback import install

from loguru import logger

install(show_locals=True)


class InterceptHandler(logging.Handler):
	"""
	This class describes an intercept handler.
	"""

	def emit(self, record) -> None:
		"""
		Get corresponding Loguru level if it exists

		:param		record:	 The record
		:type		record:	 record

		:returns:	None
		:rtype:		None
		"""
		try:
			level = logger.level(record.levelname).name
		except ValueError:
			level = record.levelno

		frame, depth = logging.currentframe(), 2

		while frame.f_code.co_filename == logging.__file__:
			frame = frame.f_back
			depth += 1

		logger.opt(depth=depth, exception=record.exc_info).log(
			level, record.getMessage()
		)


def setup_logger(level: Union[str, int] = "DEBUG", ignored: List[str] = "") -> None:
	"""
	Setup logger

	:param		level:	  The level
	:type		level:	  str
	:param		ignored:  The ignored
	:type		ignored:  List[str]
	"""
	logging.basicConfig(
		handlers=[InterceptHandler()], level=logging.getLevelName(level)
	)

	for ignore in ignored:
		logger.disable(ignore)

	logger.add("sqlsymphony_orm.log")

	logger.info("Logging is successfully configured")


setup_logger()
```

Я буду использовать модуль loguru для логгирования и rich для более красивых и информативных исключений.

Для логгирования при помощи loguru можно использовать следующую конструкцию:

```python
from loguru import logger

logger.info('info')
logger.warning('warning')
logger.error('error')
logger.debug('debug')
```

## Типы данных
В sqlite3 существуют следующие типы данных: INTEGER — вещественное число с указанной точностью, TEXT — текст, BLOB — двоичные данные, REAL — число с плавающей запятой(float24), NUMERIC — то же, что и INTEGER, VarChar - текст с ограниченным количеством символов, BOOLEAN - логическое значение.

У типов данных есть параметры: NOT NULL, DEFAULT, UNIQUE.

![fields](https://github.com/alexeev-prog/SQLSymphony/raw/refs/heads/main/docs/img/fields.png)

Давайте реализуем базовые типы данных, создав модуль fields.py:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


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
	def to_sql_type(self) -> str:
		"""
		Returns a sql type representation of the object.

		:returns:	Sql type representation of the object.
		:rtype:		str

		:raises		NotImplementedError:  abstract method
		"""
		raise NotImplementedError()

	def __str__(self):
		return "<BaseDataType>"
```

Теперь реализуем на основе этого абстрактного класса другие типы данных:

```python
@dataclass
class IntegerField(BaseDataType):
	"""
	This class describes an integer field.
	"""

	def __init__(
		self,
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

		self.min_value = min_value
		self.max_value = max_value

		if self.primary_key:
			if self.default:
				raise ValueError('The parameter "default" is not used for PrimaryKey')

			self.default = 1
			self.value = 1

	def validate(self, value: Any) -> bool:
		"""
		Validate value

		:param		value:	The value
		:type		value:	Any

		:returns:	if the value is verified then True, otherwise False
		:rtype:		bool
		"""
		if self.primary_key and value is None:
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
		if self.primary_key and value is None:
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
		self.primary_key = False
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
		self.primary_key: bool = False
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

	def __str__(self):
		return "<CharField>"


class BooleanField(BaseDataType):
	"""
	This class describes a boolean field.
	"""

	def __init__(
		self,
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
		self.primary_key = False
		self.unique: bool = unique
		self.null: bool = null
		self.default: Any = default

	def to_sql_type(self) -> str:
		return "BOOLEAN"

	def validate(self, value: Any) -> bool:
		"""
		Validate value

		:param		value:	The value
		:type		value:	Any

		:returns:	if the value is verified then True, otherwise False
		:rtype:		bool
		"""
		if isinstance(value, bool):
			return True
		else:
			return False

	def to_db_value(self, value: Any) -> str:
		"""
		Convert to db value

		:param		value:	The value
		:type		value:	Any

		:returns:	db value
		:rtype:		str
		"""
		return str(value).upper() if value is not None else self.default

	def from_db_value(self, value: Any) -> str:
		"""
		Convert from db value

		:param		value:	The value
		:type		value:	Any

		:returns:	db value
		:rtype:		str
		"""
		return str(value).upper() if value is not None else self.default

	def __str__(self):
		return "<BooleanField>"


class TextField(BaseDataType):
	"""
	This class describes a character field.
	"""

	def __init__(
		self,
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
		self.primary_key = False
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
		self.primary_key = False
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
```

У каждого поля есть следующие параметры: unique (должно ли поле быть уникальным), null (может ли быть NULL) и default (значение по умолчанию). Также некоторые поля имеют дополнительные параметры (например CharField, требуется задать максимальную длину в символах).

## Запросы (Query)
В будущем, для фильтрации и получения записей из БД, нам нужны будут запросы. Вместо сырых SQL-запросов мы будем использовать классы для выборки, фильтрации и получения записей.

Класс QueryBuilder как раз и будет отвественнен за это. Строковый вид класса будет возращать созданный SQL запрос:

```python
from abc import ABC, abstractmethod
from rich.console import Console
from rich.table import Table
from loguru import logger

AND = "and"
OR = "or"


class Q:
	"""
	This class describes a Q.
	"""

	def __init__(self, exp_type: str = AND, **kwargs):
		"""
		Constructs a new instance.

		:param		exp_type:  The exponent type
		:type		exp_type:  str
		:param		kwargs:	   The keywords arguments
		:type		kwargs:	   dictionary
		"""
		self.separator = exp_type
		self._params = kwargs

	def __str__(self) -> str:
		"""
		Returns a string representation of the object.

		:returns:	String representation of the object.
		:rtype:		str
		"""
		kv_pairs = [f'{k} = "{v}"' for k, v in self._params.items()]
		return f" {self.separator} ".join(kv_pairs)

	def __bool__(self) -> bool:
		"""
		Returns a boolean representation of the object

		:returns:	Boolean representation of the object.
		:rtype:		bool
		"""
		return bool(self._params)


class BaseExp(ABC):
	"""
	This abstract class describes a base exponent.
	"""

	name = None

	@abstractmethod
	def add(self, *args, **kwargs):
		"""
		Add params

		:param		args:				  The arguments
		:type		args:				  list
		:param		kwargs:				  The keywords arguments
		:type		kwargs:				  dictionary
		"""
		raise NotImplementedError()

	def definition(self) -> str:
		"""
		Get the definition of query

		:returns:	sql query
		:rtype:		str
		"""
		return self.name + " " + self.line() + " "

	@abstractmethod
	def line(self):
		"""
		Get line
		"""
		raise NotImplementedError()

	@abstractmethod
	def __bool__(self):
		"""
		Boolean magic function
		"""
		raise NotImplementedError()


class Select(BaseExp):
	"""
	This class describes a select.
	"""

	name = "SELECT"

	def __init__(self):
		"""
		Constructs a new instance.
		"""
		self._params = []

	def add(self, *args, **kwargs):
		"""
		Add params

		:param		args:	 The arguments
		:type		args:	 list
		:param		kwargs:	 The keywords arguments
		:type		kwargs:	 dictionary
		"""
		self._params.extend(args)

	def line(self) -> str:
		"""
		Get line

		:returns:	line
		:rtype:		str
		"""
		separator = ","
		return separator.join(self._params)

	def __bool__(self):
		"""
		Boolean magic function

		:returns:	if self._params defined
		:rtype:		bool
		"""
		return bool(self._params)


class From(BaseExp):
	"""
	This class describes a from.
	"""

	name = "FROM"

	def __init__(self):
		"""
		Constructs a new instance.
		"""
		self._params = []

	def add(self, *args, **kwargs):
		"""
		Add params

		:param		args:	 The arguments
		:type		args:	 list
		:param		kwargs:	 The keywords arguments
		:type		kwargs:	 dictionary
		"""
		self._params.extend(args)

	def line(self) -> str:
		"""
		Get line

		:returns:	line
		:rtype:		str
		"""
		separator = ","
		return separator.join(self._params)

	def __bool__(self):
		"""
		Boolean magic function

		:returns:	if self._params defined
		:rtype:		bool
		"""
		return bool(self._params)


class Where(BaseExp):
	"""
	This class describes a SQL query `where`.
	"""

	name = "WHERE"

	def __init__(self, exp_type: str = AND, **kwargs):
		"""
		Constructs a new instance.

		:param		exp_type:  The exponent type
		:type		exp_type:  str
		:param		kwargs:	   The keywords arguments
		:type		kwargs:	   dictionary
		"""
		self._q = Q(exp_type, **kwargs)

	def add(self, exp_type: str = AND, **kwargs):
		"""
		Add params to sql query `where`

		:param		exp_type:  The exponent type
		:type		exp_type:  str
		:param		kwargs:	   The keywords arguments
		:type		kwargs:	   dictionary

		:returns:	Q class instance
		:rtype:		Q
		"""
		self._q = Q(exp_type, **kwargs)
		return self._q

	def line(self):
		"""
		Get line

		:returns:	line
		:rtype:		str
		"""
		return str(self._q)

	def __bool__(self):
		"""
		Boolean magic function

		:returns:	if self._q defined
		:rtype:		bool
		"""
		return bool(self._q)


class QueryBuilder:
	"""
	Front-end to create query objects step by step.
	"""

	def __init__(self):
		"""
		Constructs a new instance.
		"""
		self._data = {"select": Select(), "from": From(), "where": Where()}

	def SELECT(self, *args) -> "QueryBuilder":
		"""
		SQL query `select`

		:param		args:  The arguments
		:type		args:  list

		:returns:	Query Builder
		:rtype:		self
		"""
		self._data["select"].add(*args)
		return self

	def FROM(self, *args) -> "QueryBuilder":
		"""
		SQL query `from`

		:param		args:  The arguments
		:type		args:  list

		:returns:	Query Builder
		:rtype:		self
		"""
		self._data["from"].add(*args)
		return self

	def WHERE(self, exp_type: str = AND, **kwargs) -> "QueryBuilder":
		"""
		SQL query `where`

		:param		exp_type:  The exponent type
		:type		exp_type:  str
		:param		kwargs:	   The keywords arguments
		:type		kwargs:	   dictionary

		:returns:	Query Builder
		:rtype:		self
		"""
		self._data["where"].add(exp_type=exp_type, **kwargs)
		return self

	def _lines(self):
		"""
		Lines

		:returns:	Value definition
		:rtype:		yeild (str)
		"""
		for key, value in self._data.items():
			if value:
				yield value.definition()

	def __str__(self) -> str:
		"""
		Returns a string representation of the object.

		:returns:	String representation of the object.
		:rtype:		str
		"""
		return "".join(self._lines())
```

## Кастомные исключение
Для того, чтобы разработчику было более понятней разобраться в ошибках, создадим кастомные исключения:

```python
from loguru import logger


class SQLSymphonyException(Exception):
	"""
	Exception for signaling sql symphony errors.
	"""

	def __init__(self, *args):
		"""
		Constructs a new instance.

		:param		args:  The arguments
		:type		args:  list
		"""
		if args:
			self.message = args[0]
		else:
			self.message = None

	def get_explanation(self) -> str:
		"""
		Gets the explanation.

		:returns:	The explanation.
		:rtype:		str
		"""
		return f"Basic SQLSymphony ORM exception. Message: {self.message if self.message else 'missing'}"

	def __str__(self):
		"""
		Returns a string representation of the object.

		:returns:	String representation of the object.
		:rtype:		str
		"""
		logger.error(f"{self.__class__.__name__}: {self.get_explanation()}")
		return f"SQLSymphonyException has been raised. {self.get_explanation()}"


class FieldNamingError(SQLSymphonyException):
	"""
	This class describes a field naming error.
	"""

	def __init__(self, *args):
		"""
		Constructs a new instance.

		:param		args:  The arguments
		:type		args:  list
		"""
		if args:
			self.message = args[0]
		else:
			self.message = None

	def get_explanation(self) -> str:
		"""
		Gets the explanation.

		:returns:	The explanation.
		:rtype:		str
		"""
		return f"SQLSymphony Field Naming Error. The field name is prohibited/unavailable to avoid naming errors. Message: {self.message if self.message else 'missing'}"

	def __str__(self):
		logger.error(f"{self.__class__.__name__}: {self.get_explanation()}")
		return f"Field Naming Error has been raised. {self.get_explanation()}"


class NullableFieldError(SQLSymphonyException):
	"""
	This class describes a nullable field error.
	"""

	def __init__(self, *args):
		"""
		Constructs a new instance.

		:param		args:  The arguments
		:type		args:  list
		"""
		if args:
			self.message = args[0]
		else:
			self.message = None

	def get_explanation(self) -> str:
		"""
		Gets the explanation.

		:returns:	The explanation.
		:rtype:		str
		"""
		return f"SQLSymphony Nullable Field Error. Field is set to NOT NULL, but it is empty. Message: {self.message if self.message else 'missing'}"

	def __str__(self):
		logger.error(f"{self.__class__.__name__}: {self.get_explanation()}")
		return f"Nullable Field Error has been raised. {self.get_explanation()}"


class FieldValidationError(SQLSymphonyException):
	"""
	This class describes a field validation error.
	"""

	def __init__(self, *args):
		"""
		Constructs a new instance.

		:param		args:  The arguments
		:type		args:  list
		"""
		if args:
			self.message = args[0]
		else:
			self.message = None

	def get_explanation(self) -> str:
		"""
		Gets the explanation.

		:returns:	The explanation.
		:rtype:		str
		"""
		return f"SQLSymphony Field Validation Error. Message: {self.message if self.message else 'missing'}"

	def __str__(self):
		logger.error(f"{self.__class__.__name__}: {self.get_explanation()}")
		return f"Field Validation Error has been raised. {self.get_explanation()}"


class PrimaryKeyError(SQLSymphonyException):
	"""
	This class describes a primary key error.
	"""

	def __init__(self, *args):
		"""
		Constructs a new instance.

		:param		args:  The arguments
		:type		args:  list
		"""
		if args:
			self.message = args[0]
		else:
			self.message = None

	def get_explanation(self) -> str:
		"""
		Gets the explanation.

		:returns:	The explanation.
		:rtype:		str
		"""
		return f"SQLSymphony Primary Key Error. According to database theory, each table should have only one PrimaryKey field, Message: {self.message if self.message else 'missing'}"

	def __str__(self):
		logger.error(f"{self.__class__.__name__}: {self.get_explanation()}")
		return f"Primary Key Error has been raised. {self.get_explanation()}"


class UniqueConstraintError(SQLSymphonyException):
	"""
	This class describes an unique constraint error.
	"""

	def __init__(self, *args):
		"""
		Constructs a new instance.

		:param		args:  The arguments
		:type		args:  list
		"""
		if args:
			self.message = args[0]
		else:
			self.message = None

	def get_explanation(self) -> str:
		"""
		Gets the explanation.

		:returns:	The explanation.
		:rtype:		str
		"""
		return f"SQLSymphony Unique Constraint Error. An exception occurred when executing an SQL query due to problems with UNIQUE fields. Message: {self.message if self.message else 'missing'}"

	def __str__(self):
		logger.error(f"{self.__class__.__name__}: {self.get_explanation()}")
		return f"Unique Constraint Error has been raised. {self.get_explanation()}"


class ModelHookError(SQLSymphonyException):
	"""
	This class describes a model hook error.
	"""

	def __init__(self, *args):
		"""
		Constructs a new instance.

		:param		args:  The arguments
		:type		args:  list
		"""
		if args:
			self.message = args[0]
		else:
			self.message = None

	def get_explanation(self) -> str:
		"""
		Gets the explanation.

		:returns:	The explanation.
		:rtype:		str
		"""
		return f"Model Hooks Error. An exception occurred when executing an hook due to problems with ORM. Message: {self.message if self.message else 'missing'}"

	def __str__(self):
		logger.error(f"{self.__class__.__name__}: {self.get_explanation()}")
		return f"Model Hook error has been raised. {self.get_explanation()}"


class MigrationError(SQLSymphonyException):
	"""
	This class describes a migration error.
	"""

	def __init__(self, *args):
		"""
		Constructs a new instance.

		:param		args:  The arguments
		:type		args:  list
		"""
		if args:
			self.message = args[0]
		else:
			self.message = None

	def get_explanation(self) -> str:
		"""
		Gets the explanation.

		:returns:	The explanation.
		:rtype:		str
		"""
		return f"Database Migration Error. An exception occurred when executing an hook due to problems with migration. Message: {self.message if self.message else 'missing'}"

	def __str__(self):
		logger.error(f"{self.__class__.__name__}: {self.get_explanation()}")
		return f"Migration Error has been raised. {self.get_explanation()}"
```

Мы создаем базовый класс, наследуемый от Exception и метод строкового обращения. А потом уже создаем более подробные исключения на основе базового класса.

## Пользовательские модели
По традициям, разработчик в нашей ORM должен создавать модели примерно следующим образом:

```python
class User(SessionModel):
	__tablename__ = "Users"

	id = IntegerField(primary_key=True)
	name = TextField(null=False)
	cash = RealField(null=False, default=0.0)

	def __repr__(self):
		return f"<User {self.pk}>"


class User2(SessionModel):
	__tablename__ = "Users"

	id = IntegerField(primary_key=True)
	name = TextField(null=False)
	cash = RealField(null=False, default=0.0)
	password = TextField(default="password1234")

	def __repr__(self):
		return f"<User {self.pk}>"


class Comment(SessionModel):
	id = IntegerField(primary_key=True)
	name = TextField(null=False)
	user_id = IntegerField(null=False)

	def __repr__(self):
		return f"<Comment {self.pk}>"
```

Для этого нам нужно будет реализовать классы моделей (мета-класс и саму модель). 

```python
from pathlib import Path
from typing import List, Any, Union, Callable
from uuid import uuid4
from abc import ABC, abstractmethod
from collections import OrderedDict

from loguru import logger

from sqlsymphony_orm.datatypes.fields import BaseDataType, IntegerField # модуль типов данных
from sqlsymphony_orm.exceptions import (
	PrimaryKeyError,
	FieldValidationError,
	NullableFieldError,
	FieldNamingError,
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
```

В метаклассе мы читаем модель, добавляем поля, задаем базовые настройки. В классе модели мы все проверяем и задаем Primary Key.

Также есть classmethod-функция и обычная функция для получения форматированных полей для SQL.

У нас есть свойство для получения Primary Key, а также функция для добавления хуков. Хуки в контексте нашей ORM - это функции, выполняемые до определенной операции модели и базы данных.

## Подключение к БД
Давайте теперь возьмемся за основу работы с базой данных - класс подключения и класс менеджера.

Напишем код для подключения к бд:

```python
import sqlite3
from abc import ABC, abstractmethod
from typing import Tuple

from rich import print

from loguru import logger


class DBConnector(ABC):
	"""
	This class describes a db connector.
	"""

	def __new__(cls, *args, **kwargs):
		"""
		New class

		:param		cls:	 The cls
		:type		cls:	 list
		:param		args:	 The arguments
		:type		args:	 list
		:param		kwargs:	 The keywords arguments
		:type		kwargs:	 dictionary

		:returns:	cls instance
		:rtype:		self
		"""
		if not hasattr(cls, "instance"):
			cls.instance = super(DBConnector, cls).__new__(cls, *args, **kwargs)

		return cls.instance

	@abstractmethod
	def connect(self, database_name: str):
		"""
		Connect to database

		:param		database_name:		  The database name
		:type		database_name:		  str

		:raises		NotImplementedError:  Abstract method
		"""
		raise NotImplementedError()

	@abstractmethod
	def commit(self):
		"""
		Commit changes to database

		:raises		NotImplementedError:  Abstract method
		"""
		raise NotImplementedError()

	@abstractmethod
	def fetch(self, query: str):
		"""
		Fetches the given query.

		:param		query:				  The query
		:type		query:				  str

		:raises		NotImplementedError:  Abstract method
		"""
		raise NotImplementedError()


class SQLiteDBConnector(DBConnector):
	"""
	This class describes a sqlite db connector.
	"""

	def __new__(cls, *args, **kwargs):
		"""
		New class

		:param		cls:	 The cls
		:type		cls:	 list
		:param		args:	 The arguments
		:type		args:	 list
		:param		kwargs:	 The keywords arguments
		:type		kwargs:	 dictionary

		:returns:	cls instance
		:rtype:		self
		"""
		if not hasattr(cls, "instance"):
			cls.instance = super(SQLiteDBConnector, cls).__new__(cls, *args, **kwargs)

		return cls.instance

	def close_connection(self):
		"""
		Closes a connection.
		"""
		self._connection.close()
		print("[bold]Connection has been closed[/bold]")
		logger.info("Close Database Connection")

	def connect(self, database_name: str = "database.db"):
		"""
		Connect to database

		:param		database_name:	The database name
		:type		database_name:	str
		"""
		pragmas = ["PRAGMA foreign_keys = 1"]
		self._connection = sqlite3.connect(database_name)
		self.database_name = database_name
		logger.info(f"[{database_name}] Connect database...")

		for pragma in pragmas:
			self._connection.execute(pragma)
			logger.debug(f"Set pragma: {pragma}")

	def commit(self):
		"""
		Commit changes to database
		"""
		logger.info("Commit changes to database")
		self._connection.commit()

	def fetch(self, query: str, values: Tuple = (), get_cursor: bool = False) -> list:
		"""
		Fetch SQL query

		:param		query:	 The query
		:type		query:	 str
		:param		values:	 The values
		:type		values:	 Tuple

		:returns:	list with fetched results
		:rtype:		list
		"""
		cursor = self._connection.cursor()
		self.commit()

		logger.debug(f"Fetch query: {query} {values}")

		try:
			cursor.execute(query, values)
		except Exception as ex:
			logger.error(f"An exception occurred while executing the request: {ex}")
			raise ex

		return [cursor, cursor.fetchall()] if get_cursor else cursor.fetchall()
```

Все просто - создаем абстрактный класс и класс SQLiteDBConnector, наследуемый от него. Если вам потребуется добавить поддержку других СУБД, такая структура сделает это более удобней.

Мы имеем метод `__new__` для создания новых инстансов, метод подключения, отключения, коммита и выполнения запроса.

Перейдем теперь к более сложному - к менеджеру:

```python
from abc import ABC, abstractmethod
from typing import Any
from loguru import logger

from sqlsymphony_orm.queries import QueryBuilder
from sqlsymphony_orm.database.connection import DBConnector, SQLiteDBConnector


class MultiManager(ABC):
	"""
	This class describes a multi manager.
	"""

	@abstractmethod
	def reconnect(self):
		"""
		reconnect to db

		:raises		NotImplementedError:  abstract method
		"""
		raise NotImplementedError()

	@abstractmethod
	def drop_table(self, table_name: str):
		"""
		Drop sql table

		:param		table_name:			  The table name
		:type		table_name:			  str

		:raises		NotImplementedError:  abstract method
		"""
		raise NotImplementedError()

	@abstractmethod
	def close_connection(self):
		"""
		Closes a connection.

		:raises		NotImplementedError:  abstract method
		"""
		raise NotImplementedError()

	@abstractmethod
	def insert(
		self,
		table_name: str,
		formatted_fields: dict,
		pk: int,
		model_class: "Model",
		ignore: bool = False,
	):
		"""
		insert new model to database

		:param		table_name:			  The table name
		:type		table_name:			  str
		:param		formatted_fields:	  The formatted fields
		:type		formatted_fields:	  dict
		:param		pk:					  primary key value
		:type		pk:					  int
		:param		model_class:		  The model class
		:type		model_class:		  Model
		:param		ignore:				  The ignore
		:type		ignore:				  bool

		:raises		NotImplementedError:  { exception_description }
		"""
		raise NotImplementedError()

	@abstractmethod
	def update(self, table_name: str, key: str, orig_field: str, new_value: str):
		"""
		update model

		:param		table_name:			  The table name
		:type		table_name:			  str
		:param		key:				  The key
		:type		key:				  str
		:param		orig_field:			  The original field
		:type		orig_field:			  str
		:param		new_value:			  The new value
		:type		new_value:			  str

		:raises		NotImplementedError:  abstract method
		"""
		raise NotImplementedError()

	@abstractmethod
	def filter(self, query: QueryBuilder):
		"""
		filter and get model by query

		:param		query:				  The query
		:type		query:				  QueryBuilder

		:raises		NotImplementedError:  abstract method
		"""
		raise NotImplementedError()

	@abstractmethod
	def commit(self):
		"""
		Commit changes

		:raises		NotImplementedError:  abstract method
		"""
		raise NotImplementedError()

	@abstractmethod
	def create_table(self, table_name: str, fields: dict):
		"""
		Creates a table.

		:param		table_name:			  The table name
		:type		table_name:			  str
		:param		fields:				  The fields
		:type		fields:				  dict

		:raises		NotImplementedError:  abstract method
		"""
		raise NotImplementedError()

	@abstractmethod
	def delete(self, table_name: str, field_name: str, field_value: Any):
		"""
		delete model

		:param		table_name:			  The table name
		:type		table_name:			  str
		:param		field_name:			  The field name
		:type		field_name:			  str
		:param		field_value:		  The field value
		:type		field_value:		  Any

		:raises		NotImplementedError:  abstract method
		"""
		raise NotImplementedError()


class SQLiteMultiManager(MultiManager):
	"""
	This class describes a sqlite multi manager.
	"""

	def __init__(self, database_name: str):
		"""
		Constructs a new instance.

		:param		database_name:	The database name
		:type		database_name:	str
		"""
		self._connector = SQLiteDBConnector()
		self.database_name = database_name
		self._connector.connect(self.database_name)

	def execute(self, raw_sql_query: str, values: tuple = (), get_cursor: bool = False):
		return self._connector.fetch(raw_sql_query, values, get_cursor)

	def reconnect(self, database_file: str = None):
		"""
		reconnect to database
		"""
		if database_file is not None:
			self.database_name = database_file
		self._connector.connect(self.database_name)

	def drop_table(self, table_name: str):
		"""
		drop table

		:param		table_name:	 The table name
		:type		table_name:	 str
		"""
		query = f"DROP TABLE IF EXISTS {table_name}"

		logger.warning(f"Drop table: {table_name}")

		self._connector.fetch(query)
		self._connector.commit()

	def close_connection(self):
		"""
		Closes a connection.
		"""
		self._connector.close_connection()

	def insert(
		self,
		table_name: str,
		formatted_fields: dict,
		pk: int,
		model_class: "Model",
		ignore: bool = False,
	):
		"""
		Insert a fields to database

		:param		table_name:	 The table name
		:type		table_name:	 str
		:param		columns:	 The columns
		:type		columns:	 str
		:param		count:		 The count
		:type		count:		 str
		:param		values:		 The values
		:type		values:		 tuple
		"""
		fields = []
		values = []

		for k, v in formatted_fields.items():
			fields.append(k)
			if "PRIMARY KEY" in v:
				values.append(pk)
			else:
				values.append(getattr(model_class, k))

		columns = ", ".join(fields)
		count = ", ".join(["?" for _ in values])

		query = "INSERT "

		if ignore:
			query += "OR IGNORE "

		query += f"INTO {table_name} ({columns}) VALUES ({count})"

		logger.info(
			f'[{table_name}] Insert {"(or ignore)" if ignore else ""} new model into database'
		)

		self._connector.fetch(query, values)

	def update(self, table_name: str, key: str, orig_field: str, new_value: str):
		"""
		Update fields in database table

		:param		table_name:	 The table name
		:type		table_name:	 str
		:param		key:		 The key
		:type		key:		 str
		:param		orig_field:	 The original field
		:type		orig_field:	 str
		:param		new_value:	 The new value
		:type		new_value:	 str
		"""
		query = f"UPDATE {table_name} SET {key} = ? WHERE {key} = ?"

		logger.info(f"[{table_name}] Update model: {key}={new_value}")

		self._connector.fetch(query, (new_value, orig_field))

	def filter(self, query: str) -> list:
		"""
		filter and get model by query

		:param		query:	The query
		:type		query:	str

		:returns:	models
		:rtype:		list
		"""
		result = self._connector.fetch(query)

		return result

	def commit(self):
		"""
		Commits changes.
		"""
		self._connector.commit()

	def create_table(self, table_name: str, fields: dict):
		"""
		Creates a table.

		:param		table_name:	 The table name
		:type		table_name:	 str
		:param		fields:		 The fields
		:type		fields:		 dict
		"""
		columns = [f"{k} {v}" for k, v in fields.items()]

		query = f"CREATE TABLE IF NOT EXISTS {table_name} ("

		for column in columns:
			query += f"{column},"

		query = query[:-1]
		query += ")"

		logger.info(f"Create new table: {table_name}")

		self._connector.fetch(query)
		self._connector.commit()

	def delete(self, table_name: str, field_name: str, field_value: Any):
		"""
		Delete model from database

		:param		table_name:	  The table name
		:type		table_name:	  str
		:param		field_name:	  The field name
		:type		field_name:	  str
		:param		field_value:  The field value
		:type		field_value:  Any
		"""
		query = f"DELETE FROM {table_name} WHERE {field_name} = ?"
		logger.info(f"[{table_name}] Delete model ({field_name}={field_value})")

		self._connector.fetch(query, (field_value,))
```

Это также относительно просто: при инициализации создаем инстанс класса подключения, подключаемся к БД, и создаем базовые методы: удаление, создание таблицы, коммит, фильтр, обновление, добавления, и прочие вспомогательные методы для работы с подключением и таблицами.

## Сессии
Но как мы будем добавлять модели в базу данных и работать с ними? Все просто - я решил что правильным способом будем создание класса сессии.

Давайте реализуем это:

```python
from pathlib import Path
from typing import List, Any, Union, Callable
from uuid import uuid4
from abc import ABC, abstractmethod
from collections import OrderedDict

from loguru import logger

from sqlsymphony_orm.database.manager import SQLiteMultiManager # менеджер
from sqlsymphony_orm.datatypes.fields import BaseDataType, IntegerField # типы данныъ
from sqlsymphony_orm.exceptions import ( # исключения
	PrimaryKeyError,
	FieldValidationError,
	NullableFieldError,
	FieldNamingError,
)lsymphony_orm.queries import QueryBuilder # билдер запросов


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
	def get_all_by_module(self, needed_model: SessionModel):
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

	def get_all_by_module(self, needed_model: SessionModel) -> List[SessionModel]:
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
```

Такая же структура, как и в остальном коде - создаем абстрактный класс сессии и позже создаем класс-наследник нужной СУБД - в данном случае sqlite.

Класс сессии имеет методы для добавления модели, фильтра, получения всех моделей, получения моделей одного типа, удаление моделей, обновления и другие вспомогательные методы.

Через сессию можно работать так:

```python
from sqlsymphony_orm.datatypes.fields import IntegerField, RealField, TextField
from sqlsymphony_orm.models.session_models import SessionModel
from sqlsymphony_orm.models.session_models import SQLiteSession
from sqlsymphony_orm.queries import QueryBuilder

session = SQLiteSession("example.db")


class User(SessionModel):
	__tablename__ = "Users"

	id = IntegerField(primary_key=True)
	name = TextField(null=False)
	cash = RealField(null=False, default=0.0)

	def __repr__(self):
		return f"<User {self.pk}>"


class User2(SessionModel):
	__tablename__ = "Users"

	id = IntegerField(primary_key=True)
	name = TextField(null=False)
	cash = RealField(null=False, default=0.0)
	password = TextField(default="password1234")

	def __repr__(self):
		return f"<User {self.pk}>"


class Comment(SessionModel):
	id = IntegerField(primary_key=True)
	name = TextField(null=False)
	user_id = IntegerField(null=False)


user = User(name="John")
user2 = User(name="Bob")
user3 = User(name="Ellie")
session.add(user)
session.commit()
session.add(user2)
session.commit()
session.add(user3)
session.commit()
session.delete(user3)
session.commit()
session.update(model=user2, name="Anna")
session.commit()

comment = Comment(name=user.name, user_id=user.pk)
session.add(comment)
session.commit()

print(
	session.filter(QueryBuilder().SELECT("*").FROM(User.table_name).WHERE(name="Anna"))
)
print(session.get_all())
print(session.get_all_by_module(User))
print(user.pk)

session.close()
```

## Вспомогательные модули
Давайте реализуем небольшой модуль хеширования. Это может потребоваться, когда в БД хранятся данные, которые должны быть засекречены.

```python
import hashlib
from abc import ABC, abstractmethod
from enum import Enum, auto
from hmac import compare_digest
from typing import Union


class HashAlgorithm(Enum):
	"""
	This class describes a hash algorithms.
	"""

	SHA256 = auto()
	SHA512 = auto()
	MD5 = auto()
	BLAKE2B = auto()
	BLAKE2S = auto()


class HashingBase(ABC):
	"""
	This class describes a hashing base.
	"""

	@abstractmethod
	def hash(
		self, data: Union[bytes, str], hexdigest: bool = False
	) -> Union[bytes, str]:
		"""
		Hash

		:param		data:				  The data
		:type		data:				  Union[bytes, str]
		:param		hexdigest:			  The hexdigest
		:type		hexdigest:			  bool

		:returns:	hashing
		:rtype:		Union[bytes, str]

		:raises		NotImplementedError:  abstract method
		"""
		raise NotImplementedError()

	@abstractmethod
	def verify(self, data: Union[bytes, str], hashed_data: Union[bytes, str]) -> bool:
		"""
		Verify data and hashed data

		:param		data:				  The data
		:type		data:				  Union[bytes, str]
		:param		hashed_data:		  The hashed data
		:type		hashed_data:		  Union[bytes, str]

		:returns:	true if data=hashed_data
		:rtype:		bool

		:raises		NotImplementedError:  { exception_description }
		"""
		raise NotImplementedError()


class PlainHasher(HashingBase):
	"""
	This class describes a plain hasher.
	"""

	def __init__(self, algorithm: HashAlgorithm = HashAlgorithm.SHA256):
		"""
		Constructs a new instance.

		:param		algorithm:	The algorithm
		:type		algorithm:	HashAlgorithm
		"""
		self.algorithm = algorithm

	def hash(self, data: Union[bytes, str]) -> bytes:
		"""
		Generate hash

		:param		data:  The data
		:type		data:  Union[bytes, str]

		:returns:	hash
		:rtype:		bytes
		"""
		if isinstance(data, str):
			data = data.encode("utf-8")

		hasher = self.get_hasher()
		return hasher(data).digest()

	def verify(self, data: Union[bytes, str], hashed_data: Union[bytes, str]) -> bool:
		"""
		Verify data and hashed data

		:param		data:		  The data
		:type		data:		  Union[bytes, str]
		:param		hashed_data:  The hashed data
		:type		hashed_data:  Union[bytes, str]

		:returns:	true if data==hashed_data
		:rtype:		bool
		"""
		if isinstance(data, str):
			data = data.encode("utf-8")
		if isinstance(hashed_data, str):
			hashed_data = hashed_data.encode()

		expected_hash = self.hash(data)

		return compare_digest(expected_hash, hashed_data)

	def get_hasher(self) -> callable:
		"""
		Gets the hasher function.

		:returns:	The hasher.
		:rtype:		callable

		:raises		ValueError:	 unknown hash function.
		"""
		hash_functions = {
			HashAlgorithm.SHA256: hashlib.sha256,
			HashAlgorithm.SHA512: hashlib.sha512,
			HashAlgorithm.MD5: hashlib.md5,
			HashAlgorithm.BLAKE2B: hashlib.blake2b,
			HashAlgorithm.BLAKE2S: hashlib.blake2s,
		}

		hash_function = hash_functions.get(self.algorithm, None)

		if hash_function is None:
			raise ValueError(f"Unknown hash function type: {self.algorithm}")
		else:
			return hash_function


class SaltedHasher(HashingBase):
	"""
	This class describes a salted hasher.
	"""

	def __init__(
		self, algorithm: HashAlgorithm = HashAlgorithm.SHA256, salt: str = "SOMESALT"
	):
		"""
		Constructs a new instance.

		:param		algorithm:	The algorithm
		:type		algorithm:	HashAlgorithm
		:param		salt:		The salt
		:type		salt:		str
		"""
		self.algorithm = algorithm
		self.salt = salt

	def hash(self, data: Union[bytes, str]) -> bytes:
		"""
		Generate hash

		:param		data:  The data
		:type		data:  Union[bytes, str]

		:returns:	hash
		:rtype:		bytes
		"""
		salt = self.salt.encode("utf-8")

		if isinstance(data, str):
			data = data.encode("utf-8")

		hasher = self.get_hasher()
		value = f"{data}{salt}".encode("utf-8")

		return hasher(value).digest()

	def verify(self, data: str, hashed_data: Union[bytes, str]) -> bool:
		"""
		Verify data and hashed_data

		:param		data:		  The data
		:type		data:		  str
		:param		hashed_data:  The hashed data
		:type		hashed_data:  Union[bytes, str]

		:returns:	true if data==hashed_data
		:rtype:		bool
		"""
		if isinstance(hashed_data, str):
			print("convert")

		expected_hash = self.hash(data)

		return compare_digest(expected_hash, hashed_data)

	def get_hasher(self) -> callable:
		"""
		Gets the hasher function.

		:returns:	The hasher.
		:rtype:		callable

		:raises		ValueError:	 unknown hasher function
		"""
		hash_functions = {
			HashAlgorithm.SHA256: hashlib.sha256,
			HashAlgorithm.SHA512: hashlib.sha512,
			HashAlgorithm.MD5: hashlib.md5,
			HashAlgorithm.BLAKE2B: hashlib.blake2b,
			HashAlgorithm.BLAKE2S: hashlib.blake2s,
		}

		hash_function = hash_functions.get(self.algorithm, None)

		if hash_function is None:
			raise ValueError(f"Unknown hash function type: {self.algorithm}")
		else:
			return hash_function
```

Здесь есть также абстрактный класс хешера и два его наследника - обычный (plain) хешер и засоленный (salted) hasher. Salted hasher генерирует хеш с солью, то есть к значению для хеширования мы добавляем соль. Это позволит избежать нахождения хеш-коллизий.

## Миграции
Миграции в контексте нашей ORM - это действия для обновления старой модели на новую с апдейтом базы данных. То есть: если старая модель имела два поля: id и name, то мы можем создать новую модель с тремя полями (id, name и age), и во время миграции в базу данных добавится новое поле, без потери старых изменений. Но есть несколько ограничений:

 + Возможны проблемы с UNIQUE-полями.
 + Если поле с параметром NOT NULL, она должна иметь параметр DEFAULT, иначе будет ошибка.

Конечно, у нас миграции простые, но вы можете сделать лучше.

Также я сделал возможность бекапить БД, которые были до миграции. Во время инициализации менеджера миграций, создается директория migrations, туда помещается бекап текущей базы данных, и после этого уже идет работа менеджера. А сами миграции для восстановления хранятся в json-файле. Благодаря этому, если миграция прошла неудачно, можно ее отменить и все вернуть на место. Главное - чтобы существовал бекап.

Напишем код:

```python
from typing import Optional, Union
from abc import ABC, abstractmethod
import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from sqlsymphony_orm.models.session_models import SQLiteSession # сессия
from sqlsymphony_orm.exceptions import MigrationError # исключение
from loguru import logger


class MigrationManager(ABC):
	"""
	This class describes a migration manager.
	"""

	@abstractmethod
	def get_current_table_columns(self, table_name: str):
		"""
		Gets the current table columns.

		:param		table_name:			  The table name
		:type		table_name:			  str

		:raises		NotImplementedError:  abstract method
		"""
		raise NotImplementedError()

	@abstractmethod
	def get_table_columns_from_model(self, model: "Model"):
		"""
		Gets the table columns from model.

		:param		model:				  The model
		:type		model:				  Model

		:raises		NotImplementedError:  abstract method
		"""
		raise NotImplementedError()

	@abstractmethod
	def revert_migration(self, index_key: int = -1):
		"""
		Revert migration

		:param		index_key:			  The index key
		:type		index_key:			  int

		:raises		NotImplementedError:  abstract method
		"""
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

	def upload_migrations_file(self):
		logger.debug(f"Load JSON migrations history file: {self.migrations_file}")
		with open(self.migrations_file, "r") as read_file:
			self.migrations = json.load(read_file)

	def update_migrations_file(self):
		logger.debug(f"Update JSON migrations history file: {self.migrations_file}")
		with open(self.migrations_file, "w") as write_file:
			json.dump(self.migrations, write_file, indent=4)

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
				f"[Migration] Change table name: {original_table_name} -> {new_table_name}"
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
				f'[Migration] Drop column {field_name.split(" ")[0]} from table {original_table_name}'
			)
			sql_queries.append(
				f"ALTER TABLE {original_table_name} DROP COLUMN {field_name.split(" ")[0]};"
			)

		for field in added:
			if "NOT NULL" in field and "DEFAULT" not in field:
				raise MigrationError(
					f'Cannot script a "not null" field without default value in field "{field}"'
				)
			logger.debug(f"[Migration] Add column {field} to {original_table_name}")
			sql_queries.append(f"ALTER TABLE {original_table_name} ADD COLUMN {field};")

		migrationfile = os.path.join(
			self.migrations_dir,
			f'{datetime.now().strftime("backup_%Y%m%d%H%M%S")}_{self.session.database_file}',
		)
		logger.debug(f"Create migraton file: {migrationfile}")
		shutil.copyfile(self.session.database_file, migrationfile)

		if Path(self.migrations_file).exists():
			self.upload_migrations_file()

		self.migrations[str(len(self.migrations) + 1)] = {
			"migrationfile": migrationfile,
			"tablename": original_table_name,
			"description": f"from {old_model._model_name} to {new_model._model_name}",
			"sql_queries": list(sql_queries),
			"fields": {
				"new": list(new_fields),
				"old": list(old_fields),
				"added": list(added),
				"dropped": list(dropped),
			},
		}

		self.update_migrations_file()

		for sql_query in sql_queries:
			logger.debug(f"[Migration] Execute sql query: {sql_query}")

			try:
				self.session.execute(sql_query)
			except Exception as ex:
				raise MigrationError(str(ex))

	def revert_migration(self, index_key: int = -1):
		"""
		Revert migration

		:param		index_key:	The index key
		:type		index_key:	int
		"""
		self.upload_migrations_file()

		if index_key == -1:
			index_key = [k for k in self.migrations.keys()][-1]

		try:
			migration = self.migrations[str(index_key)]
		except KeyError as ke:
			logger.error(f"Cannot get migration by index {index_key}: {ke}")

		logger.info("[Migration] Rollback database from new to old.")
		shutil.copyfile(migration["migrationfile"], self.session.database_file)
```

Весь основной код содержится в методе migrate_from_model, которая принимает на вход старую модель, новую модель, название таблицы и новое название таблицы (опционально). Мы получаем нужные поля, работая с ними через множества set, и создаем нужные бекапы.

Метод revert_migration же позволяет по индексу миграции вернуть старую версию БД. Индекс по умолчанию -1, то есть последний. После мы получаем нужную миграцию и замещаем новую БД старой БД.

## Пример работы
Вот полный код примера работы ORM:

```python
from sqlsymphony_orm.datatypes.fields import IntegerField, RealField, TextField # поля
from sqlsymphony_orm.models.session_models import SessionModel # модель
from sqlsymphony_orm.models.session_models import SQLiteSession # сессия
from sqlsymphony_orm.queries import QueryBuilder # билдер запросов
from sqlsymphony_orm.migrations.migrations_manager import SQLiteMigrationManager # миграции

start = time()
session = SQLiteSession("example.db")


class User(SessionModel):
	__tablename__ = "Users"

	id = IntegerField(primary_key=True)
	name = TextField(null=False)
	cash = RealField(null=False, default=0.0)

	def __repr__(self):
		return f"<User {self.pk}>"


class User2(SessionModel):
	__tablename__ = "Users"

	id = IntegerField(primary_key=True)
	name = TextField(null=False)
	cash = RealField(null=False, default=0.0)
	password = TextField(default="password1234")

	def __repr__(self):
		return f"<User {self.pk}>"


class Comment(SessionModel):
	id = IntegerField(primary_key=True)
	name = TextField(null=False)
	user_id = IntegerField(null=False)


user = User(name="John")
user2 = User(name="Bob")
user3 = User(name="Ellie")
session.add(user)
session.commit()
session.add(user2)
session.commit()
session.add(user3)
session.commit()
session.delete(user3)
session.commit()
session.update(model=user2, name="Anna")
session.commit()

comment = Comment(name=user.name, user_id=user.pk)
session.add(comment)
session.commit()

print(
	session.filter(QueryBuilder().SELECT("*").FROM(User.table_name).WHERE(name="Anna"))
)
print(session.get_all())
print(session.get_all_by_module(User))
print(user.pk)

migrations_manager = SQLiteMigrationManager(session)
migrations_manager.migrate_from_model(User, User2, "Users", "UserAnd")
migrations_manager.revert_migration(-1)

session.close()
```

У нас есть три модели - модель юзера, новая модель юзера, модель комментария. Мы всех их добавляем, обновляем если надо. Потом в коде демонстрируется фильтрация и получение моделей, а в конце мы создаем миграцию и после сразу же возвращаем старую БД, и в конце закрываем сессию.

Для сохранения изменений после операции следует вызвать session.commit().

Итак, это все!

Мы смогли изучить многие сложные конструкции ООП в python на примере создания такой базовой вещи как ORM.

Да, наша ORM не идеальна, нет ForeignKey, некоторых других вещей. Значение PrimaryKey доступно только после добавления модели. Если у вас есть замечания по поводу статьи - пишите в комментариях. Разумная критика приветствуется!

Ссылка на github-репозиторий с примерами [здесь](https://github.com/alexeev-prog/SQLSymphony).

Документация моей ORM [доступна по этой ссылке](https://alexeev-prog.github.io/SQLSymphony/).

А PyPI проект находится [по этой ссылке](https://pypi.org/project/sqlsymphony-orm/).

# Заключение
Спасибо за внимание! Это был довольно интересный опыт для меня, т.к. это мой первый большой проект на python с продвинутым ООП, где я попытался изучить более подробно язык и инструментарии.

Если у вас есть замечания по статье или по коду - пишите, наверняка есть более опытный и профессиональный программист на Python, который может помочь как и читателям статьи, так и мне.

Ссылка на мой репозиторий реализации ORM [здесь](https://github.com/alexeev-prog/SQLSymphony).

Буду рад, если вы присоединитесь к моему небольшому [телеграм-блогу](https://t.me/hex_warehouse). Анонсы статей, новости из мира IT и полезные материалы для изучения программирования и смежных областей. Если конечно хотите :)

## Источники

 + [collerek/ormar](https://github.com/collerek/ormar)
 + [ardilla/chrisdewa](https://github.com/chrisdewa/ardilla)
 + [Простой ORM для sqlite3](https://habr.com/ru/companies/ruvds/articles/766552/)
 + [Главное о базах данных](https://practicum.yandex.ru/blog/chto-takoe-bazy-dannyh/)
