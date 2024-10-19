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
migrations_manager.revert_migration(-1)

session.close()

end = time()

total = round(end - start, 2)

print(f"Execution time: {total}s")
