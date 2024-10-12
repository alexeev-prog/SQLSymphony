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
comment.add_hook("save", hello)
comment.save(ignore=True)
comment.commit()

print(video.objects.fetch())
print(comment.objects.fetch())
print(video2.get_audit_history())

connector = SQLiteDBConnector()
connector.connect("database.db")

with SQLiteDatabaseSession(connector, commit=True) as session:
	session.fetch(
		"CREATE TABLE IF NOT EXISTS BALABOLA (id INTEGER PRIMARY KEY, name VarChar(32))"
	)
