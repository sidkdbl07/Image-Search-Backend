import argparse
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
from imageprocessors import Colour, DifferenceHash, EXIF, Thumbnail

def format_timer(t):
    h = int(t/3600)
    m = int((t-h*3600)/60)
    s = int((t-h*3600-m*60))
    return str(h)+"h "+str(m)+"m "+str(s)+"s"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Find and process images")
    parser.add_argument("--mode", "-m", help="crawler: crawls the given directory (-d). processor: classifiier for found images.")
    parser.add_argument("--dir", "-d", help="local filesystem: root directory") # /mnt/pdrive
    parser.add_argument("--server", "-s", help="server path: root directory") # //s-ver-fs-01/projects
    parser.add_argument("--limit", "-l", help="the number of files to process before stopping", default=-1)
    args = parser.parse_args()

    if args.mode and args.mode == "crawler":
        start = timeit.default_timer()
        print "Entering crawler mode... ("+args.dir+" -> "+args.server+")"
        if args.dir:
            c = BasicCrawler()
            limit = int(args.limit)
            if limit != -1:
                print " Limit set to "+args.limit+" images"
            c.find_images(args.dir, args.server, args.limit)
        else:
            print "Directory not found. Quiting"
        print "Elapsed "+format_timer(timeit.default_timer() - start)

    if args.mode and args.mode == 'processor':
        start = timeit.default_timer()
        print "Entering processor mode... ("+args.dir+" -> "+args.server+")"
        # create instances of all processors, the process() function of each
        # processor will return the updated photo object
        thumbnails = Thumbnail()
        differencehash = DifferenceHash()
        exif = EXIF()
        colour = Colour()
        imageprocessors = [thumbnails,          # thumbnail, width, height
                           differencehash,      # differencehash
                           exif,                # location, datetaken
                           colour]              # white, grey, blue, red, orange, green, etc.
        # get some new images from the server. The server is expsected to send
        # a JSON array of image objects [{_id: <>, filepaths: <>, etc}]
        r = requests.get("http://localhost:3000/api/newphotos/"+urllib.quote_plus(args.server))
        data = json.loads(r.text)
        photos_to_process = data["total_new_photos"]
        # The images come in bunches (e.g. 100 new images at a time) so we loop
        # until the total number of images is zero.
        while photos_to_process > 0:
            for i in data["photos"]:
                try:
                    # We load the image and then pass it to each processor concurrently
                    path = args.dir + i["filepaths"][0].split(args.server)[1]
                    image = cv2.imread(path)
                    if image is not None:
                        for p in imageprocessors:
                            i = p.process(image, i)
                        if hasattr(i, 'location') and i["location"] is not None:
                            print i
                        i["status"] = 'processed'
                        r = requests.patch("http://localhost:3000/api/photos/"+i["_id"], data=i)
                    else:
                        # If we can't find the image, we immediately remove it from the database
                        print "Could not find image: "+i["filepaths"][0]
                        requests.delete("http://localhost:3000/api/photos/"+i["_id"])
                    # Get another batch of new images for the next loop
                    r = requests.get("http://localhost:3000/api/newphotos/"+urllib.quote_plus(args.server))
                    data = json.loads(r.text)
                    photos_to_process = data["total_new_photos"]
                except Exception as e:
                    message = "Exception encountered: {0}: {1}: {2}"
                    #print i
                    #print message.format(type(e).__name__.encode('utf-8'), i["filepaths"][0].encode('utf-8'), e.args)
                    requests.delete("http://localhost:3000/api/photos/"+i["_id"])

        print "Elapsed "+format_timer(timeit.default_timer() - start)

    if args.mode and args.mode == 'cleaner':
        start = timeit.default_timer()
        print "Entering cleaner mode... ("+args.dir+" -> "+args.server+")"
        # code here
        print "Elapsed "+format_timer(timeit.default_timer() - start)
