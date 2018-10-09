import cv2

class DifferenceHash:
    def __init__(self,config):
        self.hashsize = 8
        self.config = config

    def process(self, image, data):
        cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(image, (self.hashsize + 1, self.hashsize))
        diff = resized[:,1:] > resized[:,:-1]
        data["differencehash"] = sum([2 ** i for (i,v) in enumerate(diff.flatten()) if v])
        return data
