import pytest
from background.adapters import adapter_registry, Database, Adapter
from my_model import Model
from PIL import Image
import numpy as np
from common.constants import ROOT_DIR
import os

mysql_settings = {
    'host': 'localhost',
    'user': 'root',
    'password': 'admin',
    'port': 3306,
    'database': 'embeddings'
}

postgresql_settings = {
    'host': 'localhost',
    'user': 'postgres',
    'password': 'admin',
    'port': 5432,
    'database': 'users'
}


static_folder = ROOT_DIR / 'tests' / 'static'
test_images = os.listdir(static_folder)


@pytest.mark.parametrize("db_enum, db_settings, n_cols, init_params", [
    (Database.PostgreSQL, postgresql_settings, 2, {'table_name': 'embeddings', 'cube_dim': 64}),
    (Database.MySQL, mysql_settings, 128, {'table_name': 'embeddings'})
])
def test_db_embedding_adding(db_enum, db_settings, n_cols, init_params):
    db_adapter: Adapter = adapter_registry[db_enum](**init_params)
    db_adapter.connect(**db_settings)

    db_adapter.drop_table()
    db_adapter.create_table(n_cols)

    model = Model()
    encodings = []
    for image in test_images:
        person_id = image.split('_')[0]
        image_path = static_folder / image
        img = np.asarray(Image.open(str(image_path)))
        enc = model(img)
        encodings.append((enc, int(person_id)))

    for enc, person_id in encodings:
        db_adapter.add_embedding(enc, person_id)

    rows = db_adapter.select_all()
    assert len(rows) == len(test_images)

    for idx, image in enumerate(test_images):
        enc, expected_id = encodings[idx]
        actual_person, _ = db_adapter.select_similar(enc)
        assert actual_person == expected_id

    db_adapter.drop_table()
    db_adapter.close()
