import cv2 as cv
import utils.cv_tools as ct
import numpy as np
import sys

'''

从米游社取得的原图有以下特点：
RGB值相等，等同于灰度图。

opencv的HSV范围为 180,255,255
标准HSV范围为 360,100,100
为了方便作图，我们这里讨论的HSV均为标准HSV

导航点的要求：
H!=0,S>10,V==100


导航点类型：
出发点：H==180 青色 仅有一个，
开拓导航点：（H==60 黄色）到达后不会进行任何动作，最常用的导航点
巡猎导航点：（H==10 红色）到达后会主动开启巡猎模式，孽物速速受死！
可破坏物导航点：（H==40 橙色）到达后会尝试进行一次攻击，一般用来收集垃圾桶，爷（「星」/「穹」）的最爱。没必要标在可破坏物的实际位置上，能攻击到就行。是否要区分开所有的可破坏物（血瓶、秘技瓶、垃圾桶等）有待考虑

导航点排序依据：
先根据 S 值降序排序，
如果有S值相同的情况下，选择离当前点最近的点。
'''
path = 'maps/'
map_index = '39-1'

map_bgr = cv.imread(f'{path}{map_index}.png')
map_hsv = cv.cvtColor(map_bgr, cv.COLOR_BGR2HSV)
imh, ims, imv = cv.split(map_hsv)

mask = np.uint8(ims>25)*255
points = ct.find_cluster_points(mask)
sorted_waypoints = ct.get_sorted_waypoints(map_hsv, points)
sorted_positions = [p.get('pos', None) for p in sorted_waypoints]

print(sorted_waypoints)
print(sorted_positions)

line_img = np.zeros_like(map_bgr)
route_map = ct.draw_lines(line_img, sorted_positions, color = [255,255,255], thickness=2)
output = cv.addWeighted(map_bgr, 1, line_img, 0.1, 0)

cv.imwrite('debug/route.png', output)
# log.info(r.astype(np.uint8))
# way_points = ct.find_color_points(h, h_pioneer, max_sq=1)
# start_point = ct.find_color_points(map_bgr, self.bgr_map_start)[0]
# log.info(way_points)
# log.info(start_point)
#
# current_point = start_point
# sorted_points = [start_point]
# while 1:
#     i, next_point = ct.find_nearest_point(way_points, current_point)
#     log.info(next_point)
#
#     current_point = next_point
#
#     sorted_points.append(way_points.pop(i))
#     if len(way_points) == 0:
#         break
