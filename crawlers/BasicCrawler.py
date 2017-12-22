from datetime import datetime
import json
import os
import requests


class BasicCrawler:
    def __init__(self):
        self.allowed_ext = ('bmp','jpg','jpeg','png','tif','tiff')
        self.image_list = ()

    def find_images(self, directory, serverpath, limit):
        image_list = []
        image_bytes = 0
        total_bytes = 0
        stop = False
        for root, dirs, files in os.walk(directory):
            #image_list = image_list + [os.path.join(x,root) for x in files if x.lower().endswith(self.allowed_ext)]
            for f in files:
                path = os.path.join(root, f)
                if f.lower().endswith(self.allowed_ext):
                    image_bytes = image_bytes + os.stat(path).st_size
                    image_list.append(path)
                    if limit != -1 and len(image_list) >= int(limit):
                        stop = True
                    # send the image to the web service
                    data = dict(filepath=serverpath+path.split(directory)[1],
                                directory=directory,
                                server=serverpath,
                                datefound=datetime.now())
                    #r = requests.post("http://localhost:3000/api/photos", data=json.dumps(data, indent=4, sort_keys=True, default=str))
                    r = requests.post("http://localhost:3000/api/photos", data=data)
                total_bytes = total_bytes + os.stat(path).st_size
                if stop:
                    break
            if stop:
                break
        print self.format_number(len(image_list))+" images"
        print self.format_number(int(total_bytes/1024/1024/1024))+" GB files"
        print self.format_number(int(image_bytes/1024/1024/1024))+" GB images"

    def format_number(self, n):
        return "{:,}".format(n)

    def json_serializer(self, o):
        if isinstance(o, (datetime)):
            return o.__str__()
