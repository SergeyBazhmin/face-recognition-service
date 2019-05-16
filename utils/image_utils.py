from PIL import Image
import numpy as np
from dlib import rectangle
from typing import Tuple
from io import BytesIO
import base64

BoundingBox = Tuple[int, int, int, int]


def dlib_rect_to_box(rect: rectangle) -> BoundingBox:
    x = rect.left()
    y = rect.top()
    w = rect.right() - x
    h = rect.bottom() - y
    return x, y, w, h


def box_to_dlib_rect(box: BoundingBox) -> rectangle:
    x, y, w, h = box
    return rectangle(y, x + w, y + h, x)


def trim_box_to_bounds(box: BoundingBox, image_shape: Tuple[int, int]):
    x, y, w, h = box

    return max(x, 0), max(y, 0), min(x + w, image_shape[1]), min(y + h, image_shape[0])


def load_image(file: str, mode='RGB') -> np.ndarray:
    im = Image.open(file).convert(mode)
    return np.asarray(im)


def base64_decode_image(img):
    img = Image.open(BytesIO(base64.b64decode(img)))
    return np.asarray(img)
