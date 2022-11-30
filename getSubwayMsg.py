import numpy as np
import requests
import time

null = None  # 将json中的null定义为None
city_code = 257  # 广州的城市编号
station_info = requests.get('http://map.baidu.com/?qt=bsi&c=%s&t=%s' % (
    city_code,
    int(time.time() * 1000)
)
)
station_info_json = eval(station_info.content)  # 将json字符串转为python对象

# content = json.dumps(station_info_json)
# with open("content.json", "w") as fs:
#     fs.write(content)
