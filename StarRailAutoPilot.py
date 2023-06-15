import time, timeit, sys
import cv2 as cv
import numpy as np
import utils.jps as jps
import utils.astar as astar
import utils.cv_tools as ct
from utils.cv_tracker import Tracker
from utils.switch_window import switch_window as sw
import utils.route_helper as rh
from utils.get_angle import *
from utils.log import log, set_debug

tr = Tracker()

time.sleep(0.1)
sw()
time.sleep(0.1)
tr = Tracker()

# minimap = ct.take_screenshot(tr.minimap_rect)
# cv.imwrite('minimap.png', minimap)
# enemies = ct.find_color_points(minimap, tr.bgr_minimap_enemy) 
# log.info(enemies)
# sys.exit()

# 地图目录以及路线索引
path = 'maps/'
map_index = '50-1'

tr.run_route(map_index)
