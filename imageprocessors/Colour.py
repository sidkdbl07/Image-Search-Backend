import cv2
import math
import numpy as np
from sklearn.cluster import KMeans

class Colour:
    def __init__(self):
        self.swatch = {
            'blue': ((100,50,50), (125,255,205)),
            'red': ((83,50,50), (95,255,205)), # we will use cyan's threshold here
            'green': ((36,50,50), (86,255,205)),
            'orange': ((10, 0, 20), (25,255,205)),
            'yellow': ((23, 0, 20), (32,255,205)),
            'cyan': ((83,50,50), (95,255,205)),
            'purple': ((128,50,50), (135,255,205)),
            'pink': ((135,50,50), (162,255,205)),
            'brown': ((10, 100, 20),(20, 255, 200)),
            'white': ((0,0,250),(255,255,255)),
            'black': ((0,0,0),(255,255,5))
        }

    def process(self, image, data):
        hsvimg = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)

        for k in self.swatch.keys():
            if k == "red": #if you are red, invert image and use cyan threshold
                hsvimg = (255-hsvimg)
            inrange = cv2.inRange(hsvimg, self.swatch[k][0], self.swatch[k][1])
            numinrange = cv2.countNonZero(inrange)
            size = hsvimg.shape[0] * hsvimg.shape[1]

            data[k] = float(numinrange) / float(size)

        return data
