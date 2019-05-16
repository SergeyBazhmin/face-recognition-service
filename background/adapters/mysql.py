from background.adapters.base_adapter import Adapter, register
from background.adapters.db_enumerates import Database
from utils.face_encoding import FaceEncoding
import MySQLdb


@register(Database.MySQL)
class MysqlEmbeddings(Adapter):
    def __init__(self, table_name: str):
        self._connection = None
        self.table_name = table_name

    def connect(self, **kwargs):
        self._connection = MySQLdb.connect(**kwargs)

    def close(self):
        self._connection.close()

    def add_embedding(self, face_encoding: FaceEncoding, person_id: int):
        cols = ','.join([f'f{idx + 1}' for idx in range(face_encoding.data.shape[0])])
        query = f'insert into {self.table_name} (person_id,{cols}) values ({person_id}, {str(face_encoding)})'

        cursor = self._connection.cursor()

        cursor.execute(query)
        self._connection.commit()

    def select_similar(self, face_encoding: FaceEncoding, threshold: float = 0.6):
        cursor = self._connection.cursor()

        cols = [f'f{idx+1}' for idx in range(face_encoding.data.shape[0])]
        pows = '+'.join(list(map(lambda col, val: f'pow({col} - {val}, 2)', cols, face_encoding.data)))

        query = f'select person_id, {pows} as distance from {self.table_name} order by distance asc limit 1'

        cursor.execute(query)
        similar_person, distance = cursor.fetchone()
        if distance > threshold:
            similar_person = -1

        return similar_person, distance

    def create_table(self, n_cols: int):
        cursor = self._connection.cursor()

        columns = ['']*n_cols
        for idx, column in enumerate(columns):
            columns[idx] = f'f{idx+1} double'
        col_types = ','.join(columns)
        table_cmd = f'create table {self.table_name} (id serial primary key, person_id int,{col_types})'

        cursor.execute(f'{table_cmd}')
        self._connection.commit()
