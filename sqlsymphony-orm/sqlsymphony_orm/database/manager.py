from abc import ABC, abstractmethod
from typing import Any

from sqlsymphony_orm.queries import QueryBuilder
from sqlsymphony_orm.database.connection import DBConnector, SQLiteDBConnector
from sqlsymphony_orm.models.orm_models import Model


class DBManager(ABC):
    def __init__(self, model_class: Model):
        self.model_class = model_class
        self._model_fields = model_class._original_fields.keys()

        q = QueryBuilder()

        self.q = q.SELECT(*self._model_fields).FROM(model_class._table_name)
        self.connector = DBConnector()

    @abstractmethod
    def filter(self, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def fetch(self):
        raise NotImplementedError()


class SQLiteDBManager(DBManager):
    def __init__(self, model_class: "Model", database_name: str = "database.db"):
        self.model_class = model_class
        self._model_fields = model_class._original_fields.keys()

        q = QueryBuilder()

        self.q = q.SELECT(*self._model_fields).FROM(model_class._table_name)
        self._connector = SQLiteDBConnector()

        if model_class._table_name != "model":
            self._connector.connect(database_name)

    def insert(self, table_name, columns, count, values):
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({count})"

        self._connector.fetch(query, values)
        self._connector.commit()

    def update(self, table_name, key, orig_field, new_value):
        query = f"UPDATE {table_name} SET {key} = ? WHERE {key} = ?"

        self._connector.fetch(query, (new_value, orig_field))
        self._connector.commit()

    def filter(self, *args, **kwargs):
        self.q = self.q.WHERE(*args, **kwargs)
        return self.fetch()

    def commit_changes(self):
        self._connector.commit()

    def create_table(self, table_name: str, fields: dict):
        columns = [f"{k} {v}" for k, v in fields.items()]

        query = f"CREATE TABLE IF NOT EXISTS {table_name} ("

        for column in columns:
            query += f"{column},"

        query = query[:-1]
        query += ")"

        self._connector.fetch(query)

    def delete(self, table_name: str, field_name: str, field_value: Any):
        query = f"DELETE FROM {table_name} WHERE {field_name} = ?"

        self._connector.fetch(query, (field_value,))
        self._connector.commit()

    def fetch(self):
        q = str(self.q)
        db_results = self._connector.fetch(q)
        self.q = (
            QueryBuilder()
            .SELECT(*self._model_fields)
            .FROM(self.model_class._table_name)
        )
        results = []

        for row in db_results:
            model = self.model_class(manager=True)

            for field, val in zip(self._model_fields, row):
                setattr(model, field, val)

            results.append(model)

        return results
