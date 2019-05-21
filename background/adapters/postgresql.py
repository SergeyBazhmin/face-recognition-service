from background.adapters.db_enumerates import Database
from background.adapters.base_adapter import register, Adapter
from utils.face_encoding import FaceEncoding


try:
    import psycopg2

    @register(Database.PostgreSQL)
    class PostgresqlEmbeddings(Adapter):
        def __init__(self, table_name: str, cube_dim: int):
            self._connection = None
            self.table_name = table_name
            self.cube_dim = cube_dim

        def connect(self, **kwargs):
            self._connection = psycopg2.connect(**kwargs)

        def close(self):
            self._connection.close()

        def _get_sql_values_for_encoding(self, face_encoding: FaceEncoding):

            i = 0
            j = self.cube_dim
            total = face_encoding.data.shape[0]
            values = []
            while i < total:
                array_values_str = ','.join(str(element) for element in face_encoding.data[i:j])
                cube_str = f"cube(array[{array_values_str}])"
                values.append(cube_str)
                i = j
                j = min(total, i + self.cube_dim)

            return values

        def add_embedding(self, face_encoding: FaceEncoding, person_id: int):
            n_cubes = (face_encoding.data.shape[0] + self.cube_dim - 1) // self.cube_dim
            cubes = ','.join([f'cube_{idx + 1}' for idx in range(n_cubes)])

            cube_values_str = ','.join(self._get_sql_values_for_encoding(face_encoding))
            query = f'insert into {self.table_name} (person_id, {cubes}) values ({person_id},{cube_values_str})'

            cursor = self._connection.cursor()
            cursor.execute(query)
            self._connection.commit()

        def select_similar(self, face_encoding: FaceEncoding, threshold: float = 0.6) -> tuple:
            n_cubes = (face_encoding.data.shape[0] + self.cube_dim - 1) // self.cube_dim
            cube_cols = [f'cube_{idx + 1}' for idx in range(n_cubes)]

            cube_values = self._get_sql_values_for_encoding(face_encoding)
            cube_values = list(map(lambda values, col: f'power({values} <-> {col}, 2)', cube_values, cube_cols))
            cube_sum = '+'.join(cube_values)

            query = f'select person_id, {cube_sum} as distance from {self.table_name} order by distance asc limit 1'

            cursor = self._connection.cursor()
            cursor.execute(query)
            q_obj = cursor.fetchone()
            if q_obj is None:
                return -1, 1e9
            similar_person, distance = q_obj
            if distance > threshold:
                similar_person = -1

            return similar_person, distance

        def create_table(self, n_cols: int):
            cubes = [f'cube_{id+1} cube' for id in range(n_cols)]
            col_types = ','.join(cubes)
            table_cmd = f'create table if not exists {self.table_name} (id serial primary key, person_id int, {col_types})'
            cursor = self._connection.cursor()
            cursor.execute(table_cmd)
            self._connection.commit()
except ImportError:
    print('Postgresql adapter is not installed, skipping')