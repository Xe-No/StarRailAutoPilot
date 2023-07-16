import os
import re
import json
import cv2 as cv
import numpy as np
import jsbeautifier

from . import cv_tools as ct


# 自定义编码器，用于将uint8类型转换为整数
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.uint8):
            return int(obj)
        return super(NumpyEncoder, self).default(obj)

def import_route(path):
    map_bgr = cv.imread(path)
    map_hsv = cv.cvtColor(map_bgr, cv.COLOR_BGR2HSV)
    imh, ims, imv = cv.split(map_hsv)

    mask = np.uint8(ims > 25) * 255
    points = ct.find_cluster_points(mask)
    sorted_waypoints = ct.get_sorted_waypoints(map_hsv, points)
    return sorted_waypoints

def export_route(path, map_bgr, waypoints):
    pass


def save_route(path, waypoints):
    opts = jsbeautifier.default_options()
    opts.indent_size = 4
    opts.brace_style = 'expand'

    json_str = json.dumps(waypoints, cls=NumpyEncoder)
    json_str = jsbeautifier.beautify(json_str, opts)
    with open(path, 'w') as f:
        f.write(json_str)


        # json.dump(, f, cls=NumpyEncoder, indent=4, separators=(",", "} "))

def load_route(path):
    with open(path, 'r') as f:
        waypoints = json.load(f)    
    return waypoints