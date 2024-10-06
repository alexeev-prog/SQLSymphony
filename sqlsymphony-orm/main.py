from sqlsymphony_orm.datatypes.base import IntegerField, CharField
from sqlsymphony_orm.models.base import Model

# integer = IntegerField()
# integer.view_table_info()

# real = RealField()
# real.view_table_info()

# char = CharField()
# char.view_table_info()

# text = TextField()
# text.view_table_info()

# blob = BlobField()
# blob.view_table_info()


class User(Model):
	id = IntegerField(primary_key=True, auto_increment=True)
	name = CharField(max_length=64, unique=True)

	def __str__(self):
		return f'<User Model {self.id}>'


user = User(name='John Doe')
user.view_table_info()

user = User(name='Jane Doe')
user.view_table_info()
