from rich.traceback import install
from rich.console import Console
from rich.table import Table

install(show_locals=True)

__version__ = "0.1.2"
__author__ = 'alexeev-prog'
__license__ = 'GNU GPL v3'
__language__ = 'Python 3.12.7'
__pypi_pkg__ = 'sqlsymphony_orm'


def introduction():
	table = Table(title="SQLSymphony ORM - powerful and simple ORM for python", expand=True)

	table.add_column("Key", style='blue')
	table.add_column('Value', style='green')
	table.add_column('Description', style='magenta')

	table.add_row('Version', __version__, 'Stable')
	table.add_row('Author', __author__, 'Maintainer&Developer')
	table.add_row('License', __license__, 'License of library')
	table.add_row('Language', __language__, 'Main language')
	table.add_row('PyPi pep package', __pypi_pkg__, 'Package name')

	console = Console()
	console.print(table)

introduction()
