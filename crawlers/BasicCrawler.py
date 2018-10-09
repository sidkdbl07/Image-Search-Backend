from datetime import datetime
import json
import os
import requests

class BasicCrawler:
    def __init__(self, config):
        self.config = config
        self.allowed_ext = ('bmp','jpg','jpeg','png','tif','tiff')
        self.image_list = ()

    def find_images(self):
        image_count = 0
        image_bytes = 0
        total_bytes = 0
        stop = False
        for root, dirs, files in os.walk(self.config['RUNTIME']['DIRECTORY']):
            for f in files:
                path = os.path.join(root, f)
                if f.lower().endswith(self.allowed_ext):
                    image_bytes = image_bytes + os.stat(path).st_size
                    image_count = image_count + 1
                    if self.config['RUNTIME']['LIMIT'] != 'None' and image_count >= int(self.config['RUNTIME']['LIMIT']):
                        stop = True
                    # send the image to the web service
                    data = dict(filepath=self.config['RUNTIME']['SERVER']+path.split(self.config['RUNTIME']['DIRECTORY'])[1],
                                directory=self.config['RUNTIME']['DIRECTORY'],
                                server=self.config['RUNTIME']['SERVER'],
                                datefound=datetime.now(),
                                star=False,
                                labels=[])
                    #r = requests.post("http://localhost:3000/api/photos", data=json.dumps(data, indent=4, sort_keys=True, default=str))
                    r = requests.post(self.config['RUNTIME']['WEBSERVER']+"/api/photos", data=data)
                total_bytes = total_bytes + os.stat(path).st_size
                if stop:
                    break
            if stop:
                break
        print self.format_number(image_count)+" images"
        print self.format_number(int(total_bytes/1024/1024/1024))+" GB files"
        print self.format_number(int(image_bytes/1024/1024/1024))+" GB images"

    def format_number(self, n):
        return "{:,}".format(n)

    def json_serializer(self, o):
        if isinstance(o, (datetime)):
            return o.__str__()
