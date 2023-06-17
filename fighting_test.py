from utils.calculated import calculated 
from utils.switch_window import switch_window as sw
import cv2 as cv

cc = calculated()
cc.switch_window()


# ss, left, top, right, bottom, width, length = cc.take_screenshot( points =(40,0,60,15))

# cv.imwrite('ss.png', ss)