import time, sys
import cv2 as cv
import numpy as np
import utils.jps as jps
import utils.astar as astar
import utils.cv_tools as ct
from utils.cv_tracker import Tracker
from utils.switch_window import switch_window as sw
import utils.route_helper as rh
from utils.get_angle import *

path = 'examples/51/'

tracker = Tracker()

time.sleep(0.5)
sw()
time.sleep(0.5)
tr = Tracker()

# ret= tr.get_now_direc()
# print(ret)
# tr.turn_to_precise(270)
# ret= tr.get_now_direc()
# print(ret)
# sys.exit()



img_r = ct.take_screenshot(tr.minimap_rect)
# [index, [x,y], [hw,hh] ,corr] = tr.find_map(img_r )
# print([index, [x,y], [hw,hh] ,corr] )
tr.load_all_masked_maps()

tr.turn_to_precise(270)

map_bgra = cv.imread('datas/map_raw/51.png', cv.IMREAD_UNCHANGED)
[x,y,max_corr] = tr.get_coord_by_map2( map_bgra, img_r, scale=1.66)

print([x, y, max_corr])
start = (x//2,y//2)

# img = cv.cvtColor( cv.imread('map_with_target.png' ), cv.COLOR_BGR2RGB)
# matrix = np.all(img == [0,0,0], axis=-1).astype(np.uint8)

map_r = cv.imread(f'{path}51.png', cv.IMREAD_UNCHANGED)
b, g, r, a = cv.split(map_r)
img = cv.merge((r,g,b))

kernel = np.ones((3, 3), np.uint8)
a = cv.erode(a, kernel, iterations=5)
mask = a<200

matrix = mask.astype(np.uint8)
cv.imwrite(f'{path}mask.png', matrix*255)
matrix = matrix.T


# start = tuple( ct.find_color_points(img, [255,0,0])[0] )



goal = tuple( ct.find_color_points(img, [0,255,0])[0] )


print(matrix)
print(start)
print(goal)

route1, run_time1 = jps.method(matrix,start,goal, hchoice = 2)
print(route1, run_time1)
for i in range(len(route1)-1):
    cv.line(img, route1[i], route1[(i + 1) % len(route1)], (255, 0, 0), 2)

cv.imwrite(f'{path}solve.png', img)
# route2, run_time2 = astar.method(matrix,start,goal, hchoice = 2)
# print(route2, run_time2)

map_bgra = cv.imread('datas/map_raw/51.png', cv.IMREAD_UNCHANGED)
# rh.turn_to_precise(-90)
for i in range(1, len(route1)):
    x0, y0 = route1[i-1]
    x1, y1 = route1[i]
    
    tr.move_octo([x0,y0],[x1,y1],map_bgra)