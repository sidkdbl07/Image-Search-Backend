import re

class AEProjectInfo:
    def __init__(self,config):
        self.config = config

    def process(self, image, data):
        no = "n/a"
        if 'server' in data and data['server'] is not None:
            parts = data['server'].split("\\")
            if len(parts) >= 4 and parts[3] == 'projects':
                fileparts = data['filepaths'][0].split( data['server'] )[1].split("/")
                no = fileparts[1]

        if no != "n/a" and re.match("\d{8}",no):
            no = no[:4] + "-" + no[4:] #add a hyphen to the project number
        data["projectno"] = no

        return data
