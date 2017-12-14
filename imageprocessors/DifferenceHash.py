import cv2

class DifferenceHash:
    def __init__(self):
        self.hashsize = 8

    def process(self, image):
        cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(image, (self.hashsize + 1, self.hashsize))
        diff = resized[:,1:] > resized[:,:-1]
        return sum([2 ** i for (i,v) in enumerate(diff.flatten()) if v])
