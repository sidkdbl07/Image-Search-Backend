import argparse
import os
import requests
import sys
import timeit

from imutils import paths
import json
import cv2
import urllib

from crawlers import BasicCrawler
from imageprocessors import DifferenceHash, Thumbnail

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
        print "Entering crawler mode... ("+args.dir+" -> "+args.server+")"
        if args.dir:
            c = BasicCrawler()
            c.find_images(args.dir, args.server)
        else:
            print "Directory not found. Quiting"
        print "Elapsed "+format_timer(timeit.default_timer() - start)

    if args.mode and args.mode == 'processor':
        start = timeit.default_timer()
        print "Entering processor mode... ("+args.dir+" -> "+args.server+")"
        # create instances of all processors, and add a dictionary. The keys of
        # the dictonary will be the attribute name in the image object on the
        # server. The results of the process() function will be the value.
        thumbnails = Thumbnail()
        differencehash = DifferenceHash()
        imageprocessors = {'thumbnail': thumbnails, 'differencehash': differencehash}
        # get some new images from the server. The server is expsected to send
        # a JSON array of image objects [{_id: <>, filepath: <>, etc}]
        r = requests.get("http://localhost:3000/api/newphotos/"+urllib.quote_plus(args.server))
        data = json.loads(r.text)
        photos_to_process = data["total_new_photos"]
        # The images come in bunches (e.g. 100 new images at a time) so we loop
        # until the total number of images is zero.
        while photos_to_process > 0:
            for i in data["photos"]:
                # We load the image and then pass it to each processor concurrently
                path = args.dir + i["filepath"].split(args.server)[1]
                image = cv2.imread(path)
                if image is not None:
                    for k,p in imageprocessors.iteritems():
                        i[k] = p.process(image)
                    i["status"] = 'processed'
                    r = requests.patch("http://localhost:3000/api/photos/"+i["_id"], data=i)
                else:
                    # If we can't find the image, we immediately remove it from the database
                    print "Could not find image: "+i["filepath"]
                    requests.delete("http://localhost:3000/api/photos/"+i["_id"])
            # Get another batch of new images for the next loop
            r = requests.get("http://localhost:3000/api/newphotos/"+urllib.quote_plus(args.server))
            data = json.loads(r.text)
            photos_to_process = data["total_new_photos"]

        print "Elapsed "+format_timer(timeit.default_timer() - start)

    if args.mode and args.mode == 'cleaner':
        start = timeit.default_timer()
        print "Entering cleaner mode... ("+args.dir+" -> "+args.server+")"
        # code here
        print "Elapsed "+format_timer(timeit.default_timer() - start)
