# SQLSymphony
<a id="readme-top"></a> 

<div align="center">  
  <p align="center">
    SQLSymphony: The elegant and powerful SQLite3 ORM for Python
    <br />
    <a href="https://alexeev-prog.github.io/SQLSymphony/"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="#-comparison-with-alternatives">Comparison with Alternatives</a>
    .
    <a href="#-why-choose-sqlsymphony">Why Choose SQLSymphony</a>
    ·
    <a href="#-key-features">Key Features</a>
    ·
    <a href="#-getting-started">Getting Started</a>
    ·
    <a href="#-usage-examples">Basic Usage</a>
    ·
    <a href="#-specifications">Specification</a>
    ·
    <a href="https://alexeev-prog.github.io/SQLSymphony/">Documentation</a>
    ·
    <a href="https://github.com/alexeev-prog/SQLSymphony/blob/main/LICENSE">License</a>
  </p>
</div>
<br>
<p align="center">
	<img src="https://img.shields.io/github/languages/top/alexeev-prog/SQLSymphony?style=for-the-badge">
	<img src="https://img.shields.io/github/languages/count/alexeev-prog/SQLSymphony?style=for-the-badge">
	<img src="https://img.shields.io/github/license/alexeev-prog/SQLSymphony?style=for-the-badge">
	<img src="https://img.shields.io/github/stars/alexeev-prog/SQLSymphony?style=for-the-badge">
	<img src="https://img.shields.io/github/issues/alexeev-prog/SQLSymphony?style=for-the-badge">
	<img src="https://img.shields.io/github/last-commit/alexeev-prog/SQLSymphony?style=for-the-badge">
</p>

 > SQLSymphony: The elegant and powerful SQLite3 ORM for Python

SQLSymphony is a **lightweight** ✨, **powerful** 💪, and **high-performance**⚡️, Object-Relational Mapping (ORM) library for Python, designed to simplify the interaction with SQLite3 databases. It provides a Pythonic, object-oriented interface that allows developers to focus on their application's bussiness logic rather than the underlying database management.

<p align='center'>SQLSymphony ORM - powerful and simple ORM for python</p>

## 🌟 Comparison with Alternatives

| Feature                          | SqlSymphony  | SQLAlchemy | Peewee  |
| -------------------------------- | ------------ | ---------- | ------- |
| 💫 Simplicity                    | ✔️          | ✔️         | ✔️      |
| 🚀 Performance                   | ✔️          | ❌         | ✔️      |
| 🌐 Database Agnosticism          | ❌          | ✔️         | ❌      |
| 📚 Comprehensive Documentation   | ✔️          | ✔️         | ✔️      |
| 🔥 Active Development            | ✔️          | ✔️         | ❌      |
| 💻 Audit changes & reverts       | ✔️          | ❌         | ❌      |
| ⚡ ASYNC Support                 | ✔️          | ✔️ (v2)    | ❌      |

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 🤔 Why Choose SqlSymphony?

✨ Simplicity: SqlSymphony offers a straightforward and intuitive API for performing CRUD operations, filtering, sorting, and more, making it a breeze to work with databases in your Python projects.

💪 Flexibility: The library is designed to be database-agnostic, allowing you to switch between different SQLite3 implementations without modifying your codebase.

⚡️ Performance: SqlSymphony is optimized for performance, leveraging techniques like lazy loading and eager loading to minimize database queries and improve overall efficiency.

📚 Comprehensive Documentation: SqlSymphony comes with detailed documentation, including usage examples and API reference, to help you get started quickly and efficiently.

🔍 Maintainability: The codebase follows best practices in software engineering, including principles like SOLID, Clean Code, and modular design, ensuring the library is easy to extend and maintain.

🧪 Extensive Test Coverage: SqlSymphony is backed by a comprehensive test suite, ensuring the library's reliability and stability.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 📚 Key Features

- Intuitive API: Pythonic, object-oriented interface for interacting with SQLite3 databases.
- Database Agnosticism: Seamlessly switch between different SQLite3 implementations.
- Performance Optimization: Lazy loading, eager loading, and other techniques for efficient database queries.
- Comprehensive Documentation: Detailed usage examples and API reference to help you get started.
- Modular Design: Clean, maintainable codebase that follows best software engineering practices.
- Extensive Test Coverage: Robust test suite to ensure the library's reliability and stability.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 🚀 Getting Started

