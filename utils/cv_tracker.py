#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Created by Xe-No at 2023/5/17
# 利用cv识别小地图并返回地图索引与坐标
import cv2 as cv
import time
import sys, os, glob
import utils.cv_tools as ct
from utils.switch_window import switch_window as sw
from utils.calculated import calculated 
from utils.get_angle import *
from utils.route_helper import *
from utils.log import log, set_debug
# from ray_casting import ray_casting
# import log
import win32api
import win32con
import pyautogui
import math

from PIL import Image


def match_scaled(img, template, scale, mask=False):
    # 返回最大相似度，中心点x、y
    t0 = time.time()
    resized_template = cv.resize(template, (0,0), fx=scale, fy=scale)
    if mask ==False:
        res = cv.matchTemplate(img, resized_template, cv.TM_CCORR_NORMED)
    else:
        res = cv.matchTemplate(img, resized_template, cv.TM_CCORR_NORMED, mask=resized_template)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
    h, w = resized_template.shape[:2]
    x, y = max_loc[0] + w/2, max_loc[1] + h/2
    return [max_val, int(x), int(y)]

def find_best_match(img, template, scale_range=(1.4, 2.0, 0.05), mask=False):
    best_match = None
    max_corr = -1
    print(img.shape)

    for scale in np.arange(scale_range[0], scale_range[1],scale_range[2]):
        if mask==False:
            [max_val, x, y] = match_scaled(img, template, scale)
        else:
            [max_val, x, y] = match_scaled(img, template, scale, mask=True)
        print(f'正在匹配 {scale}，相似度{max_val}，坐标{[x,y]}')
        if max_val > max_corr:
            max_corr = max_val
            max_ret = [x, y, scale, max_val]
    return max_ret


