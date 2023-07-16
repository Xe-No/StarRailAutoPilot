import os
import re
import json
import cv2 as cv
import numpy as np

import utils.cv_tools as ct
import utils.io_route as ior

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





def visualize_route(route_file):
    print(route_file)
    map_bgr = cv.imread(f'maps/{route_file}')
    sorted_waypoints = ior.import_route(f'maps/{route_file}')
    # return 
    ior.save_route(f'debug/{route_file}.json', sorted_waypoints)


    
    sorted_positions = [p.get('pos', None) for p in sorted_waypoints]

    # print(sorted_waypoints)
    # print(sorted_positions)

    line_img = np.zeros_like(map_bgr)
    ct.draw_lines(line_img, sorted_positions, color=[255, 255, 255], thickness=2)
    output = cv.addWeighted(map_bgr, 1, line_img, 0.1, 0)

    cv.imwrite(f'debug/v-{route_file}', output)


folder = 'maps/'

files = os.listdir(folder)

# 使用正则表达式筛选出符合条件的文件名
pattern = r'\w+-\w+\.png'
matched_files = [f for f in files if re.match(pattern, f)]
print(matched_files)
for file in matched_files:
    visualize_route(file)
    break
