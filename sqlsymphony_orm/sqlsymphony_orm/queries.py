from abc import ABC, abstractmethod
from rich.console import Console
from rich.table import Table
from loguru import logger
from sqlsymphony_orm.performance.cache import cached, SingletonCache, InMemoryCache
from sqlsymphony_orm.database.connection import DBConnector

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
        self.separator: str = exp_type
        self._params: dict = kwargs

    @cached(SingletonCache(InMemoryCache, max_size=1000, ttl=60))
    def __str__(self) -> str:
        """
        Returns a string representation of the object.

        :returns:	String representation of the object.
        :rtype:		str
        """
        kv_pairs: list = [f'{k} = "{v}"' for k, v in self._params.items()]
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

    name: str = None

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

    @cached(SingletonCache(InMemoryCache, max_size=1000, ttl=60))
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

    name: str = "SELECT"

    def __init__(self):
        """
        Constructs a new instance.
        """
        self._params: list = []

    def add(self, *args, **kwargs):
        """
        Add params

        :param		args:	 The arguments
        :type		args:	 list
        :param		kwargs:	 The keywords arguments
        :type		kwargs:	 dictionary
        """
        self._params.extend(args)

    @cached(SingletonCache(InMemoryCache, max_size=1000, ttl=60))
    def line(self) -> str:
        """
        Get line

        :returns:	line
        :rtype:		str
        """
        separator: str = ","
        return separator.join(self._params)

    def __bool__(self) -> bool:
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

    name: str = "FROM"

    def __init__(self):
        """
        Constructs a new instance.
        """
        self._params: list = []

    def add(self, *args, **kwargs):
        """
        Add params

        :param		args:	 The arguments
        :type		args:	 list
        :param		kwargs:	 The keywords arguments
        :type		kwargs:	 dictionary
        """
        self._params.extend(args)

    @cached(SingletonCache(InMemoryCache, max_size=1000, ttl=60))
    def line(self) -> str:
        """
        Get line

        :returns:	line
        :rtype:		str
        """
        separator: str = ","
        return separator.join(self._params)

    def __bool__(self) -> str:
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

    name: str = "WHERE"

    def __init__(self, exp_type: str = AND, **kwargs):
        """
        Constructs a new instance.

        :param		exp_type:  The exponent type
        :type		exp_type:  str
        :param		kwargs:	   The keywords arguments
        :type		kwargs:	   dictionary
        """
        self._q: Q = Q(exp_type, **kwargs)

    def add(self, exp_type: str = AND, **kwargs) -> Q:
        """
        Add params to sql query `where`

        :param		exp_type:  The exponent type
        :type		exp_type:  str
        :param		kwargs:	   The keywords arguments
        :type		kwargs:	   dictionary

        :returns:	Q class instance
        :rtype:		Q
        """
        self._q: Q = Q(exp_type, **kwargs)
        return self._q

    @cached(SingletonCache(InMemoryCache, max_size=1000, ttl=60))
    def line(self) -> str:
        """
        Get line

        :returns:	line
        :rtype:		str
        """
        return str(self._q)

    def __bool__(self) -> bool:
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
        self._data: dict = {"select": Select(), "from": From(), "where": Where()}

    @cached(SingletonCache(InMemoryCache, max_size=1000, ttl=60))
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

    @cached(SingletonCache(InMemoryCache, max_size=1000, ttl=60))
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

    @cached(SingletonCache(InMemoryCache, max_size=1000, ttl=60))
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

    def view_table_info(self):
        """
        Get info in table view
        """
        table = Table(title="QueryBuilder")

        table.add_column("SELECT", style="blue")
        table.add_column("FROM", style="green")
        table.add_column("WHERE", style="cyan")

        for select in self._data["select"]._params:
            for param, where in self._data["where"]._q._params.items():
                for table_name in self._data["from"]._params:
                    table.add_row(select, table_name, f"{param}={where}")

        console = Console()
        console.print(table)

    @cached(SingletonCache(InMemoryCache, max_size=1000, ttl=60))
    def __str__(self) -> str:
        """
        Returns a string representation of the object.

        :returns:	String representation of the object.
        :rtype:		str
        """
        return "".join(self._lines())


def raw_sql_query(connector: "DBConnector" = None, values: tuple = ()):
    """
    RAW SQL Query executor decorator

    :param		connector:	The connector
    :type		connector:	DBConnector
    :param		values:		The values
    :type		values:		tuple

    :returns:	wrappers
    :rtype:		function
    """

    def actual_decorator(func):
        @cached(SingletonCache(InMemoryCache, max_size=1000, ttl=60))
        def wrapper(*args, **kwargs):
            query = func(*args, **kwargs)

            if connector is None:
                print(query)
            else:
                logger.info(f"Execute raw SQL query: {query} ({values})")
                connector.fetch(query, values)

            return query

        return wrapper

    return actual_decorator


class QueryExecutor:
    def __init__(self, db_connector: DBConnector, database_file: str):
        self.connector = db_connector
        self.connector.connect(database_file)

    def execute(self, query: QueryBuilder):
        q = str(query)

        db_results = self.connector.fetch(q)

        return db_results
