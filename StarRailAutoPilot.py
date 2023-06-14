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
map_index = '67-1'

img_r = ct.take_screenshot(tr.minimap_rect)
map_bgra = cv.imread(f'{path}{map_index}.png', cv.IMREAD_UNCHANGED)
map_bgr = cv.imread(f'{path}{map_index}.png')
# tr.load_all_masked_maps()

r = np.sum((map_bgr-tr.bgr_map_way)**2,axis=-1)<= 64

# log.info(r.astype(np.uint8))
way_points = ct.find_color_points(map_bgr, tr.bgr_map_way)
start_point = ct.find_color_points(map_bgr, tr.bgr_map_start)[0]
log.info(way_points)
log.info(start_point)

pyautogui.keyDown('w')
current_point = start_point
sorted_points = [start_point]
while 1:
	i, next_point = ct.find_nearest_point(way_points, current_point)
	log.info(next_point)

	current_point = next_point
	
	sorted_points.append(way_points.pop(i))
	if len(way_points) == 0:
		break

log.info(sorted_points)

for i in range(1, len(sorted_points)):
	x0, y0 = sorted_points[i-1]
	x1, y1 = sorted_points[i]
	tr.move_to([x0, y0], [x1, y1], map_bgra)

pyautogui.keyUp('w')
