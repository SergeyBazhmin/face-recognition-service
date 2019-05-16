import numpy as np


class FaceEncoding:
    def __init__(self, face_encoding: np.ndarray):
        self._face_encoding = face_encoding

    @property
    def data(self) -> np.ndarray:
        return self._face_encoding

    def __str__(self):
        data_str = np.char.mod('%f', self.data)
        data_str = ','.join(data_str)
        return data_str
