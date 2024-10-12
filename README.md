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
| ⚡ ASYNC Support                 | COMING SOON | ✔️         | ❌      |

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
<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Creating a Model

```python
from sqlsymphony_orm.datatypes.fields import IntegerField, CharField, TextField
from sqlsymphony_orm.models.orm_models import Model
from sqlsymphony_orm.database.manager import SQLiteDatabaseSession
from sqlsymphony_orm.database.connection import SQLiteDBConnector


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


class Comment(Model):
	__tablename__ = "Comments"
	__database__ = "videos.db"

	id = IntegerField(primary_key=True)
	video = IntegerField(null=False)

	def __repr__(self):
		return f"<Comment {self.id} {self.video}>"


# Simple hook
def hello():
	print("hello")


video = Video(
	author="Alexeev",
	title="How to make your own ORM in python",
	description="Big video about python coding",
)
video.save(ignore=True)
video.commit()

video2 = Video(author="Alexeev", title="Test", description="An another video", views=1)
video2.save(ignore=True)
video2.commit()
video2.update(views=102)
video2.delete()
video2.commit()
video2.rollback_last_action()
video2.commit()

comment = Comment(video=video2.pk)
comment.add_hook("save", hello) # register hook (exec before sql query exec)
comment.save(ignore=True)
comment.commit()

print(video.objects.fetch())
print(comment.objects.fetch())
print(video2.get_audit_history())
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

### Performing CRUD Operations

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

## 🤝 Contributing

We welcome contributions from the community! If you'd like to help improve SqlSymphony, please check out the [contributing guidelines](https://github.com/alexeev-prog/SqlSymphony/blob/main/CONTRIBUTING.md) to get started.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 💬 Support

If you encounter any issues or have questions about SqlSymphony, please:

- Check the [documentation](https://alexeev-prog.github.io/SQLSymphony) for answers
- Open an [issue on GitHub](https://github.com/alexeev-prog/SQLSymphony/issues/new)
- Reach out to the project maintainers via the [mailing list](mailto:alexeev.dev@mail.ru)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## ☑️ Todos
 
 + Create Migrations system and Migrations Manager
 + Create ForeignKey field
 + Create RelationShip

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 🔮 Roadmap

Our future goals for SqlSymphony include:

- 📚 Expanding support for more SQLite3 features
- 🚀 Improving performance through further optimizations
- ✅ Enhancing the testing suite and code coverage
- 🌍 Translating the documentation to multiple languages
- 🔧 Implementing advanced querying capabilities
- 🚀 Add asynchronous operation mode
- ☑️ Add more fields

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License

Distributed under the GNU GPL v3 License. See [LICENSE](https://github.com/alexeev-prog/SQLSymphony/blob/main/LICENSE) for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>
