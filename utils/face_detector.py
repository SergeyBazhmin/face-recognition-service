import dlib
from utils.image_utils import *
from typing import List


class FaceDetector:
    def __init__(self, dlib_landmark_predictor: str, dlib_detector_model: str = None):
        if dlib_detector_model is None:
            self._face_detector = dlib.get_frontal_face_detector()
        else:
            self._face_detector = dlib.cnn_face_detection_model_v1(dlib_detector_model)
        self._landmark_predictor = dlib.shape_predictor(dlib_landmark_predictor)

    def dlib_face_locations(self, img: np.ndarray, upsample: int = 1) -> dlib.rectangles:
        return self._face_detector(img, upsample)

    def dlib_face_landmarks(self, img: np.ndarray, face_locations: dlib.rectangles) -> List[dlib.full_object_detection]:
        return [self._landmark_predictor(img, face_location) for face_location in face_locations]

    def boxed_face_locations(self, img: np.ndarray, upsample: int = 1) -> List[BoundingBox]:
        return [trim_box_to_bounds(dlib_rect_to_box(face.rect), img.shape)
                for face in self.dlib_face_locations(img, upsample)]

    def face_landmarks(self, face_image, face_locations):
        pass

