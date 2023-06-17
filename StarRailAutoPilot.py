from utils.cv_tracker import Tracker
from utils.log import log

path = 'maps/'
map_index = '39-1'

log.info(f'正在初始化Tracker')
tr = Tracker()

log.info(f'切换窗口')
tr.cc.switch_window()

tr.run_route(map_index)
