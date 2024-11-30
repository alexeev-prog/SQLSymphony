from sqlsymphony_orm.datatypes.fields import IntegerField, RealField, TextField
from sqlsymphony_orm.models.session_models import SessionModel
from sqlsymphony_orm.models.session_models import SQLiteSession
from sqlsymphony_orm.queries import QueryBuilder
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


print(
    session.filter(QueryBuilder().SELECT("*").FROM(User.table_name).WHERE(name="Anna"))
)
print(session.get_all_by_model(User))

session.close()

end = time()

total = round(end - start, 2)

print(f"Execution time: {total}s")
