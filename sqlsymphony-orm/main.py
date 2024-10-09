from sqlsymphony_orm.datatypes.fields import IntegerField, CharField
from sqlsymphony_orm.models.orm_models import Model
from sqlsymphony_orm.database.connection import SQLiteDBConnector


class User(Model):
	__tablename__ = "Users"
	__database__ = "users.db"

	id = IntegerField(primary_key=True)
	name = CharField(max_length=32, unique=True, null=False)

	def __repr__(self):
		return f"<User {self.id} {self.name}>"


connector = SQLiteDBConnector().connect()


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
