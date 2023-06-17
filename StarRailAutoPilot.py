import time, timeit, sys
from utils.cv_tracker import Tracker
from utils.log import log, set_debug

path = 'maps/'
map_index = '51-1'

tr = Tracker()
tr.cc.switch_window()

tr.run_route(map_index)