SQLSymphony is available on [PyPI](https://pypi.org/project/sqlsymphony_orm). Simply install the package into your project environment with PIP:

```bash
pip install sqlsymphony_orm
```

Once installed, you can start using the library in your Python projects. Check out the [documentation](https://alexeev-prog.github.io/SQLSymphony) for detailed usage examples and API reference.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 💻 Usage Examples

## Security.Hashing
A security  created for hash functions.

<details>

<summary>PlainHasher</summary>

```python
from sqlsymphony_orm.security.hashing import PlainHasher, HashAlgorithm

hasher = PlainHasher(HashAlgorithm.SHA512) # also: SHA256, SHA512, MD5, BLAKE2B, BLAKE2S

hash1 = hasher.hash('password')
hash2 = hasher.hash('pasword')

hasher.verify('password', hash1) # True
hasher.verify('password', hash2) # False
```

</details>

<details>

<summary>SaltedHasher</summary>

```python
from sqlsymphony_orm.security.hashing import SaltedHasher, HashAlgorithm

hasher = SaltedHasher(HashAlgorithm.SHA512, salt='SALT') # also: SHA256, SHA512, MD5, BLAKE2B, BLAKE2S
hasher2 = SaltedHasher(HashAlgorithm.SHA512, salt='SALT2') # also: SHA256, SHA512, MD5, BLAKE2B, BLAKE2S

hash1 = hasher.hash('password')
hash2 = hasher2.hash('password')

hasher.verify('password', hash1) # True
hasher.verify('password', hash2) # False
```

</details>

### Migrations from old model to new model
During migration, a migrations directory is created, where database backups are stored, as well as a file sqlsymphony_migrates.json, which stores information about migrations. If you want to restore the database, then call the revert_migration function with the index_key parameter (by default -1, that is, the last migration), it will take the name of the database backup from sqlsymphony_migrates.json and replace the current database with the backup one. The current database file is taken from Session.

<details>

<summary>Migrate from old model to new model</summary>

```python
from sqlsymphony_orm.datatypes.fields import IntegerField, RealField, TextField
from sqlsymphony_orm.models.session_models import SessionModel
from sqlsymphony_orm.models.session_models import SQLiteSession
from sqlsymphony_orm.queries import QueryBuilder
from sqlsymphony_orm.migrations.migrations_manager import SQLiteMigrationManager
from time import time

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
print(session.get_all_by_model(User))
print(user.pk)

migrations_manager = SQLiteMigrationManager(session)
migrations_manager.migrate_from_model(User, User2, "Users", "UserAnd")

session.close()

end = time()

total = round(end - start, 2)

print(f"Execution time: {total}s")
```

</details>

<details>

<summary>Revert last migration (rollback database)</summary>	

```python
from sqlsymphony_orm.datatypes.fields import IntegerField, RealField, TextField
from sqlsymphony_orm.models.session_models import SessionModel
from sqlsymphony_orm.models.session_models import SQLiteSession
from sqlsymphony_orm.queries import QueryBuilder
from sqlsymphony_orm.migrations.migrations_manager import SQLiteMigrationManager
from time import time

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
print(session.get_all_by_model(User))
print(user.pk)

migrations_manager = SQLiteMigrationManager(session)
migrations_manager.migrate_from_model(User, User2, "Users", "UserAnd")
migrations_manager.revert_migration(-1) # -1 is last index key

session.close()

end = time()

total = round(end - start, 2)

print(f"Execution time: {total}s")
```

</details>

### Fields
![fields](https://github.com/alexeev-prog/SQLSymphony/raw/refs/heads/main/docs/img/fields.png)

### Basic Features
<details>
<summary>Cache Performance</summary>

```python
from sqlsymphony_orm.performance.cache import cached, SingletonCache, InMemoryCache


@cached(SingletonCache(InMemoryCache, max_size=1000, ttl=60))
def fetch_data(param1: str, param2: str):
	return {'data': f'{param1} and {param2}'}

result1 = fetch_data('foo', 'bar')
print(result1) # caching
result2 = fetch_data('foo', 'bar')
print(result2) # cached

result3 = fetch_data('baz', 'qux')
print(result3) # not cached
```

</details>

<details>
<summary>RAW SQL Query</summary>

```python
from sqlsymphony_orm.database.connection import SQLiteDBConnector
from sqlsymphony_orm.queries import raw_sql_query

connector = SQLiteDBConnector().connect('database.db')


@raw_sql_query(connector=connector, values=('John',))
def insert():
	return 'INSERT INTO Users (name) VALUES (?)'
```

</details>

<details>
<summary>Session SQL Query Executor</summary>

```python
from sqlsymphony_orm.database.manager import SQLiteDatabaseSession
from sqlsymphony_orm.database.connection import SQLiteDBConnector

with SQLiteDatabaseSession(connector, commit=True) as session:
	session.fetch(
		"CREATE TABLE IF NOT EXISTS BALABOLA (id INTEGER PRIMARY KEY, name VarChar(32))"
	)
```	

</details>

<details>
<summary>MultiModel Manager</summary>

```python
from sqlsymphony_orm.datatypes.fields import IntegerField, CharField, RealField, TextField, SlugField
from sqlsymphony_orm.models.orm_models import Model
from sqlsymphony_orm.database.manager import SQLiteMultiModelManager


class BankAccount(Model):
	__tablename__ = 'BankAccounts'
	__database__ = 'bank.db'

	id = IntegerField(primary_key=True)
	name = TextField(null=False)
	cash = RealField(null=False, default=0.0)

	def __repr__(self):
		return f'<BankAccount {self.pk}>'

account = BankAccount(name="John", cash=100.0)

mm_manager = SQLiteMultiModelManager('database.db')
mm_manager.add_model(account)
mm_manager.model_manager(account._model_name).create_table(account._table_name, account.get_formatted_sql_fields())
mm_manager.model_manager(account._model_name).insert(account._table_name, account.get_formatted_sql_fields(), account.pk, account)
mm_manager.model_manager(account._model_name).commit()
```	

</details>

### Creating a Model

#### Session Style
With this method, you create and manage models and objects through an instance of the session class:

```python
from sqlsymphony_orm.datatypes.fields import IntegerField, RealField, TextField
from sqlsymphony_orm.models.session_models import SessionModel
from sqlsymphony_orm.models.session_models import SQLiteSession
from sqlsymphony_orm.queries import QueryBuilder

session = SQLiteSession('example.db')


class User(SessionModel):
	__tablename__ = "Users"

	id = IntegerField(primary_key=True)
	name = TextField(null=False)
	cash = RealField(null=False, default=0.0)

	def __repr__(self):
		return f'<User {self.pk}>'


user = User(name='John')
user2 = User(name='Bob')
user3 = User(name='Ellie')
session.add(user)
session.add(user2)
session.add(user3)
session.commit()
session.delete(user3)
session.commit()
session.update(model=user2, name='Anna')
session.commit()

print(session.filter(QueryBuilder().SELECT(*User._original_fields.keys()).FROM(User.table_name).WHERE(name='Anna')))

session.close()
```

##### Performing CRUD Operations

<details>
<summary>Drop table</summary>

```python
from sqlsymphony_orm.datatypes.fields import IntegerField, RealField, TextField
from sqlsymphony_orm.models.session_models import SessionModel
from sqlsymphony_orm.models.session_models import SQLiteSession
from sqlsymphony_orm.queries import QueryBuilder

session = SQLiteSession('example.db')


class User(SessionModel):
	__tablename__ = "Users"

	id = IntegerField(primary_key=True)
	name = TextField(null=False)
	cash = RealField(null=False, default=0.0)

	def __repr__(self):
		return f'<User {self.pk}>'


user = User(name='John')
user2 = User(name='Bob')
user3 = User(name='Ellie')
session.add(user)
session.add(user2)
session.add(user3)
session.commit()
session.delete(user3)
session.commit()
session.update(model=user2, name='Anna')
session.commit()

print(session.filter(QueryBuilder().SELECT(*User._original_fields.keys()).FROM(User.table_name).WHERE(name='Anna')))

session.drop_table()
session.close()
```	

</details>

<details>
<summary>Create a new record</summary>

```python
user = User(name='Charlie')
session.add(user)
session.commit()

user2 = User(name='John')
session.add(user2)
session.commit()

print(session.get_all())
```

</details>

<details>
<summary>Update record</summary>

```python
user = User(name='John')
user2 = User(name='Bob')
session.add(user)
session.add(user2)

session.update(model=user2, name='Anna')
session.commit()

print(session.get_all())
```

</details>

<details>
<summary>Delete record</summary>

```python
user = User(name='John')
user2 = User(name='Bob')
user3 = User(name='Ellie')

session.add(user)
session.add(user2)
session.add(user3)

session.commit()

session.delete(user3)

session.commit()

print(session.get_all())
```

</details>

<details>
<summary>Filter</summary>

```python
from sqlsymphony_orm.queries import QueryBuilder

user = User(name='John')
user2 = User(name='Bob')
user3 = User(name='Ellie')
session.add(user)
session.add(user2)
session.add(user3)
session.commit()
session.delete(user3)
session.commit()
session.update(model=user2, name='Anna')
session.commit()

print(session.filter(QueryBuilder().SELECT(*User._original_fields.keys()).FROM(User.table_name).WHERE(name='Anna')))
print(session.get_all())
```

</details>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

#### Model Style
With this method, you create and manage models and objects through an instance of the model class:

```python
from sqlsymphony_orm.datatypes.fields import IntegerField, CharField, RealField, TextField, SlugField
from sqlsymphony_orm.models.orm_models import Model
from sqlsymphony_orm.database.manager import SQLiteMultiModelManager


class BankAccount(Model):
	__tablename__ = 'BankAccounts'
	__database__ = 'bank.db'

	id = IntegerField(primary_key=True)
	name = TextField(null=False)
	cash = RealField(null=False, default=0.0)

	def __repr__(self):
		return f'<BankAccount {self.pk}>'


account = BankAccount(name='John', cash=100.0)
account2 = BankAccount(name='Bob', cash=100000000.0)
account2.save()
account2.commit()
account.save()
account.commit()

cash = float(input('Enter sum: '))
account.update(cash=account.cash + cash)
account.commit()
account2.update(cash=account2.cash - cash)
account2.commit()

print(account.cash, account2.cash)
print(BankAccount.objects.fetch())
print(BankAccount.objects.filter(name="Bob", first=True))

BankAccount.objects.drop_table()

mm_manager = SQLiteMultiModelManager('database.db')
mm_manager.add_model(account)
mm_manager.model_manager(account._model_name).create_table(account._table_name, account.get_formatted_sql_fields())
mm_manager.model_manager(account._model_name).insert(account._table_name, account.get_formatted_sql_fields(), account.pk, account)
mm_manager.model_manager(account._model_name).commit()
```

##### Performing CRUD Operations

<details>
<summary>Drop table</summary>

```python
from sqlsymphony_orm.datatypes.fields import IntegerField, CharField, RealField, TextField, SlugField
from sqlsymphony_orm.models.orm_models import Model


class BankAccount(Model):
	__tablename__ = 'BankAccounts'
	__database__ = 'bank.db'

	id = IntegerField(primary_key=True)
	name = TextField(null=False)
	cash = RealField(null=False, default=0.0)

	def __repr__(self):
		return f'<BankAccount {self.pk}>'


account = BankAccount(name='John', cash=100.0)
account2 = BankAccount(name='Bob', cash=100000000.0)
account2.save()
account2.commit()
account.save()
account.commit()

cash = float(input('Enter sum: '))
account.update(cash=account.cash + cash)
account.commit()
account2.update(cash=account2.cash - cash)
account2.commit()

print(account.cash, account2.cash)
print(BankAccount.objects.fetch())
print(BankAccount.objects.filter(name="Bob", first=True))

BankAccount.objects.drop_table()
```	

</details>

<details>
<summary>Create a new record</summary>

```python
user = User(name='Charlie')
user.save()
user.commit()

user2 = User(name='John')
user2.save()
user2.commit()

print(user.objects.fetch())
```

</details>

<details>
<summary>Update record</summary>

```python
user2 = User(name="Carl")
user2.save()
user2.commit()

user2.update(name="Bobby")
user2.commit()

print(user2.objects.fetch())
```

</details>

<details>
<summary>Delete record</summary>

```python
user = User(name="Charlie")
user.save()
user.commit()

user2 = User(name="Carl")
user2.save()
user2.commit()

user3 = User(name="John")
user3.save()
user3.commit()

user3.delete() # delete user3
# OR
user3.delete(field_name="name", field_value="Carl") # delete user2

user3.commit()

print(user.objects.fetch())
```

</details>

<details>
<summary>Filter</summary>

```python
user = User(name="Charlie")
user.save()
user.commit()

user2 = User(name="Carl")
user2.save()
user2.commit()

user2.update(name="Bobby")
user2.commit()

user3 = User(name="John")
user3.save()
user3.commit()

user3.delete()
user3.commit()

print(user.objects.fetch())
print(user.objects.filter(name="Bobby"))
```

</details>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 🔧 Specifications

![speed](https://github.com/alexeev-prog/SQLSymphony/raw/refs/heads/main/docs/img/speed.png)

Database attractions speed top:

1. Raw SQL Query 
2. Sessions Method
3. Models Method

### Session Specification
Session Models are a new, recommended way to work with models and the database. This method is suitable for more complex projects. If you have a light project, it is better to use <a href='#model-specification'>regular Models</a>.

#### SessionModel
A class of database model.

##### Self Variables
SessionModel has some global variables that are needed to configure database fields:

 + `__tablename__` - table name
 + `_ids` - the value from which the primary key calculation begins

The session model also has the following parameters, which are set at the stage of creating a class object:

 + `table_name` - same as `__tablename__`
 + `model_name` - class model name. if `__tablename__` or `__database__` are None, then their value is changed to the class model name.
 + `_original_fields` - dictionary with original fields. The dictionary looks like this: `'<field name>'='<field class>'`
 + `fields` - fields dictionary.
 + `unique_id` - an UUID4 of instance.
 + `_hooks` - a pre-action simple hooks dictionary.
 + `_last_action` - dictionary storing the last action.

##### Methods
Session Model has some methods and functions for interactions with database:

 + `pk` (property) - a primary key value.
 + `view_table_info()` - print beautiful table with some info about model.
 + `get_formatted_sql_fields(skip_primary_key: bool = False)` - return an dictionary with formatted fields for sql query (ex. insert)
 + `_class_get_formatted_sql_fields(skip_primary_key: bool = False)` - return an dictionary with formatted fields for sql query (class method)

#### Session
A class for session.

##### Self Variables
Session has some global variables that are needed to configure database:

 + `database_file` - filepath to database
 + `models` - dictionary with saved models.
 + `manager` - main database manager.
 + `audit_manager` - audit manager instance.

##### Methods
Session has some methods and functions for interactions with database:

 + `get_all()` - get all added models.
 + `get_all_by_model(self, needed_model: SessionModel)` - get all saved models by model type.
 + `drop_table(self, table_name: str)` - drop table.
 + `filter(self, query: 'QueryBuilder', first: bool=False)` - filter and get models by query.
 + `update(self, model: SessionModel, **kwargs)` - update model.
 + `add(self, model: SessionModel, ignore: bool=False)` - add (with `OR IGNORE` sql prefix if ignore is True) new model.
 + `delete(self, model: SessionModel)` - delete model.
 + `commit()` - commit changes.
 + `close()` - close connection.
 + `reconnect()` - reconnect to database.

### Model Specification
The Model class is needed to create a model. It acts as an element in the database and allows, through the objects subclass, to manage other objects of the class through the object.

#### Self Variables
Model has some global variables that are needed to configure database fields:

 + `__tablename__` - table name
 + `__database__` - database filepath
 + `__type__` - type of database. Default: `ModelManagerType.SQLITE3`.
 + `_ids` - the value from which the primary key calculation begins

The model also has the following parameters, which are set at the stage of creating a class object:

 + `table_name` - same as `__tablename__`
 + `database_name` - same as `__database_name__`
 + `model_name` - class model name. if `__tablename__` or `__database__` are None, then their value is changed to the class model name.
 + `_original_fields` - dictionary with original fields. The dictionary looks like this: `'<field name>'='<field class>'`
 + `objects` - an `ModelManager` instance. Example, if `__type__` is `ModelManagerType.SQLITE3`, `SQLiteModelManager`.
 + `fields` - fields dictionary.
 + `_hooks` - a pre-action simple hooks dictionary.
 + `audit_manager` - an audit manager instance.
 + `unique_id` - an UUID4 of instance.
 + `_last_action` - dictionary storing the last action.

#### Methods
Model has some methods and functions for interactions with database:

 + `pk` (property) - a primary key value.
 + `commit()` - method for commit changes to database.
 + `get_audit_history()` - return audit history list.
 + `view_table_info()` - print beautiful table with some info about model
 + `add_hook(before_action: str, func: Callable, func_args: tuple = ())` - add a hook.
 + `save(ignore: bool = False)` - insert model to database.
 + `update(**kwargs)` - update any value of model.
 + `delete(field_name: str = None, field_value: Any = None)` - delete self model or delete model by field name and value.
 + `rollback_last_action()` - revert last changes (one action)
 + `get_formatted_sql_fields(skip_primary_key: bool = False)` - return an dictionary with formatted fields for sql query (ex. insert)
 + `_class_get_formatted_sql_fields(skip_primary_key: bool = False)` - return an dictionary with formatted fields for sql query (class method)

#### Objects Instance
Below you can see the methods belonging to the objects instance. Through it you can manage this and other instances of the model:

 + `objects.drop_table(table_name: str=None)` - drop table. If table_name is None, drop current model table, if table_name is not None, drop table by name.
 + `insert(table_name: str, formatted_fields: dict, pk: int, model_class: 'Model', ignore: bool = False)` - insert fields by model.
 + `update(table_name: str, key: str, orig_field: str, new_value: str)` - update element in database.
 + `filter(first: bool=False, *args, **kwargs)` - filter and get model by kwargs.
 + `commit()` - commit changes.
 + `create_table(table_name: str, fields: dict)` - create table.
 + `delete(table_name: str, field_name: str, field_value: Any)` - delete element from database.
 + `fetch()` - fetch last query and return fetched result.

### SQLiteModelManager
This class describes a sqlite db manager.

#### Self variables
SQLite model manager has some global variables that are needed to configure management process and database connection:

 + `model_class` - main model class instance.
 + `_model_fields` - original fields of model.
 + `q` - basic `QueryBuilder` instance for fetch.
 + `_connector` - database connector.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 💬 Support
If you encounter any issues or have questions about SqlSymphony, please:

- Check the [documentation](https://alexeev-prog.github.io/SQLSymphony) for answers
- Open an [issue on GitHub](https://github.com/alexeev-prog/SQLSymphony/issues/new)
- Reach out to the project maintainers via the [mailing list](mailto:alexeev.dev@mail.ru)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 🤝 Contributing
We welcome contributions from the community! If you'd like to help improve SqlSymphony, please check out the [contributing guidelines](https://github.com/alexeev-prog/SqlSymphony/blob/main/CONTRIBUTING.md) to get started.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 🔮 Roadmap
Our future goals for SQLSymphony include:

- 📚 Expanding support for more SQLite3 features
- 🚀 Improving performance through further optimizations
- ✅ Enhancing the testing suite and code coverage
- 🌍 Translating the documentation to multiple languages
- 🔧 Implementing advanced querying capabilities
- 🚀 Add asynchronous operation mode
- ☑️ Add more fields
- ⌨️ Create ForeignKey field
- ⌨️ Create RelationShip
- 🖇️ Create more query-get methods
- ✈️ Create examples for flask, fastapi
- 🌐 Create software for remote connection to SQLSymphony Database

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License
Distributed under the GNU GPL v3 License. See [LICENSE](https://github.com/alexeev-prog/SQLSymphony/blob/main/LICENSE) for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>
