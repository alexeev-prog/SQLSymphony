from sqlsymphony_orm.datatypes.base import IntegerField, CharField
from sqlsymphony_orm.models.base import Model, ModelManager
from sqlsymphony_orm.connections.database import SQLiteDatabaseConnection, DatabaseConnection

db = SQLiteDatabaseConnection('my.db')
db.connect()
model_manager = ModelManager(db)


@model_manager.register_model
class User(Model):
	__tablename__ = 'Users'

	id = IntegerField(primary_key=True, auto_increment=True, default=0)
	name = CharField(max_length=64, unique=True)
	

@model_manager.register_model
class Post(Model):
	__tablename__ = 'Posts'

	id = IntegerField(primary_key=True, auto_increment=True, default=0)
	title = CharField(max_length=128)


user = User(database_connection=db, model_manager=model_manager, name='John Doe')
user.save()

user2 = User(database_connection=db, model_manager=model_manager, name='Jane Doe')
user2.save()

user2.update_field('name', 'jane')

post1 = Post(database_connection=db, model_manager=model_manager, title='Howto')
post1.save()
