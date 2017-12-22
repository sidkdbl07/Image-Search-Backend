import exifread

class EXIF:
    def __init__(self):
        pass

    def process(self, image, data):
        # this only works on JPG and TIF files
        if not data['filepaths'][0].endswith(('jpg','jpeg','tif','tiff')):
            data["location"] = None
            data['datetaken'] = data["datefound"]
            return data
        path = data["directory"] + data["filepaths"][0].split(data["server"])[1]
        f = open(path,'rb')
        tags = exifread.process_file(f, details=False)
        gps_latitude = self.get_if_exists(tags, 'GPS GPSLatitude')
        gps_latitude_ref = self.get_if_exists(tags, 'GPS GPSLatitudeRef')
        gps_longitude = self.get_if_exists(tags, 'GPS GPSLongitude')
        gps_longitude_ref = self.get_if_exists(tags, 'GPS GPSLongitudeRef')

        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = _self.convert_to_degrees(gps_latitude)
            if gps_latitude_ref.values[0] != 'N':
                lat = 0 - lat

            lon = _self.convert_to_degrees(gps_longitude)
            if gps_longitude_ref.values[0] != 'E':
                lon = 0 - lon

            data['location'] = { "type": "Point", "coordinates": [ lon, lat ]}
            data['datetaken'] = self.get_if_exists(tags, 'EXIF DateTimeOriginal')
        else:
            data["location"] = None
            data['datetaken'] = self.get_if_exists(tags, 'EXIF DateTimeOriginal')
        return data

    def convert_to_degrees(self, value):
        d = float(value.values[0].num) / float(value.values[0].den)
        m = float(value.values[1].num) / float(value.values[1].den)
        s = float(value.values[2].num) / float(value.values[2].den)

        return d + (m / 60.0) + (s / 3600.0)

    def get_if_exists(self, data, key):
        if key in data:
            return data[key]
        return None
