import dlib
import numpy as np
from utils.face_encoding import FaceEncoding
from typing import List, Union


class FaceEncoder:
    def __init__(self, dlib_model_path: str):
        self._face_encoder = dlib.face_recognition_model_v1(dlib_model_path)

    def encode(self, face_image: Union[List, np.ndarray],
               dlib_face_landmarks: Union[List, np.ndarray]) -> List[FaceEncoding]:
        return [FaceEncoding(np.asarray(self._face_encoder.compute_face_descriptor(face_image, dlib_landmark, 1)))
                for dlib_landmark in dlib_face_landmarks]
