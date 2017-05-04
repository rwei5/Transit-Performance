# Transit Performance Specification

## Introduction


* fileHandler.py is for handling the input shapefiles(Bus stops shapefile, bus routes shapefile and census block groups shapefile).
* GTFSReader.py is for reading the GTFS file to get stop-route relationship.
* fileWriter.py is for outputing the result in shapefile and excel format.
* cal_equality.py is for handling the main calculation of routes optimation.
* DEA.py is for calculating the coefficiency of each bus line.
* DEAadapter.py is for parsing the input data and providing the parameters to DEA.py.
* model_overlay.py is for generating the LP file to calculate final results.
* cal_glpk.py is for calculating the optimization results.
* cal_rank.py is for generating the results according to the remaining bus lines, operational efficiency weight and equality weight.
* geoRender.py is for dispalying the map view of bus lines and block groups.
* launchBusAnalysis.py is for launch a GUI part.

## How to run the project
Refer to:

[Bus Line Analysis User Manual.docx](https://github.com/rwei5/Transit-Performance/blob/master/doc/Bus%20Line%20Analysis%20User%20Manual.docx) 

under https://github.com/rwei5/Transit-Performance/tree/master/doc

## Code

### fileHandler.py

You can read bus stops, bus routes and blocks shp file using FileReader class.

```
from FileHandler.py import *

fr = FileReader(bus_stop_fileName, blocks_fileName, bus_routes_fileName)
fr.initData()
```
After that, you can get shape record for stops:

```
fr.getBusStopsRecords()
```

**Input:**

The path of bus stops shapefile.

**Default input:**

"../input/BusStops_UTA/BusStops_UTA.shp"

**Output format:**

The shape of bus stops:

```
>>> [[418225.4299999997, 4548914.01]]
```

routes:

```
fr.getBusRoutesRecords()
```

**Input:**

The path of bus routes shapefile.

**Default input:**

"../input/BusRoutes_UTA/BusRoutes_UTA.shp"

**Output format:**

The shape of bus routes:

```
>>> [[428090.04000000004, 4513247.08], [428064.7599999998, 4513251.77], [428127.13999999966, 4513243.390000001], [428090.04000000004, 4513247.08]]
```

and census block groups:

```
fr.getBlocksRecords()
```
**Input:**

The path of census block groups shapefile.

**Default input:**

"../input/Utah_blck_grp/UT_blck_grp_2010.shp"

**Output format:**

The shape of census block groups:

```
>>> [[414635.3136134944, 4602173.985223745], [414638.14761937386, 4602166.84518638], [414646.40352641, 4602145.761064672], [414649.1554964636, 4602138.733025542], [414667.0483180287, 4602128.638523131]]
```

Also, you can get record details (map format) for stops:

```
fr.busStopsRecordDicts
```

**Input:**

The path of bus stops shapefile.

**Default input:**

"../input/BusStops_UTA/BusStops_UTA.shp"

**Output format:**

The information from bus stops shapefile:

```
>>> {'OnStreet': 'N HILL FIELD RD', 'Transfer': 1, 'Garbage': 0, 'AtStreet': 'ANTELOPE DR', 'Lighting': 0, 'Bicycle': 0, 'InService': 1, 'LocationUs': 'Bus Stop', 'StreetNum': '1.89100000000e+003', 'Bench': 0, 'StopId': '1.38400000000e+004', 'UTAStopID': '101001', 'StopName': 'HILL FIELD RD @ 1891 N', 'City': 'LAYTON', 'Shelter': 0}
```

routes:

```
fr.busRoutesRecordDicts
```

**Input:**

The path of bus routes shapefile.

**Default input:**

"../input/BusRoutes_UTA/BusRoutes_UTA.shp"

**Output format:**

The information from bus routes shapefile:

```
>>> {'Service': 'local', 'Frequency': '15', 'Shape_Leng': '8.77020330753e+003', 'LineAbbr': '2', 'LineName': '200 SOUTH'}
```

and blocks:

```
fr.blocksRecordDicts
```

**Input:**

The path of census block groups shapefile.

**Default input:**

"../input/Utah_blck_grp/UT_blck_grp_2010.shp"

**Output format:**

The information from census block groups shapefile:

```
>>> {'GEOID10': '490039605001', 'Race': 49, 'NAMELSAD10': 'Block Group 1', 'Age': 681, 'MTFCC10': 'G5030', 'Shape_Area': '1.42063209219e+007', 'FUNCSTAT10': 'S', 'Shape_Leng': '2.40437000631e+004', 'Transporta': 35, 'Unemploy': 38, 'Poverty': 11, 'Disability': 92}
```





```
excelWritableCreate(tablename):
```
**description**
Create writable excel file with table

**input**
tablename		 table name

**output**
File handler and table

```
excelWritableSave(file, filename)
```
**description**
Save excel file with name

**input **
file	 		       File handler
filename	       File name

**output **
N/A

```
excelWritableCell(table, row, col, value)
```
**description **
Write cell to excel file

**input **
table       Current table
row         Current row
col         Current col
value       Value to write

**output **
N/A

```
openRegularFile(filename)
```
**description **
Open regular file

**input **
filename      Input file name
**output **
File handler

```
closeRegularFile(fd)
```
**description **
Close regular file

**input **
fd             File handlers

**output **
N/A

```
writeRegularFile(fd, str)
```
**description **
Write regular file

**input **
fd             File handler
str            The string will be written to the file

```
parseInputFile(filename, sheet_id = 0)
```
**description **
Parse the input file. This function will call different internal functions according to the extend name of the input file.

**input **
filename       Input file name
sheed_id       Excel sheet NO.

**output **
File data


### GTFSReader.py

We can't know which stops belong to which route for just using shp files, so we need to use GTFS file to get the information about that.

the way to get the information:

```
from GTFSReader import *

GTFSinfo = GTFSReader(stops_fileName, stops_times_fileName, trips_fileName)
GTFSinfo.mapStopsToRoute()
```

**Input:**:

GTFS routes file, GTFS stop times file and GTFS trips file.

**Default input:**

GTFS stops file : "../input/routes.txt"

GTFS stop times file : "../input/stop_times.txt"

GTFS trips file : "../input/trips.txt"

**Output format:**

You will get to know which stops belong to which route.

```
>>> {'64016': [18768, 13731, 13733, 13734], '64184': [23623, 20408, 4895, 18684, 20409, 13207, 4898, 13941], '64191': [22184, 23793, 23828, 17441, 17442]}
```
### fileWriter.py

This file is for outputing the result in shapefile(shp) format and excel format.


#####write_to_file_dict(polys, resultMap)

The method writes the bus routes coverage result calculated using intersection method as polygons in shapefile.

```
from fileWriter import *

fw = fileWriter()
fw.write_to_file_dict_centroid(polys, resultMap)

```

**Input**:

The method takes two arguments:

* **polys** is a list of polygons.

```
[[444543.0285057391, 4451446.881305269], [444522.8478449208, 4451413.211906792], [444499.4641813449, 4451381.6826863345], [444473.1027124744, 4451352.5972875245], [444444.01731366524, 4451326.235818654], [444412.4880932076, 4451302.852155078], [444378.8186947302, 4451282.67149426], [444343.33337294584, 4451265.888186995], [444327.3015140701, 4451260.151896166]]

```
* **resultMap** is the bus routes coverage result.

```
'64186': {'Poverty': 622, 'Disability': 651, 'Transporta': 622, 'Age': 7607, 'Race': 1887, 'Unemploy': 361}

```
**Ouput**:

shapefile, default file name is 'shapefiles/test/polygonLines_normal'


#####write_to_file_dict_centroid(polys, resultMap)

The method writes the bus routes coverage result calculated using centroid method as polylines in shapefile.

```
from fileWriter import *

fw = fileWriter()
fw.write_to_file_dict_centroid(polys, resultMap)

```

**Input**:

The method takes two arguments:

* **polys** is a list of polygons.

```
[[444543.0285057391, 4451446.881305269], [444522.8478449208, 4451413.211906792], [444499.4641813449, 4451381.6826863345], [444473.1027124744, 4451352.5972875245], [444444.01731366524, 4451326.235818654], [444412.4880932076, 4451302.852155078], [444378.8186947302, 4451282.67149426], [444343.33337294584, 4451265.888186995], [444327.3015140701, 4451260.151896166]]

```
* **resultMap** is the bus routes coverage result.

```
'64061':{'PovertyCentroid':426, 'DisabilityCentroid':554, 'TransportaCentroid':318, 'AgeCentroid':	478, 'RaceCentroid':237, 'UnemployCentroid':184}

```

**Ouput**:

shapefile, default file name is 'shapefiles/test/polygonLines_Centroid'

### cal_equality.py

#### Package:

* rtree

Rtree is a ctypes Python wrapper of libspatialindex that provides a number of advanced spatial indexing features for the spatially curious Python user.

Install Tutorial:

<http://toblerity.org/rtree/install.html#nix>

* shapefile

The Python Shapefile Library (pyshp). 

Install Tutorial:

<https://pypi.python.org/pypi/pyshp>

* shapely

Shapely is a BSD-licensed Python package for manipulation and analysis of planar geometric objects.

Install Tutorial:

<https://pypi.python.org/pypi/Shapely/>

#### Methods:


#####calculate(population\_field\_name, method_name)

**Input:**

Population field name:

User can input the population field name on the interface.

Method name:

There are two methods can be chose from,

"overlap": will call linesOverLap() method.

"centroid": will call calDisbycentroiddistance() method.

**Output:**

For "overlap" method:

PieceId: {'sum': Disadvantaged population, 'lines': a list of routes short names shows which routes the piece belongs to}

```
>>> 1770: {'sum': 154.0, 'lines': ['205', '200']}, 1771: {'sum': 48.0, 'lines': ['902']}

```

For "centroid" method:

Route short name: {'sum': Disadvantaged population, 'blocks': a list of block ids shows which blocks the route serves 'lines': its route short name}
```
'477': {'blocks': [1619, 1420, 1421, 1419, 1455], 'sum': 3917.0, 'lines': ['477']}
```

#####linesOverLap()

This method calculates how many disadvantaged population in each overlap pieces of bus routes coverage and which routes these pieces belong to by following steps:

First create a buffer area of bus stops (default: 400 meters), and then union all the buffer areas of bus stops belonging to one bus route. This is considered to be the service area of each bus route. Then use all these service area to intersects with each other, after that, make each small parts as independent service area pieces, Finally we use the service area piece which is overlaid with the census block groups to calculate the disadvantaged population served by each small service area piece. 



```
ce = CalEquality()
ce.linesOverLap()

```
**Input:**

The path of Bus stops shapefile, bus routes shapefile, census block groups shapefile, GTFS stops file, GTFS stop times file and GTFS trips file.

**Default Input:**

GTFS stops file : "../input/stops.txt"

GTFS stop times file : "../input/stop_times.txt"

GTFS trips file : "../input/trips.txt"

bus stops shapefile : "../input/BusStops_UTA/BusStops_UTA.shp"

census block groups shapefile : "../input/Utah_blck_grp/UT_blck_grp_2010.shp"

bus routes shapefile : "../input/BusRoutes_UTA/BusRoutes_UTA.shp"

**Output format:**

PieceId: {'sum': Disadvantaged population, 'lines': a list of routes short names shows which routes the piece belongs to}

```
>>> 1770: {'sum': 154.0, 'lines': ['205', '200']}, 1771: {'sum': 48.0, 'lines': ['902']}

```

#####linesOverLap_shp()

This method calculates how many disadvantaged population in each overlap pieces of bus routes coverage and which routes these pieces belong to by following steps:

First create a buffer area of bus stops (default: 400 meters), and then union all the buffer areas of bus stops belonging to one bus route. This is considered to be the service area of each bus route. Then use all these service area to intersects with each other, after that, make each small parts as independent service area pieces, Finally we use the service area piece which is overlaid with the census block groups to calculate the disadvantaged population served by each small service area piece. 

Then output it as shapefile.

```
ce = CalEquality()
ce.linesOverLap_shp()

```
**Input:**

The path of Bus stops shapefile, bus routes shapefile, census block groups shapefile, GTFS stops file, GTFS stop times file and GTFS trips file.

**Default Input:**

GTFS stops file : "../input/stops.txt"

GTFS stop times file : "../input/stop_times.txt"

GTFS trips file : "../input/trips.txt"

bus stops shapefile : "../input/BusStops_UTA/BusStops_UTA.shp"

census block groups shapefile : "../input/Utah_blck_grp/UT_blck_grp_2010.shp"

bus routes shapefile : "../input/BusRoutes_UTA/BusRoutes_UTA.shp"

**Output format**:

Shapefile.

**Default output file**: 

'shapefiles/test/polygonPieces'

#####calUnion()

This method calculate how many disadvantaged in each bus routes coverage by following steps:

First create a buffer area of bus stops (default: 400 meters), and then union all the buffer areas of bus stops belonging to one bus route. This is considered to be the service area of each bus route. Finally we use the service area piece which is overlaid with the census block groups to calculate the disadvantaged population served by each bus route.

```
ce = CalEquality()
ce.calUnion()

```

**Input:**

The path of Bus stops shapefile, bus routes shapefile, census block groups shapefile, GTFS stops file, GTFS stop times file and GTFS trips file.

**Default Input:**

GTFS stops file : "../input/stops.txt"

GTFS stop times file : "../input/stop_times.txt"

GTFS trips file : "../input/trips.txt"

bus stops shapefile : "../input/BusStops_UTA/BusStops_UTA.shp"

census block groups shapefile : "../input/Utah_blck_grp/UT_blck_grp_2010.shp"

bus routes shapefile : "../input/BusRoutes_UTA/BusRoutes_UTA.shp"

**Output format**:

Bus route id: {'Poverty': the number of poverty people, 'Disability': the number of poverty people, 'Transporta': the number of transporta people, 'Age': the number of aged people, 'Race': the number of race people, 'Unemploy': the number of unemploy people}


```
>>>'64186': {'Poverty': 622, 'Disability': 651, 'Transporta': 622, 'Age': 7607, 'Race': 1887, 'Unemploy': 361}
```

#####calUnion_shp()

This method calculate how many disadvantaged in each bus routes coverage by following steps:

First create a buffer area of bus stops (default: 400 meters), and then union all the buffer areas of bus stops belonging to one bus route. This is considered to be the service area of each bus route. Finally the service area is overlaid with the census block groups to calculate the disadvantaged population served by each bus route.

Then output it as shapefile.

```
ce = CalEquality()
ce.calUnion_shp()

```

**Input:**

The path of Bus stops shapefile, bus routes shapefile, census block groups shapefile, GTFS stops file, GTFS stop times file and GTFS trips file.

**Default Input:**

GTFS stops file : "../input/stops.txt"

GTFS stop times file : "../input/stop_times.txt"

GTFS trips file : "../input/trips.txt"

bus stops shapefile : "../input/BusStops_UTA/BusStops_UTA.shp"

census block groups shapefile : "../input/Utah_blck_grp/UT_blck_grp_2010.shp"

bus routes shapefile : "../input/BusRoutes_UTA/BusRoutes_UTA.shp"

**Output format**:

A Shapefile contains each bus routes(lines) polygons with ids and disadvantaged population details.

**Default output file**: 

'shapefiles/test/polygonLines_normal'


#####calDisByCentroidDistance()

This method calculate how many disadvantaged people in each bus routes using centroid method ( Calculate the distance between bus stop and centroid, if the distance less than a threshold value, those bus stops sever all the disadvantaged population in this block.)

```
ce = CalEquality()
ce.calDisByCentroidDistance()

```

**Input:**

The path of Bus stops shapefile, bus routes shapefile, census block groups shapefile, GTFS stops file, GTFS stop times file and GTFS trips file.

**Default Input:**

GTFS stops file : "../input/stops.txt"

GTFS stop times file : "../input/stop_times.txt"

GTFS trips file : "../input/trips.txt"

bus stops shapefile : "../input/BusStops_UTA/BusStops_UTA.shp"

census block groups shapefile : "../input/Utah_blck_grp/UT_blck_grp_2010.shp"

bus routes shapefile : "../input/BusRoutes_UTA/BusRoutes_UTA.shp"

**Output format**:

Bus route id: {'Poverty': the number of poverty people, 'Disability': the number of poverty people, 'Transporta': the number of transporta people, 'Age': the number of aged people, 'Race': the number of race people, 'Unemploy': the number of unemploy people}

```
>>>'64061':	{'PovertyCentroid':426, 'DisabilityCentroid':554, 'TransportaCentroid':318, 'AgeCentroid':	478, 'RaceCentroid':237, 'UnemployCentroid':184}
```

#####calDisByCentroidDistance_shp()

This method calculate how many disadvantaged people in each bus routes using centroid method and output it as shapefile.

```
ce = CalEquality()
ce.calDisByCentroidDistance_shp()

```
**Input:**

The path of Bus stops shapefile, bus routes shapefile, census block groups shapefile, GTFS stops file, GTFS stop times file and GTFS trips file.

**Default Input:**

GTFS route file : "../input/route.txt"

GTFS stop times file : "../input/stop_times.txt"

GTFS trips file : "../input/trips.txt"

bus stops shapefile : "../input/BusStops_UTA/BusStops_UTA.shp"

census block groups shapefile : "../input/Utah_blck_grp/UT_blck_grp_2010.shp"

bus routes shapefile : "../input/BusRoutes_UTA/BusRoutes_UTA.shp"

**Output format**:

A Shapefile contains each bus routes(lines) polylines with ids and disadvantaged population details.

**Default output file**: 

'shapefiles/test/polygonLines_Centroid'


#####compareDiffWays()

This method calculate how many disadvantaged population each bus routes(lines) cover using two methods and output it as excel file:

1. Create a buffer area of bus stops (default: 400 meters), and then union all the buffer areas of bus stops belonging to one bus route. This is considered to be the service area of each bus route. Finally the service area is overlaid with the census block groups to calculate the disadvantaged population served by each bus route.

2. Calculate the distance between bus stops and city blocks centroid, if the distance less than a threshold value, we see those bus stops can cover all the disadvantaged population in this block.

```
ce = CalEquality()
ce.compareDiffWays()
```

**Input:**

The path of Bus stops shapefile, bus routes shapefile, census block groups shapefile, GTFS stops file, GTFS stop times file and GTFS trips file.

**Default Input:**

GTFS stops file : "../input/stops.txt"

GTFS stop times file : "../input/stop_times.txt"

GTFS trips file : "../input/trips.txt"

bus stops shapefile : "../input/BusStops_UTA/BusStops_UTA.shp"

census block groups shapefile : "../input/Utah_blck_grp/UT_blck_grp_2010.shp"

bus routes shapefile : "../input/BusRoutes_UTA/BusRoutes_UTA.shp"

**Output format**:


| id    | Age  | AgeCentroid | AgeDiff |
| ----- | ---- | ----------- | ------- |
| 64061 | 304  | 426         | -122    |


**Default output file**: 

'resultDiff'

### DEA.py
**reference code**
https://github.com/metjush/envelopment-py

#### package
numpy
scipy

```
class DEA(object)
```
**description**
Data envelopment analysis core

```
__init__(self, inputs, outputs)
```
**description**
Constructor, init DEA class variables

**input**
input          The coefficients of the formular, n x m array
output         The value of the formular, n x r array

**output**
N/A

```
__efficiency(self, unit)
```
**description**
The efficiency function with already computed weights

**input**
unit           The number of entities

**output**
Efficiency

```
__target(self, x, unit)
```
**description**
Calculate theta

**input**
unit           The number of entities
x              Combined weights

**output**
Theta

```
__constraints(self, x, unit)
```
**description**
Constraints for optimization for one unit

**input**
unit           The number of entities
x              Combined weights

** output **
Array of constraints

```
__optimize(self)
```
**description**
Optimization of DEA model
Use: http://docs.scipy.org/doc/scipy0.17.0/reference/generated/scipy.optimize.linprog.html
A = coefficients in the constraints
b = rhs of constraints
c = coefficients of the target function

```
name_units(self, names)
```
**description**
Get names

**input**
name           The name list

**output**
N/A

```
fit(self)
```
**description**
Optimize dataset, generate the table

**input**
N/A

**output**
Generated table, e.g
"990": 0.0461, "516": 0.4766, "313": 0.2049, "513": 0.2873

```
getResult(self)
```
**description**
Call fit() to get the optimize dataset, generate the table

**input**
N/A

**output**
The same as the output of fit.

### DEAadapter.py
#### Package
numpy
xlrd
time
datetime
os, platform
json

#### input file:
inputExcel = "../input/DEA_input_dataset.xlsx"

#### output file
outputFile = "cal_dea.json"
outputCSV = "dea_csv.csv"
outputExcel = "dea_excel.xls"

```
parse(_excelfile, _head_busline_str, _head_input_set, _head_output_set)
```
**description**
Calculate the bus line. This is the actually interface to provide the parameters to DEA core.

**input**

_excelfile: the input excel file

_head_busline_str: the field name of bus line

_head_input_set: the field names of input for linear programming

_head_output_set: the field name of output for linear programming

**output**
Bus name, input, output

```
calDEA(_excelfile, _output_path, _head_busline_str, _head_input_set, _head_output_set)
```
**description**
Calculate the coefficiency. 

**intput**

_excelfile: the input excel file

_output_path: the folder to store the output file

_head_busline_str: the field name of bus line

_head_input_set: the field names of input for linear programming

_head_output_set: the field name of output for linear programming

**output**
Dict: dict[bus line] -> coefficiency, e.g
"990": 0.0461, "516": 0.4766, "313": 0.2049, "513": 0.2873


### model_overlay.py
#### Package
numpy
sys
os, platform
json

#### input file
inputCal = "../output/cal_equality.json"
inputDEA = "../output/cal_dea.json"

#### output file
output =                    "model_overlay.lp"

#### output format
Standard LP file, e.g. (http://www.gurobi.com/documentation/6.5/refman/lp_format.html)
```
Maximize
  x + y + z
Subject To
  c0: x + y = 1
  c1: x + 5 y + 2 z <= 10
  qc0: x + y + [ x ^ 2 - 2 x * y + 3 y ^ 2 ] <= 5
Bounds
  0 <= x <= 5
  z >= 2
Generals
  x y z
End
```

### cal_glpk.py
#### Package
os, platform, sys
time
json

#### input file
inputLpFile = "model_overlay.lp"
inputCal = "../output/cal_equality.json"
inputDea = "../output/cal_dea.json"

#### output file
outputRet = "glpk_result"
outputExcel = "glpk_excel"

### cal_rank.py
#### Package
os, platform, sys
json

#### input file
inputCal = "../output/cal_equality.json"
inputDea = "../output/cal_dea.json"

#### output file
outputExcel = "rank_excel"

### geoRender.py
#### Package
osgeo
numpy
matplotlib
sys

#### input file
block shape file
bus routes shape file

#### output file
N/A

### launchBusAnalysis.py
#### Package
Tkinter
ttk
tkMessageBox
osgeo
os, platform, sys
thread
json
xlrd

#### input file
N/A

#### output file
N/A
