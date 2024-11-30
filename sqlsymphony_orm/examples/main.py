from sqlsymphony_orm.datatypes.fields import IntegerField, RealField, TextField
from sqlsymphony_orm.models.orm_models import Model
from sqlsymphony_orm.database.manager import SQLiteMultiModelManager
from time import time

start = time()


class BankAccount(Model):
    __tablename__ = "BankAccounts"
    __database__ = "bank.db"

    id = IntegerField(primary_key=True)
    name = TextField(null=False)
    cash = RealField(null=False, default=0.0)

    def __repr__(self):
        return f"<BankAccount {self.pk}>"


account = BankAccount(name="John", cash=100.0)
account2 = BankAccount(name="Bob", cash=100000000.0)
account2.save()
account2.commit()
account.save()
account.commit()

cash = float(100)
account.update(cash=account.cash + cash)
account.commit()
account2.update(cash=account2.cash - cash)
account2.commit()

print(account.cash, account2.cash)
print(BankAccount.objects.fetch())
print(BankAccount.objects.filter(name="Bob", first=True))

BankAccount.objects.drop_table()

mm_manager = SQLiteMultiModelManager("database.db")
mm_manager.add_model(account)
mm_manager.model_manager(account._model_name).create_table(
    account.table_name, account.get_formatted_sql_fields()
)
mm_manager.model_manager(account._model_name).insert(
    account.table_name, account.get_formatted_sql_fields(), account.pk, account
)
mm_manager.model_manager(account._model_name).commit()

end = time()

total = round(end - start, 2)

print(f"Execution time: {total}s")
