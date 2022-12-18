from pywebio.input import *
from pywebio.output import *
from Planing.Map import Map
from Planing.Plan import Plan
def stationchoose():
    remove("result")
    with use_scope("choose", clear=True):
        put_button('Origin Tube Map', onclick=lambda: map.originprint())
        station = input_group("Select a location", [
            input('Starting', datalist=stations, name='start',required=True),
            input('Destination', datalist=stations, name='end', required=True),
            # select('Starting', options=stations, name='start'),
            # select('Destination', options=stations, name='end'),
        ])
    result(station)


def result(station):
    
    scroll_to("result", position='top')
    scroll_to("plan", position='top')
    with use_scope("result", clear=True):
        put_row([
            put_button(' From ', disabled=True, onclick=lambda:None),
            put_text(station['start']),
            put_button(' To ', disabled=True, onclick=lambda:None),
            put_text(station['end']),
            put_button('Reset', onclick=lambda: stationchoose())
        ], size='auto')
        put_collapse('Shortest actual distance', put_scope("distance"),open=True)
        put_collapse('Least number of station', put_scope("station"),open=True)
        put_collapse('Least number of transit station', put_scope("line"),open=True)
    
    with use_scope("distance"):
        plan.setweight('distance')
        path, dis = plan.getpath(station['start'], station['end'])
        display = [[path[0]]]
        for i in range(1, len(path)):
            if(path[i]['line_name'] == path[i-1]['line_name']):
                display[-1].append(path[i])
            else:
                display.append([path[i]])
        put_row([
            put_table([[dis/1000]], header=['Total actual distance (km)']),
            put_button(' Show map by distance ', onclick=lambda:map.print(plan.getpathinfo('distance',station['start'], station['end'])))
        ])
        id = 1
        for subpath in display:
            put_text(subpath[0]['line_name']),
            put_table([[i['station'] for i in subpath]], header=[
                      i for i in range(id, len(subpath)+id)])
            id += len(subpath)-1
    with use_scope("station"):
        plan.setweight('station')
        path, dis = plan.getpath(station['start'], station['end'])
        display = [[path[0]]]
        for i in range(1, len(path)):
            if(path[i]['line_name'] == path[i-1]['line_name']):
                display[-1].append(path[i])
            else:
                display.append([path[i]])
        put_row([
            put_table([[dis+1]], header=['Total station']),
            put_button(' Show map by station ',onclick=lambda:map.print(plan.getpathinfo('station',station['start'], station['end'])))
        ])
        id = 1
        for subpath in display:
            put_text(subpath[0]['line_name']),
            put_table([[i['station'] for i in subpath]], header=[
                      i for i in range(id, len(subpath)+id)])
            id += len(subpath)-1
    with use_scope("line"):
        plan.setweight('line')
        path, dis = plan.getpath(station['start'], station['end'])
        display = [[path[0]]]
        for i in range(1, len(path)):
            if(path[i]['line_name'] == path[i-1]['line_name']):
                display[-1].append(path[i])
            else:
                display.append([path[i]])
        put_row([
            put_table([[dis-1]], header=['Total transit stations']),
            put_button(' Show map by transit stations ',onclick=lambda:map.print(plan.getpathinfo('line',station['start'], station['end'])))
        ])
        id = 1
        for subpath in display:
            put_text(subpath[0]['line_name']),
            put_table([[i['station'] for i in subpath]], header=[
                      i for i in range(id, len(subpath)+id)])
            id += len(subpath)-1

def loop():
    stationchoose()

if __name__ == '__main__':
    plan=Plan()
    map=Map()
    stations = plan.getstations()
    loop()