from datetime import datetime
import os
import requests


class BasicCrawler:
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
                    # send the image to the web service
                    data = {'filepath': serverpath+path.split(directory)[1],
                            'server': serverpath,
                            'datefound': datetime.now()}
                    r = requests.post("http://localhost:3000/api/photos", data=data)
                total_bytes = total_bytes + os.stat(path).st_size
        print self.format_number(len(image_list))+" images"
        print self.format_number(int(total_bytes/1024/1024/1024))+" GB files"
        print self.format_number(int(image_bytes/1024/1024/1024))+" GB images"

    def format_number(self, n):
        return "{:,}".format(n)
