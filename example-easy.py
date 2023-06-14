import cv2 as cv
import numpy as np
import utils.jps as jps
import utils.astar as astar
import utils.cv_tools as ct

path = 'examples/easy/'

img = cv.cvtColor( cv.imread(f'{path}tar.png' ), cv.COLOR_BGR2RGB)
matrix = np.all(img == [0,0,0], axis=-1).astype(np.uint8)

start = tuple( find_color_points(img, [255,0,0])[0] )
goal = tuple( find_color_points(img, [0,255,0])[0] )


print(matrix)
print(start)
print(goal)





route1, run_time1 = jps.method(matrix,start,goal, hchoice = 2)
print(route1, run_time1)

for i in range(len(route1)-1):
    cv.line(img, route1[i], route1[(i + 1) % len(route1)], (255, 0, 0), 2)

cv.imwrite('solve.png', img)
# route2, run_time2 = astar.method(matrix,start,goal, hchoice = 2)
# print(route2, run_time2)