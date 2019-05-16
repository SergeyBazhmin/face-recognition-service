from utils.face_encoder import FaceEncoder
from utils.face_detector import FaceDetector
from background import FaceProcessor
from pathlib import Path

threshold = 0.6
face_landmarks = 68
shape_predictor_model_path = Path('./utils/models/shape_predictor_{}_face_landmarks.dat'.format(face_landmarks))
face_encoder_model_path = Path('./utils/models/dlib_face_recognition_resnet_model_v1.dat')


class Model(FaceProcessor):
    __slots__ = ['detector', 'encoder']

    def __init__(self):
        self.detector = FaceDetector(dlib_landmark_predictor=str(shape_predictor_model_path))
        self.encoder = FaceEncoder(dlib_model_path=str(face_encoder_model_path))

    def process(self, image):
        location_rects = self.detector.dlib_face_locations(image)
        landmarks = self.detector.dlib_face_landmarks(image, location_rects)
        face_descriptors = self.encoder.encode(image, landmarks)
        return face_descriptors[0]
