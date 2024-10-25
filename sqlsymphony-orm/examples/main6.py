import asyncio
from sqlsymphony_orm.asyncio.datatypes.fields import IntegerField, RealField, TextField
from sqlsymphony_orm.asyncio.models.session_models import SessionModel
from sqlsymphony_orm.asyncio.models.session_models import SQLiteSession
from sqlsymphony_orm.asyncio.queries import QueryBuilder
from sqlsymphony_orm.asyncio.migrations.migrations_manager import SQLiteMigrationManager
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


async def main():
	user = User(name="John")
	user2 = User(name="Bob")
	user3 = User(name="Ellie")
	await session.add(user)
	await session.commit()
	await session.add(user2)
	await session.commit()
	await session.add(user3)
	await session.commit()
	await session.delete(user3)
	await session.commit()
	await session.update(model=user2, name="Anna")
	await session.commit()

	comment = Comment(name=user.name, user_id=user.pk)
	await session.add(comment)
	await session.commit()

	print(
		await session.filter(
			QueryBuilder().SELECT("*").FROM(User.table_name).WHERE(name="Anna")
		)
	)
	print(await session.get_all())
	print(await session.get_all_by_model(User))
	print(user.pk)

	migrations_manager = SQLiteMigrationManager(session)
	await migrations_manager.migrate_from_model(User, User2, "Users", "UserAnd")
	await migrations_manager.revert_migration(-1)

	await session.close()

	end = time()

	total = round(end - start, 2)

	print(f"Execution time: {total}s")


if __name__ == "__main__":
	asyncio.run(main())
