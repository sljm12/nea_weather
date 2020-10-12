from PIL import Image
import datetime
import requests
from shapely.geometry import Point, MultiPoint
import os
import sys
from io import BytesIO


def get_date_time(delta_hours=0, delta_minutes=0):
    """

    :param delta_minutes: To move back the time by this value minutes. In case ur server and nea server time are not sync
    :return:
    """
    current = datetime.datetime.now()
    minute = current.minute if current.minute%5 == 0 else current.minute - (current.minute%5)
    minute = minute - delta_minutes if minute - delta_minutes > 0 else 0
    return "%d%s%s%s%s0000" % (current.year, "%02d"% current.month, "%02d"%current.day, "%02d"%(current.hour+delta_hours), "%02d"%minute)


def download_rain_file(mode="memory", dir="./"):
    filename = "dpsri_70km_%sdbr.dpsri.png" % get_date_time(0, 5)
    url = "https://www.nea.gov.sg/docs/default-source/rain-area/%s" % (filename)
    print(url)
    r = requests.get(url)
    if mode == "memory":
        return BytesIO(r.content)
    else:
        with open(os.path.join(dir, filename),'wb') as f:
            f.write(r.content)
        return os.path.join(dir, filename)


def find_x_pixel(ul_x,lr_x, x_len, x):
    range_x = lr_x - ul_x
    return x/float(x_len) * range_x +ul_x


def find_y_pixel(ul_y,lr_y, y_len, y):
    range_y = ul_y- lr_y
    return ul_y- (y/float(y_len) * range_y)


def get_rain_area(im, x, y, upper_left_x, upper_left_y, lower_right_x, lower_right_y):
    arr_points = []
    for px in range(x):
        for py in range(y):
            (r, g, b, a) = im.getpixel((px, py))
            if a == 255:
                point = Point((find_x_pixel(upper_left_x, lower_right_x, x, px),
                               find_y_pixel(upper_left_y, lower_right_y, y, py)))
                arr_points.append({"type": "rain", "geometry": point})
    return arr_points


class NeaWeatherProcessing:
    def __init__(self, rain_picture):
        self.upper_left_x = 103.5544
        self.lower_right_x = 104.1337
        self.upper_left_y = 1.4771
        self.lower_right_y = 1.1530
        self.rain_df = self.generate_rain_data_frame(rain_picture)

    def generate_rain_data_frame(self, picture_fp):
        """

        :param picture_fp: a file or a fp that PIL can use.
        :return:
        """
        im = Image.open(picture_fp)
        (x, y) = im.size
        arr_points = self.get_rain_area(im, x, y, self.upper_left_x, self.upper_left_y, self.lower_right_x, self.lower_right_y)

        #return gpd.GeoDataFrame(data=arr_points, crs="EPSG:4326")
        return arr_points

    def get_rain_area(self, im, x, y, upper_left_x, upper_left_y, lower_right_x, lower_right_y):
        """

        :param im: the PIL Image object
        :param x: the picture size
        :param y: the picture size
        :param upper_left_x: Extent of the image
        :param upper_left_y: Extent of the image
        :param lower_right_x: Extent of the image
        :param lower_right_y: Extent of the image
        :return:
        """
        arr_points = []
        for px in range(x):
            for py in range(y):
                (r, g, b, a) = im.getpixel((px, py))
                if a == 255:
                    point = Point((find_x_pixel(upper_left_x, lower_right_x, x, px),
                                   find_y_pixel(upper_left_y, lower_right_y, y, py)))
                    #arr_points.append({"type": "rain", "geometry": point})
                    arr_points.append(point)
        return MultiPoint(arr_points)

    def check_rain(self, long, lat, buffer_in_degrees):
        newDf = self.create_location_df(long, lat, buffer_in_degrees)

        #intersect = gpd.overlay(self.rain_df, newDf, how="intersection")
        #return len(intersect)
        return self.rain_df.intersects(newDf)

    def create_location_df(self, long, lat, buffer_in_degrees):
        """

        :param long:
        :param lat:
        :param buffer_in_degrees: roughly 0.009 is about 1km
        :return:
        """
        myLoc = Point((long, lat))
        buf = myLoc.buffer(buffer_in_degrees)
        return buf
        #with_buffer = [{"type": "location", "geometry": buf}]
        #return gpd.GeoDataFrame(data=with_buffer, crs="EPSG:4326")


if __name__ == "__main__":
    upper_left_x = 103.5544
    lower_right_x = 104.1337
    upper_left_y = 1.4771
    lower_right_y = 1.1530
    location = (float(sys.argv[1]), float(sys.argv[2]))

    filename = download_rain_file(mode="memory")

    a = NeaWeatherProcessing("testImage/a.png")
    intersect = a.check_rain(location[0], location[1], 0.009)
    print(intersect)