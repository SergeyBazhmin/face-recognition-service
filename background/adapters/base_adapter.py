from utils.face_encoding import FaceEncoding
from abc import abstractmethod

adapter_registry = {}


def register(database):
    def wrapper(cls):
        adapter_registry[database] = cls
        return cls
    return lambda x: wrapper(x)


class Adapter:

    @abstractmethod
    def connect(self, **kwargs):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def add_embedding(self, face_encoding: FaceEncoding, person_id: int):
        pass

    @abstractmethod
    def select_similar(self, face_encoding: FaceEncoding, threshold: float = 0.6) -> tuple:
        pass

    @abstractmethod
    def create_table(self, n_cols: int):
        pass

    def select_all(self):
        con = getattr(self, '_connection')
        cursor = con.cursor()
        table_name = getattr(self, 'table_name')
        cursor.execute(f'select * from {table_name}')
        return cursor.fetchall()

    def truncate(self):
        con = getattr(self, '_connection')
        cursor = con.cursor()
        table_name = getattr(self, 'table_name')
        cursor.execute(f'truncate table {table_name}')
        con.commit()

    def drop_table(self):
        con = getattr(self, '_connection')
        cursor = con.cursor()
        table_name = getattr(self, 'table_name')
        cursor.execute(f'drop table {table_name}')


