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

```
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Key              ┃ Value           ┃ Description          ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ Version          │ 0.1.0           │ Stable               │
│ Author           │ alexeev-prog    │ Maintainer&Developer │
│ License          │ GNU GPL v3      │ License of library   │
│ Language         │ Python 3.12.7   │ Main language        │
│ PyPi pep package │ sqlsymphony_orm │ Package name         │
└──────────────────┴─────────────────┴──────────────────────┘
```

## 🌟 Comparison with Alternatives

| Feature                          | SqlSymphony | SQLAlchemy | Peewee  |
| -------------------------------- | ----------- | ---------- | ------- |
| 💫 Simplicity                    | ✔️         | ✔️         | ❌      |
| 🚀 Performance                   | ✔️         | ❌         | ✔️      |
| 🌐 Database Agnosticism          | ❌         | ✔️         | ❌      |
| 📚 Comprehensive Documentation   | ✔️         | ✔️         | ✔️      |
| 🔥 Active Development            | ✔️         | ✔️         | ❌      |

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
from sqlsymphony import Model, fields

class User(Model):
    id = fields.IntegerField(primary_key=True)
    name = fields.CharField()
```

### Performing CRUD Operations

<details>
<summary>Create a new record</summary>

```python
user = User(name='John Doe', email='john.doe@example.com')
user.save()
```

</details>

<details>
<summary>Read records</summary>

```python
all_users = User.all()
user = User.get(id=1)
```

</details>

<details>
<summary>Update a record</summary>

```python
user = User.get(id=1)
user.email = 'new_email@example.com'
user.save()
```

</details>

<details>
<summary>Delete a record</summary>

```python
user = User.get(id=1)
user.delete()
```

</details>


## 🤝 Contributing

We welcome contributions from the community! If you'd like to help improve SqlSymphony, please check out the [contributing guidelines](https://github.com/alexeev-prog/SqlSymphony/blob/main/CONTRIBUTING.md) to get started.

## 💬 Support

If you encounter any issues or have questions about SqlSymphony, please:

- Check the [documentation](https://alexeev-prog.github.io/SQLSymphony) for answers
- Open an [issue on GitHub](https://github.com/alexeev-prog/SqlSymphony/issues/new)
- Reach out to the project maintainers via the [mailing list](mailto:alexeev.dev@mail.ru)

## 🔮 Roadmap

Our future goals for SqlSymphony include:

- 📚 Expanding support for more SQLite3 features
- 🚀 Improving performance through further optimizations
- ✅ Enhancing the testing suite and code coverage
- 🌍 Translating the documentation to multiple languages
- 🔧 Implementing advanced querying capabilities
