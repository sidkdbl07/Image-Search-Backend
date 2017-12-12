import argparse
import os
import requests
import sys
import timeit

from imutils import paths
import base64
import cv2

class Crawler:
    def __init__(self):
        self.allowed_ext = ('jpg','jpeg','png','tif','tiff','gif')
        self.image_list = ()

    def find_images(self, directory, serverpath):
        image_list = []
        image_bytes = 0
        total_bytes = 0
        for root, dirs, files in os.walk(directory):
            image_list = image_list + [os.path.join(x,root) for x in files if x.lower().endswith(self.allowed_ext)]
            for f in files:
                path = os.path.join(root, f)
                if f.lower().endswith(self.allowed_ext):
                    image_bytes = image_bytes + os.stat(path).st_size
                    #print serverpath+path.split(directory)[1]
                    image = cv2.imread(path)
                    if image is None:
                        continue
                    thumb = self.thumbnail(image)
                    retval, buf = cv2.imencode('.jpg', thumb)
                    thumb = base64.b64encode(buf)
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    imagehash = self.dhash(image)
                    data = {'serverpath': serverpath+path.split(directory)[1],
                            'differencehash': imagehash,
                            'thumbnail': thumb}
                    requests.post("http://localhost:3000/api/photos", data=data)
                total_bytes = total_bytes + os.stat(path).st_size
        print format_number(len(image_list))+" images"
        print format_number(int(total_bytes/1024/1024/1024))+" GB files"
        print format_number(int(image_bytes/1024/1024/1024))+" GB images"

    def dhash(self, image, hashsize=8):
        resized = cv2.resize(image, (hashsize + 1, hashsize))
        diff = resized[:,1:] > resized[:,:-1]
        return sum([2 ** i for (i,v) in enumerate(diff.flatten()) if v])

    def thumbnail(self, image):
        max_height = 167
        if(image.shape[1] > image.shape[0]): # landscape
            ratio = 167.0 / image.shape[1]
            dim = (167, int(image.shape[0]*ratio))
            return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
        ratio = 167.0 / image.shape[0]
        dim = (int(image.shape[1]*ratio), 167)
        return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

def format_number(n):
    return "{:,}".format(n)

def format_timer(t):
    h = int(t/3600)
    m = int((t-h*3600)/60)
    s = int((t-h*3600-m*60))
    return str(h)+"h "+str(m)+"m "+str(s)+"s"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Find and process images")
    parser.add_argument("--mode", "-m", help="crawler: crawls the given directory (-d). processor: classifiier for found images.")
    parser.add_argument("--dir", "-d", help="local filesystem: root directory")
    parser.add_argument("--server", "-s", help="server path: root directory")
    args = parser.parse_args()

    if args.mode and args.mode == "crawler":
        start = timeit.default_timer()
        print "Entering crawler mode... ("+args.dir+")"
        if args.dir:
            c = Crawler()
            c.find_images(args.dir, args.server)
        else:
            print "Directory not found. Quiting"
        print "Elapsed "+format_timer(timeit.default_timer() - start)
    else:
        print "Doing nothing. Quitting."
