import cv2
import math
#import numpy as np
#from sklearn.cluster import KMeans

class Colour:
    def __init__(self,config):
        self.config = config
        self.swatch = {
            'blue': ((108,75,140), (128,255,255)), # hue, saturation, value
            'cyan': ((88,75,140), (97,255,255)),
            'green': ((45,75,120), (75,255,255)),
            'red': ((88,0,0), (97,180,110)), # we will use cyan's threshold here
            'orange': ((17,75,205), (24,255,255)),
            'yellow': ((25,75,140), (35,255,255)),
            'purple': ((129,75,140), (138,255,255)),
            'pink': ((145,105,140), (155,255,255)),
            'brown': ((14,105,80), (18,180,205)),
            'white': ((0,0,205),(180,12,255)),
            'grey': ((0,0,102),(180,25,205)),
            'black': ((0,0,0),(180,255,12))
        }

    def process(self, image, data):
        hsvimg = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
        for k in self.swatch.keys():
            if k == "red": #if you are red, invert image and use cyan threshold
                hsvimg = (255-hsvimg)
            hsvimg = cv2.blur(hsvimg,(5,5))
            inrange = cv2.inRange(hsvimg, self.swatch[k][0], self.swatch[k][1])
            numinrange = cv2.countNonZero(inrange)
            size = hsvimg.shape[0] * hsvimg.shape[1]

            if size < 1:
                data[k] = -1
            else:
                data[k] = float(numinrange) / float(size) * 100.0

        return data
