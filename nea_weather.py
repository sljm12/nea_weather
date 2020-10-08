from PIL import Image
import datetime
import requests
import geopandas as gpd
from shapely.geometry import Point
import os
import sys


def get_date_time(delta=0):
    """

    :param delta: To move back the time by this value minutes. In case ur server and nea server time are not sync
    :return:
    """
    current = datetime.datetime.now()
    minute = current.minute if current.minute%5 == 0 else current.minute -  (current.minute%5)
    minute = minute - delta
    return "%d%s%s%d%d0000" % (current.year, "%02d"% current.month, "%02d"%current.day, current.hour, minute)


def download_rain_file(dir):
    filename = "dpsri_70km_%sdbr.dpsri.png" % get_date_time(5)
    url = "https://www.nea.gov.sg/docs/default-source/rain-area/%s" % (filename)
    r = requests.get(url)
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


if __name__ == "__main__":
    upper_left_x = 103.5544
    lower_right_x = 104.1337
    upper_left_y = 1.4771
    lower_right_y = 1.1530
    location = (sys.argv[1], sys.argv[2])

    filename = download_rain_file("rain")
    im = Image.open(filename)
    (x, y) = im.size
    arr_points = get_rain_area(im, x, y, upper_left_x, upper_left_y, lower_right_x, lower_right_y)

    rain_df = gpd.GeoDataFrame(data=arr_points, crs="EPSG:4326")

    myLoc = Point(location)
    buf = myLoc.buffer(0.009)

    with_buffer = []
    with_buffer.append({"type": "location", "geometry": buf})
    newDf = gpd.GeoDataFrame(data=with_buffer, crs="EPSG:4326")

    intersect = gpd.overlay(rain_df, newDf, how="intersection")

    print(len(intersect))