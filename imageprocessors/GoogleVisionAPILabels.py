import requests

class GoogleVisionAPILabels:
    def __init__(self, config):
        self.config = config

    def process(self, image, data):
        req = {
            "requests": [
                {
                    "image": {
                        "content": data["thumbnail"]
                    },
                    "features": [
                        {
                            "type": "SAFE_SEARCH_DETECTION"
                        },
                        {
                            "type": "LABEL_DETECTION"
                        }
                    ]
                }
            ]
        }
        url = "https://vision.googleapis.com/v1/images:annotate?key="+self.config['GOOGLE']['APP_KEY']
        #print url
        r = requests.post(url, json=req)
        #print r.text
        labels = []
        safesearchnogos = ["UNKNOWN","LIKELY","VERY_LIKELY"] # leaving out VERY_UNLIKELY, UNLIKELY, and POSSIBLE
        if r.status_code == 200:
            stop = False
            res = r.json()
            if "responses" in res:
                for response in res["responses"]:
                    if not stop:
                        if "labelAnnotations" in response:
                            for label in response["labelAnnotations"]:
                                if float(label["score"]) > 0.8:
                                    labels.append(label["description"])
                        if "safeSearchAnnotation" in response:
                            for nogo in safesearchnogos:
                                if response["safeSearchAnnotation"]["adult"] == nogo or response["safeSearchAnnotation"]["violence"] == nogo or response["safeSearchAnnotation"]["racy"] == nogo:
                                    stop = True
                                    labels = []
                                    data['quarantine'] = True
                    else:
                        break
            else:
                labels = []
        else:
            print "Google gave an error"
            labels = []
        data["labels"] = labels

        return data