class Tracker():
    """docstring for Tracker"""
    def __init__(self):
        self.cc = calculated()

        self.map_prefix = 'datas/map_raw/'
        self.masked_map_prefix = 'datas/map_masked/'
        self.template_prefix = 'datas/map_template_sample/'
        self.result_prefix = 'datas/map_result/'

        # self.minimap_rect = [47,58,187,187] # 全尺度，只有圆形部分匹配度较差
        self.minimap_rect = [77,88,127,127]
        self.full_minimap_rect = [47,58,187,187]
        self.arrow_rect = [117,128,47,47]
        # 节省时间，只有需要时才调用load_all_masked_maps
        self.masked_maps = None
        self.bgr_minimap_enemy = [45,45,233] #红
        self.bgr_map_way = [0,255,255]# 黄
        self.bgr_map_start = [255,255,0] # 青


    def load_all_images(self, prefix, flag=cv.IMREAD_UNCHANGED):
        images = {}
        for file in glob.glob(f'{prefix}*.png'):
            index = os.path.basename(file)
            images[index] = cv.imread(file, flag)
        return images

    def load_all_gray_images(self, prefix):
        images = {}
        for file in glob.glob(f'{prefix}*.png'):
            index = os.path.basename(file)
            images[index] = cv.imread(file, cv.IMREAD_GRAYSCALE)
        return images

    def load_map(self, index, prefix):
        return cv.imread(prefix+index)

    def load_all_masked_maps(self):
        images = {}
        for file in glob.glob(f'{self.masked_map_prefix}*.png'):
            index = os.path.basename(file)
            images[index] = cv.cvtColor( cv.imread(file), cv.COLOR_BGR2GRAY)
        self.masked_maps = images
        return images

    def save_all_masked_maps(self):
        maps = self.load_all_images(self.map_prefix)
        # # 路面掩膜

        # show_img(b, 0.25)
        
        # map_b = get_mask(map_hsv,np.array([[0,0,30],[360,10,90]]))
        # map_b = cv.medianBlur(map_b, 5)
        # 路沿掩膜
        masked_maps = {}
        for index, map_r in maps.items():
            b, g, r, a = cv.split(map_r)
            mask = a>200
            b = b * mask
            map_b = cv.threshold(b, 20, 150, cv.THRESH_BINARY)[1]
            # map_hsv = cv.cvtColor(map_r, cv.COLOR_BGR2HSV)
            # map_s = get_mask(map_hsv,np.array([[0,0,180],[360,10,255]]))
            # map_s = cv.medianBlur(map_s, 3)
            masked_maps[index] = map_b
            cv.imwrite(self.masked_map_prefix + index, map_b)
        # 保存之后也返回
        return masked_maps

    def get_img(self, prefix=None, img_path=False ):
        if img_path:
            img_r = cv.imread(prefix + img_path)
        else:
            img_r = ct.take_screenshot(self.minimap_rect)
        return img_r

    def get_minimap_mask(self, mini_r, color_range = np.array([[0,0,180],[360,10,255]]) ):
        # img_hsv = cv.cvtColor(img_r, cv.COLOR_BGR2HSV)
        # img_s = get_mask(img_hsv, color_range)
        mini_r = cv.cvtColor(mini_r, cv.COLOR_BGR2GRAY)
        mini_b = cv.threshold(mini_r, 20, 150, cv.THRESH_BINARY)[1]
        kernel = np.ones((5, 5), np.uint8)
        mini_b = cv.dilate(mini_b, kernel, iterations=1)

        return mini_b

    def get_coord_by_map(self, map_b, img_r, scale=2.09):
        # 固定地图，识别坐标 map_index 图片索引 img 彩色图
        img_s =self.get_minimap_mask(img_r)
        img_s = cv.resize(img_s, (0,0), fx = scale, fy = scale) # 小地图到大地图的缩放尺度
        w,h = img_s.shape[:2]
        min_val, max_val, min_loc, max_loc = ct.get_loc(map_b, img_s)

        print(max_val)
        cx = max_loc[0] + w//2
        cy = max_loc[1] + h//2
        pos = [cx,cy]
        return [cx, cy, max_val]

    def get_coord_by_map2(self, map_bgra, img_r, scale_range=(1.66,2.09,0.05), rect=[0,0,0,0]):
        # 固定地图，识别坐标 map_index 图片索引 img 彩色图
        left, top, width, height = rect

        img_s = ct.get_mask_mk2(img_r)
        
        map_b = ct.get_mask_mk3(map_bgra)
        if rect != [0,0,0,0]:
            map_b = map_b[top:top+height,left:left+width]

        cv.imwrite('img.png', img_s)
        cv.imwrite('map.png', map_b)
        [cx, cy, max_val, scale] = find_best_match(map_b, img_s, scale_range=scale_range)
        x = left + cx
        y = top + cy

        return [int(x), int(y), max_val, scale]

    def get_front_angle(self):
        main_angle = get_angle()
        mini_r = ct.take_fine_screenshot(self.minimap_rect, n=1, dy=30)
        mini_r = cv.cvtColor(mini_r, cv.COLOR_BGR2GRAY)
        mini_b = cv.threshold(mini_r, 20, 150, cv.THRESH_BINARY)[1]
        # 扇形组成简易神经网络
        h,w = mini_r.shape[:2]
        fans = {}
        fans['f'] = ct.get_camera_fan(color = 255, angle=main_angle, w=w, h=h, delta=30, dimen=1, radius=60)
        fans['l'] = ct.get_camera_fan(color = 255, angle=main_angle-60, w=w, h=h, delta=90, dimen=1, radius=60)
        fans['r'] = ct.get_camera_fan(color = 255, angle=main_angle+60, w=w, h=h, delta=90, dimen=1, radius=60)
        # fans['b'] = get_camera_fan(color = 255, angle=main_angle-180, w=w, h=h, delta=90, dimen=1, radius=60)

        
        lx = np.linspace(-1, 1, w)
        ly = np.linspace(-1, 1, h) 
        xx, yy= np.meshgrid(lx,ly)
        rr = xx*xx++yy*yy
        count = {}
        for key, fan in fans.items():
            # cx = np.mean(xx * fan)
            # cy = np.mean(yy * fan)  
            count[key] = np.sum(mini_b * fan * rr)/255

        print(count)

        if count['f'] > 200:
            angle = 0
        else:
            if count['r'] > count['l']:
                angle =90
            else: 
                angle =-90

        return angle

    def move_octo(self, r0, r1, map_bgra, v=12):
        # 八方向移动
        print(f'开始从{r0}移动到{r1}')
        x0, y0 = r0
        x1, y1 = r1
        dx, dy = x1-x0, y1-y0
       
        angle = np.degrees(np.arctan2(dy, dx))
        r = np.linalg.norm([dx,dy])

        direction = int((angle +22.5)//45) % 8 # 0 东 1 东南 ...顺时针类推
        operator = ['d','ds','s','sa','a','aw','w','wd']
        for key in operator[direction]:
            pyautogui.keyDown(key)
        if r < 30:
            time.sleep(r/v)
            print(f'初始距离只有{r}像素，直接走')
        else:
            time.sleep(1)
            while 1:
                img_r = ct.take_screenshot(self.minimap_rect)
                [x,y,max_corr] = self.get_coord_by_map2( map_bgra, img_r, scale=2.09)
                x, y = int(x/2), int(y/2)
                dr = np.linalg.norm([x1-x,y1-y])
                print(f'目前位于{[x,y]}，距离目标点还有{dr}像素')
                if dr > 30:
                    time.sleep(0.5)
                else:
                    time.sleep(dr/v)
                    break

        for key in operator[direction]:
            pyautogui.keyUp(key)         

        time.sleep(0.1)



    def move_to(self, pos0, pos1, map_bgra, v=24):
        ix, iy = pos0
        tx, ty = pos1
        img_r = ct.take_screenshot(self.minimap_rect)

        img_s = ct.get_mask_mk2(img_r)
        map_b = ct.get_mask_mk3(map_bgra)

        dx01, dy01 = tx-ix,ty-iy
        rit = np.linalg.norm([dx01, dy01])  
        dex01, dey01 = [dx01, dy01]/rit # 起点目标单位向量 
        theta01 = np.arctan2(dy01,dx01)
        angle01 = np.rad2deg(theta01) 
        self.turn_to(angle01,moving=1)

        t0 = time.time()
        i=0
        
        walking = 0
        while 1:
            t1 = time.time()
            dt = t1-t0
            if i ==0:
                x,y = ix,iy
            if dt >1:
                if len(self.find_minimap_enemies()):
                    self.hunt()

                img_r = ct.take_screenshot(self.minimap_rect)
                img_s = ct.get_mask_mk2(img_r)
                print(f'识别前位置{[x,y]}')
                print(map_b[y-200:y+200,x-200:x+200].shape)

                # [max_corr, x,y] = match_scaled(map_b, img_s, scale = 2.09)
                # 相对匹配
                t2 =time.time()
                [max_corr, dx,dy] = match_scaled(map_b[y-200:y+200,x-200:x+200], img_s, scale = 2.09) #[y-200:y+200,x-200:x+200]
                t3 =time.time()
                print(f'图片匹配时间{t3-t2}')
                dx-=200
                dy-=200
                x+=dx
                y+=dy
                dx,dy = tx-x, ty-y
                theta = np.arctan2(dy,dx)
                angle = np.rad2deg(theta) 
                r = np.linalg.norm([dx,dy])  
                print(f'第{i}次定位，移动时间{dt}，将从{[x,y]}移动到{[tx,ty]}，相对位移{[dx,dy]}，匹配度{max_corr}')
                rc0 = np.linalg.norm([x-ix,y-iy])
                # 将dx,dy做旋转变换，dx_rot为 [当前to目标]在[初始to目标]方向上的投影，小于零说明走过头了，dy_rot则为最小距离，很大说明偏离主轴
                dx_rot = dex01 * dx + dey01 * dy 
                dy_rot = dey01 * dx - dex01 * dy

                # if dy_rot <5 and dx_rot > 0:
                if 1:
                    t2 =time.time()
                    self.turn_to(angle,moving=1)
                    t3 =time.time()
                print(f'转动时间{t3-t2}')
                time.sleep(0.01)
                # 提前停止转向，避免过度转向
                if dx_rot < 25:
                    rest_r = max(0,r-2)
                    print(f'只剩路程{r}，只走{rest_r}像素，等待{rest_r/v}秒')
                    # time.sleep(r/v)
                    break
                i+=1



    def find_minimap_enemies(self):
        minimap = ct.take_screenshot(self.minimap_rect)
        enemies = ct.find_color_points(minimap, self.bgr_minimap_enemy)
        return enemies

    def hunt(self):
        # 巡猎模式，小地图上有敌人时触发
        # 触发后，寻找最近的敌人并攻击
        # 小地图上没有敌人后解除
        # 默认处于前进状态
        cx,cy = self.minimap_rect[2] / 2, self.minimap_rect[3] / 2

        while 1:
            enemies = self.find_minimap_enemies()
            if len(enemies) >0:
                _, ne = ct.find_nearest_point(enemies, [cx,cy])
            else:
                break

            
            dx,dy = ne[0] - cx, ne[1] - cy
            angle, r = ct.cart_to_polar([dx,dy])
            if r < 30:
                # pyautogui.click()
                self.cc.fighting()
            self.turn_to(angle, moving=1)
        

    def move_to_st(self, pos, map_bgra):
        
        tx, ty = pos
        i = 0
        while 1:
            img_r = ct.take_screenshot(self.minimap_rect)

            rect = [x-200,y-200,400,400]
            [x,y,max_corr] = self.get_coord_by_map2( map_bgra, img_r, scale=2.09, rect= rect)
            dx,dy = tx-x, ty-y
            i+=1

            theta = np.arctan2(dy,dx)
            angle = np.rad2deg(theta) 
            r = np.linalg.norm([dx,dy])
            x_on = 0
            y_on = 0
            tolerance = 20

            if x_on == 0:
                if dx > tolerance:
                    pyautogui.keyDown('d')
                    x_on = 'd'
                if dx < -tolerance:
                    pyautogui.keyDown('a')
                    x_on = 'a'
            elif x_on == 'd':
                if dx < tolerance:
                    pyautogui.keyUp('d')
                    x_on = 0
            elif x_on == 'a':
                if dx > -tolerance:
                    pyautogui.keyUp('a')
                    x_on = 0

            if y_on == 0:
                if dy > tolerance:
                    pyautogui.keyDown('s')
                    y_on = 's'
                if dy < -tolerance:
                    pyautogui.keyDown('w')
                    y_on = 'w'
            elif y_on == 's':
                if dy < tolerance:
                    pyautogui.keyUp('s')
                    y_on = 0
            elif y_on == 'w':
                if dy > -tolerance:
                    pyautogui.keyUp('w')
                    y_on = 0
            print(f'将从{[x,y]}移动到{[tx,ty]}，相对位移{[dx,dy]}，x轴控制{x_on}，y轴控制{y_on}')

            if x_on== 0 and y_on==0:
                break
            time.sleep(0.5)

    # 计算旋转变换矩阵
    def handle_rotate_val(self, x, y, rotate):
        cos_val = np.cos(np.deg2rad(rotate))
        sin_val = np.sin(np.deg2rad(rotate))
        return np.float32(
            [
                [cos_val, sin_val, x * (1 - cos_val) - y * sin_val],
                [-sin_val, cos_val, x * sin_val + y * (1 - cos_val)],
            ]
        )

    # 图像旋转（以任意点为中心旋转）
    def image_rotate(self, src, rotate=0):
        h, w, c = src.shape
        M = self.handle_rotate_val(w // 2, h // 2, rotate)
        img = cv.warpAffine(src, M, (w, h))
        return img

    def get_now_direc(self):
        blue = np.array([234, 191, 4])
        arrow = cv.imread("imgs/loc_arrow.jpg")
        loc_tp = ct.take_screenshot(self.arrow_rect)
        loc_tp[np.sum(np.abs(loc_tp - blue), axis=-1) <= 50] = blue
        loc_tp[np.sum(np.abs(loc_tp - blue), axis=-1) > 0] = [0, 0, 0]
        mx_acc = 0
        ang = 0
        for i in range(0,360,30):
            rt = self.image_rotate(arrow, -i) # 顺时坐标系
            result = cv.matchTemplate(loc_tp, rt, cv.TM_CCORR_NORMED)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
            if max_val > mx_acc:
                mx_acc = max_val
                mx_loc = (max_loc[0] + 12, max_loc[1] + 12)
                ang = i

        for i in range(-30,30,6):
            i = (ang+i)%360
            rt = self.image_rotate(arrow, -i) # 顺时坐标系
            result = cv.matchTemplate(loc_tp, rt, cv.TM_CCORR_NORMED)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
            if max_val > mx_acc:
                mx_acc = max_val
                mx_loc = (max_loc[0] + 12, max_loc[1] + 12)
                ang = i

        for i in range(-6,6,1):
            i = (ang+i)%360
            rt = self.image_rotate(arrow, -i) # 顺时坐标系
            result = cv.matchTemplate(loc_tp, rt, cv.TM_CCORR_NORMED)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
            if max_val > mx_acc:
                mx_acc = max_val
                mx_loc = (max_loc[0] + 12, max_loc[1] + 12)
                ang = i
        ang = (ang - 90)%360

        return ang

    def turn_by(self, x, speed_factor=None):
        if x > 30:
            y = 30
        elif x < -30:
            y = -30
        else:
            y = x
        dx = int(9800 * y * 1295 / 1920 / 180 * 0.4624277456647399)

        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, 0)  # 进行视角移动
        time.sleep(0.1)
        if x != y:
            self.turn_by(x - y)


    def turn_to(self, target_angle,speed_factor=1, n=1, moving=0):
        # print(f'目标{target_angle}度')
        # 非移动状态，
        if moving == 0:
            pyautogui.press('w')
            time.sleep(0.2)
        # n为校准次数，至少为1 
        for _ in range(n):
            current_angle = self.get_now_direc() 
            turn_angle = target_angle - current_angle
            turn_angle -= round(turn_angle/360)*360
            self.turn_by(turn_angle,speed_factor)
 

    def turn_to_precise(self, target_angle, tolerance=4.0, moving=0):
        print(f'目标{target_angle}度')
        while 1:
            if moving == 0:
                pyautogui.press('w')
                time.sleep(0.2)
            current_angle = self.get_now_direc() 
            turn_angle = target_angle - current_angle
            turn_angle -= round(turn_angle/360)*360
            print(f'{turn_angle} {current_angle}')
            if abs(turn_angle) < tolerance:
                break

            self.turn_by(turn_angle)




    def find_map(self, img_r, scale=1.66):
        if self.masked_maps == None:
            self.load_all_masked_maps()
        max_index = -1
        max_corr = -1
        max_ret = None
        for index, map_b in self.masked_maps.items():
            # img_hsv = cv.cvtColor(img_r, cv.COLOR_BGR2HSV)
            # img_s = get_mask(img_hsv,np.array([[0,0,160],[360,10,255]]))

            img_s = self.get_minimap_mask(img_r)
            # show_img(img_s)
            print(f'正在匹配{index}的缩放尺度')
            # [scale, corr, loc] = find_best_match(map_b, img_s, (100,200,5))
            # [cx, cy, corr] = self.get_coord_by_map(self.masked_maps[index],img_r)
            [corr, loc] = match_scaled(map_b, img_s, scale)
            print(f'正在找{index}，相似度{corr}')
            # if corr < 0.5:
            #     continue
            if corr > max_corr:
                max_corr = corr
                max_ret = [index, corr, loc, scale]

            [index, corr, loc, scale] = max_ret
            [hh,hw] = img_r.shape[:2] # 半高半宽
            hh = int(hh * scale //2)
            hw = int(hw * scale //2)
            x = loc[0] + hw
            y = loc[1] + hh
            print(f'地图{index}的相似度为{corr},当前坐标为{[x,y]}')
        return [index, [x,y], [hw,hh] ,corr]

    def get_scale(self, map_b, mini_b ):

        # 获取小地图比例尺，一次获取，终生受益

        [scale, max_val, max_loc] = find_best_match(map_b, mini_b)
        # show_img(ret)
        [h, w] = mini_b.shape[:2]
        hf = int(h * scale)
        wf = int(w * scale)

        cv.rectangle(map_b, max_loc, np.add(max_loc, [wf,hf]), 255, 5   )
        ct.show_img(map_b, 0.25)
        
        return scale

    def run_route(self, map_index, path= 'maps/'):
        img_r = ct.take_screenshot(self.minimap_rect)
        map_bgra = cv.imread(f'{path}{map_index}', cv.IMREAD_UNCHANGED)
        map_bgr = cv.imread(f'{path}{map_index}')
        # self.load_all_masked_maps()

        r = np.sum((map_bgr-self.bgr_map_way)**2,axis=-1)<= 64

        # log.info(r.astype(np.uint8))
        way_points = ct.find_color_points(map_bgr, self.bgr_map_way)
        start_point = ct.find_color_points(map_bgr, self.bgr_map_start)[0]
        log.info(way_points)
        log.info(start_point)


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
            if i == 1:
                angle0, _ = ct.cart_to_polar([x1-x0,y1-y0])
                print(f'路线刚开始，先转向至{angle0}')
                pyautogui.press('w')
                time.sleep(0.5)
                self.turn_to(angle0)
                pyautogui.press('w')
                time.sleep(1)

                pyautogui.keyDown('w')
            self.move_to([x0, y0], [x1, y1], map_bgra)

        pyautogui.keyUp('w')

def test_1():

    tracker = Tracker()


    map_b = cv.imread(tracker.masked_map_prefix + '56.png', cv.IMREAD_GRAYSCALE)

    img_r = cv.imread(tracker.template_prefix+'screenshot_1684407906_26.png')
    img_b = tracker.get_minimap_mask(img_r, color_range = np.array([[0,0,180],[255,60,255]]))

    # img_g = cv.cvtColor(img_r, cv.COLOR_BGR2GRAY)
    # map_g = cv.cvtColor(map_r, cv.COLOR_BGR2GRAY)
    # # img_g = map_g[400:900,400:900]
    # map_g = cv.resize(map_g, (0,0) ,fx=1.2,fy=1.2)
    img_b = map_b[1000:1600,1000:1600]
    ret = sift_match(map_b,img_b)
    show_img(ret, 0.5)


    time.sleep(0.5)
    sw()
    time.sleep(0.5)




def test_2(index):
    # 找某张图缩放比

    time.sleep(0.5)
    sw()
    time.sleep(0.5)
    tr = Tracker()
    
    map_bgra = cv.imread(tr.map_prefix + index, cv.IMREAD_UNCHANGED) 
    b, g, r, a = cv.split(map_bgra)
    mask = a>200
    b = b * mask
    # show_img(b, 0.25)
    map_b = cv.threshold(b, 20, 150, cv.THRESH_BINARY)[1]

    mini = ct.take_fine_screenshot([77,88,127,127])
    show_img(mini)
    mini = cv.cvtColor(mini, cv.COLOR_BGR2GRAY)
    mini_b = cv.threshold(mini, 20, 150, cv.THRESH_BINARY)[1]
    print('?')
    kernel = np.ones((5, 5), np.uint8)
    mini_b = cv.dilate(mini_b, kernel, iterations=1)


    scale = tr.get_scale( map_b, mini_b)

    print(f'地图{index}最佳匹配缩放百分比为{scale}')

def test_3():
    # 将所有地图转为掩膜图
    tr = Tracker() 
    tr.save_all_masked_maps()

def test_4():
    # 找地图测试
    time.sleep(0.5)
    sw()
    time.sleep(0.5)
    tr = Tracker()



    img_r = ct.take_fine_screenshot(tr.minimap_rect)
    [index, [x,y], [hw,hh] ,corr] = tr.find_map(img_r )
    map_r = tr.load_map(index, tr.map_prefix)




    print([x,y])
    print([hw,hh])
    cv.rectangle(map_r, [x,y], [x+1,y+1], [0,0,255],5 )
    cv.rectangle(map_r, [x-hw,y-hh], [x+hw,y+hh], [255,0,0],5 )
    ct.show_img(img_r)
    show_img(map_r,0.25)

def test_5():
    time.sleep(0.5)
    sw()
    time.sleep(0.5)

    tr = Tracker()

    # pyautogui.keyDown('w')
    # for _ in range(20):
    #     front_angle = tr.get_front_angle()
    #     # char_angle = get_angle()
    #     # bias_angle = camera_angle-char_angle
    #     # bias_angle -= round((bias_angle)/360)*360
    #     # print(bias_angle)
    #     # win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(bias_angle*20), 0, 0, 0)
    #     turn_by(front_angle, speed_factor = 5)
    #     time.sleep(0.3)
    # # print(get_camera_angle())

    # pyautogui.keyUp('w')
    # show_img(mask)

def test_6():
    time.sleep(0.5)
    sw()
    time.sleep(0.5)

    img = ct.take_fine_screenshot()
    # img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    cv.imwrite( 'test.png', img)

def test_7():
    # 光线透射法暴力求最可能路径
    prefix = 'datas/'
    time.sleep(0.5)
    sw()
    time.sleep(0.5)
    tr = Tracker()

    while not get_image_pos(f'{prefix}atlas_portal.jpg', 0.9):
        image = ct.take_fine_screenshot(tr.minimap_rect)
        kernel = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=np.uint8)
        image =  cv2.dilate(image, kernel, iterations=1)
        image_b = get_binary(image, 30)
        angle_r = ray_casting(image_b, threshold=128, step=5)
        char_angle = get_angle()
        max_weight = -1
        max_angle_r = None
        final_angle = 0
        for angle, r in angle_r:
            # 根据角度对转向进行投票
            turn_angle = angle - char_angle
            turn_angle -= round(turn_angle/360)*360

            weight = np.sign(turn_angle) * r /60
            if abs(turn_angle) > 90:
                weight*=0.3
            final_angle  += weight * angle /18  


        # max_angle, max_r = max_angle_r
        print(f'角度{final_angle},半径{r}')
        r-=5
        if r>0 :
            turn_by(final_angle, speed_factor = 5.0)
            move(r/25)
            time.sleep(0.3)





if __name__ == '__main__':
    test_4()
    # test_6()
    index = '62.png'
    # test_2(index)
    # test_4()

