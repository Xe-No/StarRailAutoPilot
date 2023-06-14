import cv2 as cv
import numpy as np
import utils.jps as jps
import utils.astar as astar
import utils.cv_tools as ct


path = 'examples/60/'

# img = cv.cvtColor( cv.imread('map_with_target.png' ), cv.COLOR_BGR2RGB)
# matrix = np.all(img == [0,0,0], axis=-1).astype(np.uint8)

map_r = cv.imread(f'{path}60-tar.png', cv.IMREAD_UNCHANGED)
b, g, r, a = cv.split(map_r)
img = cv.merge((r,g,b))

kernel = np.ones((3, 3), np.uint8)
a = cv.erode(a, kernel, iterations=5)
mask = a<200

matrix = mask.astype(np.uint8)
cv.imwrite(f'{path}mask.png', matrix*255)
matrix = matrix.T


start = tuple( ct.find_color_points(img, [255,0,0])[0] )
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