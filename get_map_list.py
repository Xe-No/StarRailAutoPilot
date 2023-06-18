import json

def get_map_list():
    with open('datas/tree.json', "r", encoding="utf-8") as j:
        tree = json.load(j)
    map_list = {}
    for map_d in tree['tree']:
        for children in map_d['children']:
            map_list[children['id']] = children['name']
    return map_list

print(get_map_list())