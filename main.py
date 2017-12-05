import argparse
import os
import timeit

class Crawler:
    def __init__(self):
        self.allowed_ext = ('jpg','jpeg','png','tif','tiff','gif')
        self.image_list = ()

    def find_images(self, directory):
        filelist = []
        total_bytes = 0
        for root, dirs, files in os.walk(directory):
            filelist = filelist + [os.path.join(x,root) for x in files if x.lower().endswith(self.allowed_ext)]
            for f in files:
                path = os.path.join(root, f)
                total_bytes = total_bytes + os.stat(path).st_size
        print format_number(len(filelist))+" files"
        print format_number(int(total_bytes/1024/1024/1024))+" GB"

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
    parser.add_argument("--dir", "-d", help="root directory")
    args = parser.parse_args()

    if args.mode and args.mode == "crawler":
        start = timeit.default_timer()
        print "Entering crawler mode... ("+args.dir+")"
        if args.dir:
            app = Crawler()
            app.find_images(args.dir)
        else:
            print "Directory not found. Quiting"
        print "Elapsed "+format_timer(timeit.default_timer() - start)
    else:
        print "Doing nothing. Quitting."
