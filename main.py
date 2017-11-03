import argparse
import os
import time

class Crawler:
    def __init__(self):
        self.allowed_ext = ('jpg','jpeg','png','tif','tiff','gif')
        self.image_list = ()

    def find_images(self, directory):
        filelist = []
        for root, dirs, files in os.walk(directory):
            filelist = filelist + [os.path.join(x,root) for x in files if x.lower().endswith(self.allowed_ext)]
        print str(len(filelist))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Find and process images")
    parser.add_argument("--mode", "-m", help="crawler: crawls the given directory (-d). processor: classifiier for found images.")
    parser.add_argument("--dir", "-d", help="root directory")
    args = parser.parse_args()

    if args.mode and args.mode == "crawler":
        start = time.time()
        print "Entering crawler mode... ("+args.dir+")"
        if args.dir:
            app = Crawler()
            app.find_images(args.dir)
        else:
            print "Directory not found. Quiting"

        print "Elapsed: "+str(time.time() - start)
    else:
        print "Doing nothing. Quitting."
