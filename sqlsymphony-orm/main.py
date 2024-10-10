from sqlsymphony_orm.datatypes.fields import IntegerField, CharField, TextField
from sqlsymphony_orm.models.orm_models import Model


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


video = Video(
	author="Alexeev",
	title="How to make your own ORM in python",
	description="Big video about python coding",
)
video.save()

video2 = Video(author="Alexeev", title="Test", description="An another video", views=1)
video2.save()

print(video.pk)
video2.delete()

print(video.objects.fetch())
