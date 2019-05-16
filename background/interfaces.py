class FaceProcessor:

    def __call__(self, image):
        return self.process(image)

    def process(self, image):
        pass


class Preprocessing:

    def __call__(self, image):
        return self.preprocess(image)

    def preprocess(self, image):
        return image
