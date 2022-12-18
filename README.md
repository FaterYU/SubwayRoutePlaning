# SubwayRoutePlaning

A road map of Guangzhou metro is given, and visitors can query  metro information through the terminal. The system can provide the shortest route  calculation and recommendation function

## Fast start

Install python requirements

```shell
pip install ./requirements.txt
```

Start system (**need close the System Proxy**)

```shell
python3 ./control.py
```

## File stucture

```text
SubwayRoutePlaning
│  content.json
│  control.py
│  Guangzhou_railway.html
│  README.md
│  Report.md
│  Report.pdf
│  requirements.txt
│
├─img
│      distancemap.png
│      distancemsg.jpg
│      end.jpg
│      home.jpg
│      linemap.png
│      linemsg.jpg
│      list.jpg
│      listmsg.jpg
│      PartGZGraph.png
│      start.jpg
│      stationmap.png
│      stationmsg.jpg
│
└─Planing
    │  Map.py
    │  Plan.py
    │  __init__.py
    │
    └─__pycache__
```