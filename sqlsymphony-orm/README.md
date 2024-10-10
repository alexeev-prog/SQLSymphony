@mainpage
# SQLSymphony

<p align="center">A simple and powerful ORM library in Python</p>
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
| 💫 Simplicity                    | ✔️          | ✔️         | ❌      |
| 🚀 Performance                   | ✔️          | ❌         | ✔️      |
| 🌐 Database Agnosticism          | ❌          | ✔️         | ❌      |
| 📚 Comprehensive Documentation   | ✔️          | ✔️         | ✔️      |
| 🔥 Active Development            | ✔️          | ✔️         | ❌      |
| ⚡️ ASYNC Support                 | COMING SOON | ❌         | ❌      |

## 🤔 Why Choose SqlSymphony?

✨ Simplicity: SqlSymphony offers a straightforward and intuitive API for performing CRUD operations, filtering, sorting, and more, making it a breeze to work with databases in your Python projects.

💪 Flexibility: The library is designed to be database-agnostic, allowing you to switch between different SQLite3 implementations without modifying your codebase.

⚡️ Performance: SqlSymphony is optimized for performance, leveraging techniques like lazy loading and eager loading to minimize database queries and improve overall efficiency.

📚 Comprehensive Documentation: SqlSymphony comes with detailed documentation, including usage examples and API reference, to help you get started quickly and efficiently.

🔍 Maintainability: The codebase follows best practices in software engineering, including principles like SOLID, Clean Code, and modular design, ensuring the library is easy to extend and maintain.

🧪 Extensive Test Coverage: SqlSymphony is backed by a comprehensive test suite, ensuring the library's reliability and stability.

## 📚 Key Features

- Intuitive API: Pythonic, object-oriented interface for interacting with SQLite3 databases.
- Database Agnosticism: Seamlessly switch between different SQLite3 implementations.
- Performance Optimization: Lazy loading, eager loading, and other techniques for efficient database queries.
- Comprehensive Documentation: Detailed usage examples and API reference to help you get started.
- Modular Design: Clean, maintainable codebase that follows best software engineering practices.
- Extensive Test Coverage: Robust test suite to ensure the library's reliability and stability.

## 🚀 Getting Started

To install SqlSymphony, use pip:

```bash
pip install sqlsymphony_orm
```

Once installed, you can start using the library in your Python projects. Check out the [documentation](https://alexeev-prog.github.io/SQLSymphony) for detailed usage examples and API reference.

## 💻 Usage Examples

### Creating a Model

```python
from sqlsymphony_orm.datatypes.fields import IntegerField, CharField
from sqlsymphony_orm.models.orm_models import Model
from sqlsymphony_orm.queries import raw_sql_query
from sqlsymphony_orm.database.connection import SQLiteDBConnector


class User(Model):
    __tablename__ = "Users"
    __database__ = "users.db"

    id = IntegerField(primary_key=True)
    name = CharField(max_length=32, unique=True, null=False)

    def __repr__(self):
        return f"<User {self.id} {self.name}>"

connector = SQLiteDBConnector().connect()


@raw_sql_query(connector=connector)
def create_table(name: str):
    return 'CREATE TABLE IF NOT EXISTS %s (id INTEGER, name TEXT NOT NULL)' % (name,)


create_table('Memo')


user = User(name="Charlie")
user.save()

user2 = User(name="Carl")
user2.save()

user2.update(name="Bobby")

user3 = User(name="John")
user3.save()

user3.delete()

print(user.objects.fetch())
print(user.objects.filter(name="Bobby"))

user.view_table_info()
```

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

### Performing CRUD Operations

<details>
<summary>Create a new record</summary>

```python
user = User(name='Charlie')
user.save()

user2 = User(name='John')
user2.save()

print(user.objects.fetch())
```

</details>

<details>
<summary>Update record</summary>

```python
user2 = User(name="Carl")
user2.save()

user2.update(name="Bobby")

print(user.objects.fetch())
```

</details>

<details>
<summary>Delete record</summary>

```python
user = User(name="Charlie")
user.save()

user2 = User(name="Carl")
user2.save()

user3 = User(name="John")
user3.save()

user3.delete() # delete user3
# OR
user3.delete(field_name="name", field_value="Carl") # delete user2

print(user.objects.fetch())
```

</details>

<details>
<summary>Filter</summary>

```python
user = User(name="Charlie")
user.save()

user2 = User(name="Carl")
user2.save()

user2.update(name="Bobby")

user3 = User(name="John")
user3.save()

user3.delete()

print(user.objects.fetch())
print(user.objects.filter(name="Bobby"))
```

</details>

## ❌ Restrictions
Known limitations in SQLSymphony ORM are listed below:

### PrimaryKey Field
The PrimaryKey field in the model is not updated until the save method is called:

#### Good Code

```python
from sqlsymphony_orm.datatypes.fields import IntegerField, CharField, TextField
from sqlsymphony_orm.models.orm_models import Model


class Video(Model):
	__tablename__ = "Videos"
	__database__ = "videos.db"

	id = IntegerField(primary_key=True)
	author = CharField(max_length=32)
	title = CharField(max_length=64, null=False)
	description = TextField(null=False)
	views = IntegerField(null=False, default=0)

	def __repr__(self):
		return f"<Video {self.id} {self.title}>"


video = Video(author='Alexeev', title='How to make your own ORM in python', description='Big video about python coding')
video.save()

video2 = Video(author='Alexeev', title='Test', description='An another video', views=1)
video2.save()

print(video2.pk, video2.id)

print(video.objects.fetch())
```

#### Bad Code

```python
from sqlsymphony_orm.datatypes.fields import IntegerField, CharField, TextField
from sqlsymphony_orm.models.orm_models import Model


class Video(Model):
	__tablename__ = "Videos"
	__database__ = "videos.db"

	id = IntegerField(primary_key=True)
	author = CharField(max_length=32)
	title = CharField(max_length=64, null=False)
	description = TextField(null=False)
	views = IntegerField(null=False, default=0)

	def __repr__(self):
		return f"<Video {self.id} {self.title}>"


video = Video(author='Alexeev', title='How to make your own ORM in python', description='Big video about python coding')
video.save()

video2 = Video(author='Alexeev', title='Test', description='An another video', views=1)

print(video2.pk, video2.id) # value is none or primary key = 0

print(video.objects.fetch())
```

## 🤝 Contributing

We welcome contributions from the community! If you'd like to help improve SqlSymphony, please check out the [contributing guidelines](https://github.com/alexeev-prog/SqlSymphony/blob/main/CONTRIBUTING.md) to get started.

## 💬 Support

If you encounter any issues or have questions about SqlSymphony, please:

- Check the [documentation](https://alexeev-prog.github.io/SQLSymphony) for answers
- Open an [issue on GitHub](https://github.com/alexeev-prog/SQLSymphony/issues/new)
- Reach out to the project maintainers via the [mailing list](mailto:alexeev.dev@mail.ru)

## ☑️ Todos
 
 + Create Migrations system and Migrations Manager
 + Create ForeignKey field

## 🔮 Roadmap

Our future goals for SqlSymphony include:

- 📚 Expanding support for more SQLite3 features
- 🚀 Improving performance through further optimizations
- ✅ Enhancing the testing suite and code coverage
- 🌍 Translating the documentation to multiple languages
- 🔧 Implementing advanced querying capabilities
- 🚀 Add asynchronous operation mode
- ☑️ Add more fields
