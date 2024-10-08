from sqlsymphony_orm.datatypes.fields import IntegerField, CharField
from sqlsymphony_orm.models.orm_models import Model


class User(Model):
	__tablename__ = 'Users'
	__database__ = 'users.db'

	id = IntegerField(primary_key=True)
	name = CharField(max_length=32, unique=True)

	def __repr__(self):
		return f'<User {self.id}>'


user = User(name='Charlie')
user.save()

user2 = User(name='John')
user2.save()

print(user.objects.fetch())
