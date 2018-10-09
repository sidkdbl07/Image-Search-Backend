import argparse
import configparser
from datetime import datetime
import importlib
import multiprocess as mp
import os
import requests
import sys
import timeit

from bson import json_util
from imutils import paths
import json
import cv2
import urllib

from crawlers import BasicCrawler
from imageprocessors import AEProjectInfo, Colour, DifferenceHash, EXIF, GoogleVisionAPILabels, Thumbnail

class ImageSearchBackend:
    def __init__(self, config):
        self.config = config
        # CRAWLER
        if "RUNTIME" in config and "MODE" in config["RUNTIME"] and config['RUNTIME']['MODE'] == "crawler":
            start = timeit.default_timer()
            print "Entering crawler mode... ("+config['RUNTIME']['DIRECTORY']+" -> "+config['RUNTIME']['SERVER']+")"
            if config['RUNTIME']['DIRECTORY']:
                c = BasicCrawler(config)
                if config['RUNTIME']['LIMIT'] != "None":
                    print " Limit set to "+config['RUNTIME']['LIMIT']+" images"
                c.find_images()
            else:
                print "Directory not found. Quiting"
            print "Elapsed "+self.format_timer(timeit.default_timer() - start)
        # PROCESSOR AND REPROCESS
        self.imageprocessors = []
        if self.config.has_option('PROCESSOR','USE_THUMBNAIL') and config['PROCESSOR']['USE_THUMBNAIL'] == "True":
            self.imageprocessors.append({"name": "Thumbnail", "procName": "Thumbnail"})
            # thumbnail, width, height
        if self.config.has_option('PROCESSOR','USE_DEFAULTSTAR') and config['PROCESSOR']['USE_DEFAULTSTAR'] == "True":
            self.imageprocessors.append({"name": "Default Star", "procName": "DefaultStar"})
            # differencehash
        if self.config.has_option('PROCESSOR','USE_DIFFERENCEHASH') and config['PROCESSOR']['USE_DIFFERENCEHASH'] == "True":
            self.imageprocessors.append({"name": "Difference Hash", "procName": "DifferenceHash"})
            # differencehash
        if self.config.has_option('PROCESSOR','USE_EXIF') and config['PROCESSOR']['USE_EXIF'] == "True":
            self.imageprocessors.append({"name": "EXIF", "procName": "EXIF"})
            # location, datetaken
        if self.config.has_option('PROCESSOR','USE_COLOUR') and config['PROCESSOR']['USE_COLOUR'] == "True":
            self.imageprocessors.append({"name": "Colour", "procName": "Colour"})
            # white, grey, blue, red, orange, green, etc.
        if self.config.has_option('PROCESSOR','USE_AEPROJECTINFO') and config['PROCESSOR']['USE_AEPROJECTINFO'] == "True":
            self.imageprocessors.append({"name": "AE Project Info", "procName": "AEProjectInfo"})
            # projectno
        if self.config.has_option('PROCESSOR','USE_GOOGLEVISIONAPILABELS') and config['PROCESSOR']['USE_GOOGLEVISIONAPILABELS'] == "True":
            self.imageprocessors.append({"name": "Google Vision API: Labels", "procName": "GoogleVisionAPILabels"})
            # projectno
        if "RUNTIME" in config and "MODE" in config["RUNTIME"] and (config['RUNTIME']['MODE'] == 'processor' or config['RUNTIME']['MODE'] == 'reprocess'):
            print "Processors to include:"
            for ip in self.imageprocessors:
                print " -"+ip["name"]
        # PROCESSOR
        if "RUNTIME" in config and "MODE" in config["RUNTIME"] and config['RUNTIME']['MODE'] == 'processor':
            start = timeit.default_timer()
            print "Entering processor mode... ("+config['RUNTIME']['DIRECTORY']+" -> "+config['RUNTIME']['SERVER']+")"
            # The config file specifies which processors we use. The individual
            # processors are instantiated on the fly by the procName
            cores = int(config['SYSTEM']['CORES'])
            # get some new images from the server. The server is expsected to send
            # a JSON array of image objects [{_id: <>, filepaths: <>, etc}]
            res = requests.get(config['RUNTIME']['WEBSERVER']+"/api/newphotos/"+urllib.quote_plus(config['RUNTIME']['SERVER'])+"/"+str(cores))
            data = json.loads(res.text)
            photos_to_process = data["total_new_photos"]
            print str(photos_to_process)+" new photos left"
            # The images come in bunches (e.g. 100 new images at a time) so we loop
            # until the total number of images is zero.
            while photos_to_process > 0:
                # We use multiprocess to parallellize the task for each photo
                # the config file specifes the number of cores and we use one
                # core per photo
                pool = mp.Pool(processes=int(cores))
                results = [pool.apply(self.process_image, args=(photodata,)) for photodata in data["photos"]]
                for r in results:
                    if not r:
                        print "An error occured"
                pool.terminate()

                # Get another batch of new images for the next loop
                res = requests.get(config['RUNTIME']['WEBSERVER']+"/api/newphotos/"+urllib.quote_plus(config['RUNTIME']['SERVER'])+"/"+str(cores))
                data = json.loads(res.text)
                photos_to_process = data["total_new_photos"]
                print str(photos_to_process)+" new photos left"

            print "Elapsed "+self.format_timer(timeit.default_timer() - start)

        # RE-PROCESS
        if "RUNTIME" in config and "MODE" in config["RUNTIME"] and config['RUNTIME']['MODE'] == 'reprocess':
            start = timeit.default_timer()
            print "Entering reprocess mode... ("+config['RUNTIME']['DIRECTORY']+" -> "+config['RUNTIME']['SERVER']+")"
            # The config file specifies which processors we use. The individual
            # processors are instantiated on the fly by the procName
            cores = int(config['SYSTEM']['CORES'])
            # get some new images from the server. The server is expsected to send
            # a JSON array of image objects [{_id: <>, filepaths: <>, etc}]
            res = requests.get(config['RUNTIME']['WEBSERVER']+"/api/processedphotos/"+urllib.quote_plus(config['RUNTIME']['SERVER'])+"/"+str(cores)+"/"+urllib.quote_plus(config['REPROCESS']['DATE']))
            data = json.loads(res.text)
            photos_to_process = data["total_photos"]
            print str(photos_to_process)+" photos left"
            # The images come in bunches (e.g. 100 images at a time) so we loop
            # until the total number of images is zero.
            while photos_to_process > 0:
                # We use multiprocess to parallellize the task for each photo
                # the config file specifes the number of cores and we use one
                # core per photo
                pool = mp.Pool(processes=int(cores))
                results = [pool.apply_async(self.process_image, args=(photodata,)) for photodata in data["photos"]]
                for r in results:
                    if not r:
                        print "An error occured"
                pool.close()
                pool.join()

                # Get another batch of new images for the next loop
                res = requests.get(config['RUNTIME']['WEBSERVER']+"/api/processedphotos/"+urllib.quote_plus(config['RUNTIME']['SERVER'])+"/"+str(cores)+"/"+urllib.quote_plus(config['REPROCESS']['DATE']))
                data = json.loads(res.text)
                photos_to_process = data["total_photos"]
                print str(photos_to_process)+" photos left"

            print "Elapsed "+self.format_timer(timeit.default_timer() - start)

        # CLEANER
        if "RUNTIME" in config and "MODE" in config["RUNTIME"] and config['RUNTIME']['MODE'] == 'cleaner':
            start = timeit.default_timer()
            print "Entering cleaner mode... ("+config['RUNTIME']['DIRECTORY']+" -> "+config['RUNTIME']['SERVER']+")"
            # code here
            print "Elapsed "+self.format_timer(timeit.default_timer() - start)

    def format_timer(self, t):
        d = int(t/86400)
        h = int((t-d*86400)/3600)
        m = int((t-d*86400-h*3600)/60)
        s = int((t-d*86400-h*3600-m*60))
        return str(d)+"d "+str(h)+"h "+str(m)+"m "+str(s)+"s"

    def process_image(self, data):
        print "Processing..."
        try:
            # We load the image and then pass it to each processor concurrently
            path = self.config['RUNTIME']['DIRECTORY'] + data["filepaths"][0].split(self.config['RUNTIME']['SERVER'])[1]
            image = cv2.imread(path)
            if image is not None:
                for p in self.imageprocessors:
                    mod = __import__('imageprocessors.'+p["procName"])
                    class_name = getattr(mod,p["procName"])
                    instance = class_name(self.config)
                    data = instance.process(image, data)
                data["status"] = 'processed'
                data["processeddate"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                res = requests.patch(self.config['RUNTIME']['WEBSERVER']+"/api/photos/"+data["_id"], data=data)
                return True
            else:
                # If we can't find the image, we immediately remove it from the database
                #print "Could not find image: "+i["filepaths"][0]
                res = requests.delete(self.config['RUNTIME']['WEBSERVER']+"/api/photos/"+data["_id"])
                return False
        except Exception as e:
            message = "Exception encountered {0}: {1}: {2}"
            print message.format(type(e).__name__.encode('utf-8'), data["filepaths"][0].encode('utf-8'), e.args)
            res = requests.delete(self.config['RUNTIME']['WEBSERVER']+"/api/photos/"+data["_id"])
            return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Find and process images")
    parser.add_argument("--config", "-c", help="config file", required=True)
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.config)
    myprog = ImageSearchBackend(config)
