import heapq
import numpy as np
import requests
import time
import json
from collections import defaultdict
import matplotlib.pyplot as plt

class Plan:
    def loadByinternet(self):
        null = None
        city_code = 257
        station_info = requests.get('http://map.baidu.com/?qt=bsi&c=%s&t=%s' % (
            city_code,
            int(time.time() * 1000)
        )
        )
        station_info_json = eval(station_info.content)
        return station_info_json


    def loadByjson(self,filename="content.json"):
        with open(filename, "r") as fs:
            content = fs.read()
        station_info_json = json.loads(content)
        return station_info_json

    def save2json(self,filename="content.json"):
        content = json.dumps(self.station_info)
        with open(filename, "w") as fs:
            fs.write(content)

    def gettranslatestation(self):
        station_info_json = self.station_info
        lines = {}
        for line in station_info_json['content']:
            for station in line['stops']:
                if station['name'] not in lines:
                    lines[station['name']] = []
                lines[station['name']].append(line['line_name'])
        translate_station = []
        for i in lines:
            if len(lines[i]) > 2:
                translate_station.append(i)
        return translate_station

    def weightBydistance(self):
        station_info_json = self.station_info
        station_list={}
        for line in station_info_json['content']:
            for station_id in range(len(line['stops'])):
                if line['stops'][station_id]['name'] not in station_list:
                    station_list[line['stops'][station_id]['name']] = {}
                if station_id != len(line['stops'])-1:
                    x1 = line['stops'][station_id]['x']
                    x2 = line['stops'][station_id+1]['x']
                    y1 = line['stops'][station_id]['y']
                    y2 = line['stops'][station_id+1]['y']
                    distance = ((x1-x2)**2+(y1-y2)**2)**0.5
                    station_list[line['stops'][station_id]['name']][line['stops'][station_id+1]['name']] = {'distance': distance, 'line_name':line['line_name']}
        return station_list

    def weightBystation(self):
        station_info_json = self.station_info
        station_list={}
        for line in station_info_json['content']:
            for station_id in range(len(line['stops'])):
                if line['stops'][station_id]['name'] not in station_list:
                    station_list[line['stops'][station_id]['name']] = {}
                if station_id != len(line['stops'])-1:
                    station_list[line['stops'][station_id]['name']][line['stops'][station_id+1]['name']] = {'distance': 1, 'line_name':line['line_name']}
        return station_list

    def weightByline(self):
        station_info_json = self.station_info
        station_list={}
        for line in station_info_json['content']:
            for station_id in range(len(line['stops'])):
                if line['stops'][station_id]['name'] not in station_list:
                    station_list[line['stops'][station_id]['name']] = {}
                if station_id != len(line['stops'])-1:
                    istranslate = 1 if line['stops'][station_id+1]['name'] in self.gettranslatestation() else 0
                    station_list[line['stops'][station_id]['name']][line['stops'][station_id+1]['name']] = {'distance': istranslate, 'line_name':line['line_name']}
        return station_list

    def dijkstra(self,e,s):
        dis = defaultdict(lambda:float("inf"))
        dis[s] = 0
        q = [(0,s)]
        vis = set()
        path={}
        while q:
            _, u = heapq.heappop(q)
            if u in vis: continue
            vis.add(u)
            for v in e[u]:
                w=e[u][v]['distance']
                if dis[v] > dis[u] + w:
                    dis[v] = dis[u] + w
                    path[v] = {'station': u, 'line_name': e[u][v]['line_name']}
                    heapq.heappush(q,(dis[v],v))
        return dis,path


    # start = '新城东'
    # end = '东风'
    def planByweight(self,start,end):
        dis,path=self.dijkstra(self.station_list, start)
        # print(path)
        q=[]
        q.append(path[end])
        while q[-1]['station']!=start:
            if(path[q[-1]['station']]['line_name']==q[-1]['line_name']):
                q.append(path[q[-1]['station']])
            else:
                q.append({'station':q[-1]['station'],'line_name':path[q[-1]['station']]['line_name']})
                q.append(path[q[-2]['station']])

        q.reverse()
        q.append({'station':end,'line_name':q[-1]['line_name']})
        # print(q)
        # print(dis[end])
        self.path=q
        self.dis=dis[end]

    def path2info(self):
        change_station_info={'content':{}}
        for station in self.path:
            a=0
            for i in self.station_info['content']:
                if(i['line_name'] == station['line_name']):
                    break
                a+=1
            b=0
            if(station['line_name'] not in change_station_info['content']):
                change_station_info['content'][station['line_name']]=self.station_info['content'][a].copy()
                change_station_info['content'][station['line_name']]['stops']=[]
            for i in self.station_info['content'][a]['stops']:
                if(i['name']==station['station']):
                    break
                b+=1
            change_station_info['content'][station['line_name']]['stops'].append(self.station_info['content'][a]['stops'][b])

        second_station_info = {'content':[]}
        for i in change_station_info['content']:
            second_station_info['content'].append(change_station_info['content'][i])
        # print(second_station_info)
        # save2json(second_station_info, 'kktohs.json')
        return second_station_info

    def setParams(self):
        if(self.load_way=='internet'):
            try:
                self.station_info=self.loadByinternet()
                self.save2json()
            except:
                self.station_info=self.loadByjson()
        else:
            self.station_info=self.loadByjson()
        if(self.weight=='station'):
            self.station_list=self.weightBystation()
        elif(self.weight=='line'):
            self.station_list=self.weightByline()
        else:
            self.station_list = self.weightBydistance()
    
    def setweight(self,weight):
        self.weight=weight
        if(self.weight == 'station'):
            self.station_list = self.weightBystation()
        elif(self.weight == 'line'):
            self.station_list = self.weightByline()
        else:
            self.station_list = self.weightBydistance()
    
    def __init__(self,weight='distance',load_way='internet'):
        self.weight=weight
        self.load_way=load_way
        self.setParams()
    
    def getpath(self,start,end):
        self.planByweight(start,end)
        return self.path,self.dis

    def getpathinfo(self,weight,start,end):
        self.setweight(weight)
        self.planByweight(start,end)
        return self.path2info()
    
    def getstations(self):
        result=[]
        for i in self.station_list:
            result.append(i)
        return result

if __name__ == '__main__':
    start='黄沙'
    end='万胜围'
    plan=Plan()
    path,dis=plan.getpath(start,end)
    # print(path)
    # print(plan.station_info)
    info=plan.getpathinfo()
    # print(info)
    print(plan.getstations())
