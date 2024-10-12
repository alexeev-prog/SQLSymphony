import logging
from typing import Union, List
from rich.traceback import install
from rich.console import Console
from rich.table import Table

from loguru import logger

install(show_locals=True)

__version__ = "0.2.8"
__author__ = "alexeev-prog"
__license__ = "GNU GPL v3"
__language__ = "Python 3.12.7"
__pypi_pkg__ = "sqlsymphony_orm"


def introduction():
	"""
	Print introduction table
	"""
	table = Table(
		title="SQLSymphony ORM - powerful and simple ORM for python", expand=True
	)

	table.add_column("Key", style="blue")
	table.add_column("Value", style="green")
	table.add_column("Description", style="magenta")

	table.add_row("Version", __version__, "Stable")
	table.add_row("Author", __author__, "Maintainer&Developer")
	table.add_row("License", __license__, "License of library")
	table.add_row("Language", __language__, "Main language")
	table.add_row("PyPi pep package", __pypi_pkg__, "Package name")

	console = Console()
	console.print(table)


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


introduction()
setup_logger()
