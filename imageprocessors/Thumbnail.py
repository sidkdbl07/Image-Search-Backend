import cv2
import base64

class Thumbnail:
    def __init__(self):
        self.maxdim = 167

    def process(self, image, data):
        if(image.shape[1] > image.shape[0]): # landscape
            ratio = (1.0 * self.maxdim) / image.shape[1]
            dim = (self.maxdim, int(image.shape[0]*ratio))
            thumb = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
            retval, buf = cv2.imencode('.jpg', thumb)
            data["thumbnail"] = base64.b64encode(buf)
            data["width"] = image.shape[1]
            data["height"] = image.shape[0]
            return data
        ratio = (1.0 * self.maxdim) / image.shape[0]
        dim = (int(image.shape[1]*ratio), self.maxdim)
        thumb = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
        retval, buf = cv2.imencode('.jpg', thumb)
        data["thumbnail"] = base64.b64encode(buf)
        data["width"] = image.shape[1]
        data["height"] = image.shape[0]
        return data
