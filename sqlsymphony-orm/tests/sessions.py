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


class Comment(SessionModel):
	id = IntegerField(primary_key=True)
	name = TextField(null=False)
	user_id = IntegerField(null=False)


def test_sessions():
	user = User(name="John")
	user2 = User(name="Bob")
	user3 = User(name="Ellie")
	session.add(user)
	session.add(user2)
	session.add(user3)
	session.commit()
	session.delete(user3)
	session.commit()
	session.update(model=user2, name="Anna")
	session.commit()

	comment = Comment(name=user.name, user_id=user.pk)
	session.add(comment)
	session.commit()

	finded_user = session.filter(
		QueryBuilder()
		.SELECT(*User._original_fields.keys())
		.FROM(User.table_name)
		.WHERE(name="Anna")
	)[0]

	assert finded_user == user2


def test_all_models():
	all_models = session.get_all()
	all_users = session.get_all_by_model(User)

	assert len(all_models) == 4
	assert len(all_users) == 3
