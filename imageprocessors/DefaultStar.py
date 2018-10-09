import cv2

class DefaultStar:
    def __init__(self,config):
        self.config = config

    def process(self, image, data):
        data["star"] = True
        return data
