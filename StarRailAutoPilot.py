from utils.log import log

log.info(f'导入模块')

import sys, os, re
import questionary
from utils.cv_tracker import Tracker
from get_map_list import get_map_list

path = 'maps/'
map_index = '39-1'



files = os.listdir(path)
# 使用正则表达式筛选出符合条件的文件名
pattern = r'\w+-\w+\.png'
matched_files = [f for f in files if re.match(pattern, f)]
map_list = get_map_list()


# Create a list of choices
choices = []
log.info(matched_files)
for f in matched_files:
    pattern = r"(\w+)-(\w+)\.png"
    match = re.search(pattern, f)

    map_id = match.group(1)
    map_name = map_list[int(map_id)]
    route_id = match.group(2)

    route_desc = f'地图{map_id}:{map_name}，路线{route_id}'
    log.info(route_desc)
    choices.append( { 'name': route_desc, 'value': f  })



title = '选择路线'


selection = questionary.select(title, choices=choices).ask()


print(f"You selected {selection}")


log.info(f'正在初始化Tracker')
tr = Tracker()

log.info(f'切换窗口')
tr.cc.switch_window()

tr.run_route(selection)


path = 'maps/'

files = os.listdir(path)