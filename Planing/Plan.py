import heapq
import numpy as np
import requests
import time
import json
from collections import defaultdict
import matplotlib.pyplot as plt
import queue
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
                    station_list[line['stops'][station_id]['name']][line['stops'][station_id+1]['name']] = {'distance': distance, 'line_name':line['line_name'],'line_uid':line['line_uid'],'pair_line_uid':line['pair_line_uid']}
        return station_list

    def weightBystation(self):
        station_info_json = self.station_info
        station_list={}
        for line in station_info_json['content']:
            for station_id in range(len(line['stops'])):
                if line['stops'][station_id]['name'] not in station_list:
                    station_list[line['stops'][station_id]['name']] = {}
                if station_id != len(line['stops'])-1:
                    station_list[line['stops'][station_id]['name']][line['stops'][station_id+1]['name']] = {'distance': 1, 'line_name':line['line_name'],'line_uid':line['line_uid'],'pair_line_uid':line['pair_line_uid']}
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
                    station_list[line['stops'][station_id]['name']][line['stops'][station_id+1]['name']] = {'distance': istranslate, 'line_name':line['line_name'],'line_uid':line['line_uid'],'pair_line_uid':line['pair_line_uid']}
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

    def planByweight(self,start,end):
        dis,path=self.dijkstra(self.station_list, start)
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
            # self.station_list = self.weightByline()
            pass
        else:
            self.station_list = self.weightBydistance()
    
    def __init__(self,weight='distance',load_way='internet'):
        self.weight=weight
        self.load_way=load_way
        self.setParams()
    
    def getpath(self,start,end):
        if(self.weight=='line'):
            self.planByline(start,end)
        else:
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
    
    def planByline(self,start,end):
        translate=self.gettranslatestation()
        q=queue.Queue()
        path={}
        station={}
        marked=set()
        for i in self.station_list[start]:
            if(self.station_list[start][i]['line_uid'] in marked):
                continue
            marked.add(self.station_list[start][i]['line_uid'])
            marked.add(self.station_list[start][i]['pair_line_uid'])
            q.put(self.station_list[start][i]['line_name'])
        while(not q.empty()):
            line_name=q.get()
            for i in self.station_info['content']:
                if(line_name == i['line_name']):
                    finded=0
                    for j in i['stops']:
                        if(j['name']==end):
                            finded=1
                            break
                        if(j['name'] in translate):
                            for k in self.station_list[j['name']]:
                                if(self.station_list[j['name']][k]['line_uid'] not in marked):
                                    q.put(self.station_list[j['name']][k]['line_name'])
                                    marked.add(self.station_list[j['name']][k]['line_uid'])
                                    marked.add(self.station_list[j['name']][k]['pair_line_uid'])
                                    path[self.station_list[j['name']][k]['line_name']]=line_name
                                    station[self.station_list[j['name']][k]['line_name']]=j['name']
                    
                    if(finded):
                        result=[{'line_name':line_name,'station':end}]
                        while(line_name in path):
                            result.append({'line_name':path[line_name],'station':station[line_name]})
                            line_name = path[line_name]
                        result.reverse()
                        return self.out_result(result,start,end)
    
    def out_result(self,result,start,end):
        q=[]
        for translate in result:
            start_id=0
            end_id=0
            line_info=self.station_info['content'][[i['line_name'] for i in self.station_info['content']].index(translate['line_name'])]
            for station in range(len(line_info['stops'])):
                if(start==line_info['stops'][station]['name']):
                    start_id=station
                if(translate['station'] == line_info['stops'][station]['name']):
                    end_id=station
            step=int((end_id-start_id)/abs(end_id-start_id))
            for station in range(start_id,end_id+step,step):
                q.append({'station': line_info['stops'][station]['name'], 'line_name': translate['line_name']})
            start=translate['station']
        self.dis=len(result)
        self.path=q
                            
                            

# if __name__ == '__main__':
#     start='长寿路'
#     end='钟村'
#     plan=Plan()
#     result=plan.planByline(start,end)
#     print(result)
