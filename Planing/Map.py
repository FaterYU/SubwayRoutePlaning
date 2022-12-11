import random
import plotly.offline as py
import plotly.graph_objs as go
import requests
import time
import numpy as np
import math
import json

PI = math.pi

class Map:
    def _transformlat(self, coordinates):
        lng = coordinates[:, 0] - 105
        lat = coordinates[:, 1] - 35
        ret = -100 + 2 * lng + 3 * lat + 0.2 * lat * lat + \
            0.1 * lng * lat + 0.2 * np.sqrt(np.fabs(lng))
        ret += (20 * np.sin(6 * lng * PI) + 20 *
                np.sin(2 * lng * PI)) * 2 / 3
        ret += (20 * np.sin(lat * PI) + 40 *
                np.sin(lat / 3 * PI)) * 2 / 3
        ret += (160 * np.sin(lat / 12 * PI) + 320 *
                np.sin(lat * PI / 30.0)) * 2 / 3
        return ret

    def _transformlng(self, coordinates):
        lng = coordinates[:, 0] - 105
        lat = coordinates[:, 1] - 35
        ret = 300 + lng + 2 * lat + 0.1 * lng * lng + \
            0.1 * lng * lat + 0.1 * np.sqrt(np.fabs(lng))
        ret += (20 * np.sin(6 * lng * PI) + 20 *
                np.sin(2 * lng * PI)) * 2 / 3
        ret += (20 * np.sin(lng * PI) + 40 *
                np.sin(lng / 3 * PI)) * 2 / 3
        ret += (150 * np.sin(lng / 12 * PI) + 300 *
                np.sin(lng / 30 * PI)) * 2 / 3
        return ret


    def gcj02_to_wgs84(self,coordinates):
        """
        GCJ-02转WGS-84
        :param coordinates: GCJ-02坐标系的经度和纬度的numpy数组
        :returns: WGS-84坐标系的经度和纬度的numpy数组
        """
        ee = 0.006693421622965943  # 偏心率平方
        a = 6378245  # 长半轴
        lng = coordinates[:, 0]
        lat = coordinates[:, 1]
        is_in_china = (lng > 73.66) & (lng < 135.05) & (lat > 3.86) & (lat < 53.55)
        _transform = coordinates[is_in_china]  # 只对国内的坐标做偏移

        dlat = self._transformlat(_transform)
        dlng = self._transformlng(_transform)
        radlat = _transform[:, 1] / 180 * PI
        magic = np.sin(radlat)
        magic = 1 - ee * magic * magic
        sqrtmagic = np.sqrt(magic)
        dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * PI)
        dlng = (dlng * 180.0) / (a / sqrtmagic * np.cos(radlat) * PI)
        mglat = _transform[:, 1] + dlat
        mglng = _transform[:, 0] + dlng
        coordinates[is_in_china] = np.array([
            _transform[:, 0] * 2 - mglng, _transform[:, 1] * 2 - mglat
        ]).T
        return coordinates

    def bd09_to_gcj02(self, coordinates):
        """
        BD-09转GCJ-02
        :param coordinates: BD-09坐标系的经度和纬度的numpy数组
        :returns: GCJ-02坐标系的经度和纬度的numpy数组
        """
        x_pi = PI * 3000 / 180
        x = coordinates[:, 0] - 0.0065
        y = coordinates[:, 1] - 0.006
        z = np.sqrt(x * x + y * y) - 0.00002 * np.sin(y * x_pi)
        theta = np.arctan2(y, x) - 0.000003 * np.cos(x * x_pi)
        lng = z * np.cos(theta)
        lat = z * np.sin(theta)
        coordinates = np.array([lng, lat]).T
        return coordinates

    def bd09_to_wgs84(self, coordinates):
        """
        BD-09转WGS-84
        :param coordinates: BD-09坐标系的经度和纬度的numpy数组
        :returns: WGS-84坐标系的经度和纬度的numpy数组
        """
        return self.gcj02_to_wgs84(self.bd09_to_gcj02(coordinates))

    def mercator_to_bd09(self, mercator):
        """
        BD-09MC转BD-09
        :param coordinates: GCJ-02坐标系的经度和纬度的numpy数组
        :returns: WGS-84坐标系的经度和纬度的numpy数组
        """
        MCBAND = [12890594.86, 8362377.87, 5591021, 3481989.83, 1678043.12, 0]
        MC2LL = [[1.410526172116255e-08,   8.98305509648872e-06,    -1.9939833816331,
                200.9824383106796,       -187.2403703815547,      91.6087516669843,
                -23.38765649603339,      2.57121317296198,        -0.03801003308653,
                17337981.2],
                [-7.435856389565537e-09,  8.983055097726239e-06,   -0.78625201886289,
                96.32687599759846,       -1.85204757529826,       -59.36935905485877,
                47.40033549296737,       -16.50741931063887,      2.28786674699375,
                10260144.86],
                [-3.030883460898826e-08,  8.98305509983578e-06,    0.30071316287616,
                59.74293618442277,       7.357984074871,          -25.38371002664745,
                13.45380521110908,       -3.29883767235584,       0.32710905363475,
                6856817.37],
                [-1.981981304930552e-08,  8.983055099779535e-06,   0.03278182852591,
                40.31678527705744,       0.65659298677277,        -4.44255534477492,
                0.85341911805263,        0.12923347998204,        -0.04625736007561,
                4482777.06],
                [3.09191371068437e-09,    8.983055096812155e-06,   6.995724062e-05,
                23.10934304144901,       -0.00023663490511,       -0.6321817810242,
                -0.00663494467273,       0.03430082397953,        -0.00466043876332,
                2555164.4],
                [2.890871144776878e-09,   8.983055095805407e-06,   -3.068298e-08,
                7.47137025468032,        -3.53937994e-06,         -0.02145144861037,
                -1.234426596e-05,        0.00010322952773,        -3.23890364e-06,
                826088.5]]

        x = np.abs(mercator[:, 0])
        y = np.abs(mercator[:, 1])
        coef = np.array([
            MC2LL[index] for index in
            (np.tile(y.reshape((-1, 1)), (1, 6)) < MCBAND).sum(axis=1)
        ])
        return self.converter(x, y, coef)

    def converter(self, x, y, coef):
        x_temp = coef[:, 0] + coef[:, 1] * np.abs(x)
        x_n = np.abs(y) / coef[:, 9]
        y_temp = coef[:, 2] + coef[:, 3] * x_n + coef[:, 4] * x_n ** 2 + \
            coef[:, 5] * x_n ** 3 + coef[:, 6] * x_n ** 4 + coef[:, 7] * x_n ** 5 + \
            coef[:, 8] * x_n ** 6
        x[x < 0] = -1
        x[x >= 0] = 1
        y[y < 0] = -1
        y[y >= 0] = 1
        x_temp *= x
        y_temp *= y
        coordinates = np.array([x_temp, y_temp]).T
        return coordinates

    def loadByjson(self, filename="content.json"):
        with open(filename, "r") as fs:
            content = fs.read()
        station_info_json = json.loads(content)
        return station_info_json

    def prepare(self):
        null = None  # 将json中的null定义为None
        city_code = 257  # 广州的城市编号
        station_info = requests.get('http://map.baidu.com/?qt=bsi&c=%s&t=%s' % (
            city_code,
            int(time.time() * 1000)
        )
        )
        station_info_json = eval(station_info.content)  # 将json字符串转为python对象
        self.station_info_json=station_info_json
        # path_info_json=loadByjson('kktohs.json')

        mapbox_access_token = (
            'pk.eyJ1IjoibHVrYXNtYXJ0aW5lbGxpIiwiYSI6ImNpem85dmhwazAy'
            'ajIyd284dGxhN2VxYnYifQ.HQCmyhEXZUTz3S98FMrVAQ'
        )  # 此处的写法只是为了排版，结果为连接在一起的字符串
        # layout = go.Layout(
        #     autosize=True,
        #     mapbox=dict(
        #         accesstoken=mapbox_access_token,
        #         bearing=0,
        #         center=dict(
        #             lat=23.12864583,  # 广州市纬度
        #             lon=113.2648325  # 广州市经度
        #         ),
        #         pitch=0,
        #         zoom=10
        #     ),
        # )
        colors = ('blue', 'green', 'yellow', 'purple', 'orange', 'red', 'violet',
                'navy', 'crimson', 'cyan', 'magenta', 'maroon', 'peru')  # 可按需增加
        null = None  # 将json中的null定义为None
        city_code = 257  # 广州的城市编号
        self.data = []  # 绘制数据
        self.origindata=[]
        marked = set()

        for railway in station_info_json['content']:
            uid = railway['line_uid']
            if uid in marked:  # 由于线路包括了来回两个方向，需要排除已绘制线路的反向线路
                continue

            railway_json = requests.get(
                'https://map.baidu.com/?qt=bsl&tps=&newmap=1&uid=%s&c=%s' % (
                    uid, city_code)
            )
            railway_json.close()
            railway_json = eval(railway_json.content.decode().replace('false','False'))  # 将json字符串转为python对象
            trace_mercator = np.array(
                # 取出线路信息字典，以“|”划分后，取出第三部分信息，去掉末尾的“;”,获取BD-09MC坐标序列
                railway_json['content'][0]['geo'].split('|')[2][: -1].split(','),
                dtype=float
            ).reshape((-1, 2))
            trace_coordinates = self.bd09_to_wgs84(self.mercator_to_bd09(trace_mercator))

            plots = []  # 站台BD-09MC坐标
            plots_name = []  # 站台名称
            for plot in railway['stops']:
                plots.append([plot['x'], plot['y']])
                plots_name.append(plot['name'])
            plot_mercator = np.array(plots)
            plot_coordinates = self.bd09_to_wgs84(self.mercator_to_bd09(plot_mercator))  # 站台经纬度

            color = railway_json['content'][0]['lineColor']  # 利用json所给线路的颜色
            if color == '':
                color = random.choice(colors)
            self.data.extend([
                # 地铁路线
                go.Scattermapbox(
                    lon=trace_coordinates[:, 0],  # 路线点经度
                    lat=trace_coordinates[:, 1],  # 路线点纬度
                    mode='lines',
                    text=railway['line_name'],
                    # 设置路线的参数
                    line=go.scattermapbox.Line(
                        width=1,
                        color=color
                    ),
                    name=railway['line_name'],  # 线路名称，显示在图例（legend）上
                    legendgroup=railway['line_name'],
                    hoverinfo='text'
                    # showlegend=False  # 不显示图例（legend)
                ),
                go.Scattermapbox(
                    lon=plot_coordinates[:, 0],  # 站台经度
                    lat=plot_coordinates[:, 1],  # 站台纬度
                    mode='markers',
                    text=plots_name,
                    hoverinfo='text',
                    # 设置标记点的参数
                    marker=go.scattermapbox.Marker(
                        size=4,
                        color=color
                    ),
                    name=railway['line_name'],  # 线路名称，显示在图例（legend）及鼠标悬浮在标记点时的路线名上
                    # legendgroup=railway['line_name'],  # 设置与路线同组，当隐藏该路线时隐藏标记点
                    showlegend=False  # 不显示图例（legend)
                )
            ])
            self.origindata.extend([
                # 地铁路线
                go.Scattermapbox(
                    lon=trace_coordinates[:, 0],  # 路线点经度
                    lat=trace_coordinates[:, 1],  # 路线点纬度
                    mode='lines',
                    text=railway['line_name'],
                    # 设置路线的参数
                    line=go.scattermapbox.Line(
                        width=2,
                        color=color
                    ),
                    name=railway['line_name'],  # 线路名称，显示在图例（legend）上
                    legendgroup=railway['line_name'],
                    hoverinfo='text'
                    # showlegend=False  # 不显示图例（legend)
                ),
                go.Scattermapbox(
                    lon=plot_coordinates[:, 0],  # 站台经度
                    lat=plot_coordinates[:, 1],  # 站台纬度
                    mode='markers',
                    text=plots_name,
                    hoverinfo='text',
                    # 设置标记点的参数
                    marker=go.scattermapbox.Marker(
                        size=8,
                        color=color
                    ),
                    name=railway['line_name'],  # 线路名称，显示在图例（legend）及鼠标悬浮在标记点时的路线名上
                    # legendgroup=railway['line_name'],  # 设置与路线同组，当隐藏该路线时隐藏标记点
                    showlegend=False  # 不显示图例（legend)
                ),
                go.Scattermapbox(
                    lon=plot_coordinates[:, 0],  # 站台经度
                    lat=[i+0.001 for i in plot_coordinates[:, 1]],  # 站台纬度
                    mode='text',
                    text=plots_name,
                    hoverinfo='skip',
                    # 设置标记点的参数
                    marker=go.scattermapbox.Marker(
                        size=12,
                        color=color
                    ),
                    # 线路名称，显示在图例（legend）及鼠标悬浮在标记点时的路线名上
                    name=railway['line_name'],
                    # legendgroup=railway['line_name'],  # 设置与路线同组，当隐藏该路线时隐藏标记点
                    showlegend=False  # 不显示图例（legend)
                )
                
            ])
            marked.add(uid)  # 添加已绘制线路的uid
            marked.add(railway['pair_line_uid'])  # 添加已绘制线路反向线路的uid



            # marked.add(uid)  # 添加已绘制线路的uid
            # marked.add(railway['pair_line_uid'])  # 添加已绘制线路反向线路的uid
            
    def print(self, path_info_json):
        # station_info_json = self.station_info_json.copy()  # 将json字符串转为python对象

        # path_info_json=loadByjson('kktohs.json')
        
        mapbox_access_token = (
            'pk.eyJ1IjoibHVrYXNtYXJ0aW5lbGxpIiwiYSI6ImNpem85dmhwazAy'
            'ajIyd284dGxhN2VxYnYifQ.HQCmyhEXZUTz3S98FMrVAQ'
        )  # 此处的写法只是为了排版，结果为连接在一起的字符串
        layout = go.Layout(
            autosize=True,
            mapbox=dict(
                accesstoken=mapbox_access_token,
                bearing=0,
                center=dict(
                    lat=23.12864583,  # 广州市纬度
                    lon=113.2648325  # 广州市经度
                ),
                pitch=0,
                zoom=10
            ),
        )
        colors = ('blue', 'green', 'yellow', 'purple', 'orange', 'red', 'violet',
                  'navy', 'crimson', 'cyan', 'magenta', 'maroon', 'peru')  # 可按需增加
        null = None  # 将json中的null定义为None
        city_code = 257  # 广州的城市编号
        data = self.data.copy()  # 绘制数据
        marked = set()

        for railway in path_info_json['content']:
            uid = railway['line_uid']
            if uid in marked:  # 由于线路包括了来回两个方向，需要排除已绘制线路的反向线路
                continue

            railway_json = requests.get(
                'https://map.baidu.com/?qt=bsl&tps=&newmap=1&uid=%s&c=%s' % (
                    uid, city_code)
            )
            railway_json.close()
            railway_json = eval(railway_json.content.decode().replace('false','False'))  # 将json字符串转为python对象
            trace_mercator = np.array(
                # 取出线路信息字典，以“|”划分后，取出第三部分信息，去掉末尾的“;”,获取BD-09MC坐标序列
                railway_json['content'][0]['geo'].split('|')[2][: -1].split(','),
                dtype=float
            ).reshape((-1, 2))
            trace_coordinates = self.bd09_to_wgs84(self.mercator_to_bd09(trace_mercator))

            plots = []  # 站台BD-09MC坐标
            plots_name = []  # 站台名称
            for plot in railway['stops']:
                plots.append([plot['x'], plot['y']])
                plots_name.append(plot['name'])
            plot_mercator = np.array(plots)
            plot_coordinates = self.bd09_to_wgs84(
                self.mercator_to_bd09(plot_mercator))  # 站台经纬度

            color = railway_json['content'][0]['lineColor']  # 利用json所给线路的颜色
            if color == '':
                color = random.choice(colors)
            data.extend([
                # 地铁站台
                go.Scattermapbox(
                    lon=plot_coordinates[:, 0],  # 站台经度
                    lat=plot_coordinates[:, 1],  # 站台纬度
                    mode='markers',
                    text=plots_name,
                    hoverinfo='text',
                    # 设置标记点的参数
                    marker=go.scattermapbox.Marker(
                        size=18,
                        color=color
                    ),
                    # 线路名称，显示在图例（legend）及鼠标悬浮在标记点时的路线名上
                    name=railway['line_name'],
                    # legendgroup=railway['line_name'],  # 设置与路线同组，当隐藏该路线时隐藏标记点
                    # showlegend=False  # 不显示图例（legend)
                ),
                go.Scattermapbox(
                    lon=plot_coordinates[:, 0],  # 站台经度
                    lat=[i+0.001 for i in plot_coordinates[:, 1]],  # 站台纬度
                    mode='text',
                    text=plots_name,
                    hoverinfo='skip',
                    # 设置标记点的参数
                    marker=go.scattermapbox.Marker(
                        size=16,
                        color=color
                    ),
                    # 线路名称，显示在图例（legend）及鼠标悬浮在标记点时的路线名上
                    name=railway['line_name'],
                    # legendgroup=railway['line_name'],  # 设置与路线同组，当隐藏该路线时隐藏标记点
                    showlegend=False  # 不显示图例（legend)
                )
            ])
        self.fig = dict(data=data, layout=layout)
        py.iplot(self.fig) #直接显示地图
    def originprint(self):
        mapbox_access_token = (
            'pk.eyJ1IjoibHVrYXNtYXJ0aW5lbGxpIiwiYSI6ImNpem85dmhwazAy'
            'ajIyd284dGxhN2VxYnYifQ.HQCmyhEXZUTz3S98FMrVAQ'
        )  # 此处的写法只是为了排版，结果为连接在一起的字符串
        layout = go.Layout(
            autosize=True,
            mapbox=dict(
                accesstoken=mapbox_access_token,
                bearing=0,
                center=dict(
                    lat=23.12864583,  # 广州市纬度
                    lon=113.2648325  # 广州市经度
                ),
                pitch=0,
                zoom=10
            ),
        )
        fig = dict(data=self.origindata, layout=layout)
        py.iplot(fig)  # 直接显示地图

    def __init__(self):
        self.prepare()
# map=Map()
# map.prepare()
# with open('kktohs.json', "r") as fs:
#     content = fs.read()
#     station_info_json = json.loads(content)
#     map.print(station_info_json)
#     input('origin')
#     map.originprint()
