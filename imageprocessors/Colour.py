import cv2
import math
import numpy as np
from sklearn.cluster import KMeans

class Colour:
    def __init__(self):
        self.swatch = {
            'blue': ((100,168,168), (124,255,255)), # hue, saturation, value
            'cyan': ((88,168,168), (97,255,255)),
            'green': ((50,168,168), (70,255,255)),
            'red': ((88,168,168), (97,255,255)), # we will use cyan's threshold here
            'orange': ((17,168,168), (24,255,255)),
            'yellow': ((25,168,168), (35,255,255)),
            'purple': ((129,168,168), (138,255,255)),
            'pink': ((88,38,168), (97,168,255)),
            'brown': ((17,168,50), (24,255,168)),
            'white': ((0,0,205),(180,50,255)),
            'black': ((0,0,0),(180,255,50))
        }

    def process(self, image, data):
        hsvimg = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)

        for k in self.swatch.keys():
            if k == "red" or k == "pink": #if you are red, invert image and use cyan threshold
                hsvimg = (255-hsvimg)
            inrange = cv2.inRange(hsvimg, self.swatch[k][0], self.swatch[k][1])
            numinrange = cv2.countNonZero(inrange)
            size = hsvimg.shape[0] * hsvimg.shape[1]

            data[k] = float(numinrange) / float(size)

        return data
