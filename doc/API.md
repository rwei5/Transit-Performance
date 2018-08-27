# Transit Performance API

### cal_equality.py

#### Methods:
```
CalEquality(self, _rf, _stf, _tf, _bus_stops, _block, _bus_routes,
stop_id, route_id)
```
__Description__

This class constructor will initiate the parameters to calculate the results.

__Parameters__

\_rf: GTFS routes.txt
\_stf: GTFS stop times.txt
\_tf: GTFS trips.txt
\_bus_stops: bus stops shape file
\_block: block groups shape file
\_bus_routes: bus routes shape file
stop_id: the stop id field of bus stops shape file
route_id: the route id field of bus routes shape file

```
calculate(self, output_path, population_name,  method = "overlap")
```
__Description__

This method calculates how many disadvantaged population are served by each bus line.

For the overlap method:
It calculates how many disadvantaged population in each overlap pieces of bus routes coverage and which routes these pieces belong to by following steps:

First create a buffer area of bus stops (default: 400 meters), and then union all the buffer areas of bus stops belonging to one bus route. This is considered to be the service area of each bus route. Then use all these service area to intersect with each other, after that, make each small parts as independent service area pieces, Finally we use the service area piece which is overlaid with the census block groups to calculate the disadvantaged population served by each small service area piece. 

For the centroid method:
The service coverage area of bus routes is calculated by measuring the distance from the block group centroid to the nearest transit stops of the routes. If the distance is less than or equal to 400 meters, then this block group is considered to be served by this bus route.

__Parameters__

output_path: the output folder used to store the results
population_name: the population field of block group shape file
method: "overlap" or "centroid"

__Example__

```
from cal_equality import CalEquality

cal = CalEquality('../input/routes.txt', '../input/stop_times.txt', '../input/trips.txt', '../input/BusStops_UTA/BusStops_UTA.shp', '../input/Utah_blck_grp/UT_blck_grp_2010.shp', '../input/BusRoutes_UTA/BusRoutes_UTA.shp', 'StopId', 'RouteId')
cal.calculate('../output/', "Age", "overlap")
```



__Output__

The output file __cal_equality.json__ and __equality_csv.csv__ will be generated in the output folder.

The return value of calculate() is a dictionary.

For overlap method:
PieceId: {'sum': Disadvantaged population, 'lines': a list of routes short names shows which routes the piece belongs to}

```
>>> 1770: {'sum': 154.0, 'lines': ['205', '200']}, 1771: {'sum': 48.0, 'lines': ['902']}

```

For centroid method:
Id: {'sum': Disadvantaged population, 'lines': a list of routes short names shows which routes the piece belongs to, 'blocks': the blocks which contains coordinate disadvantage population}

```
{"217": {"blocks": [450, 228, 502, 444, 264, 329, 586, 203, 301, 307, 688, 536, 403, 437, 790, 792, 411, 220, 170, 767], "sum": 13590.0, "lines": ["217"]}, "213": {"blocks": [391, 777, 142, 283, 294, 295, 298, 305, 55, 315, 62, 195, 324, 71, 461, 590, 589, 214, 353, 482, 358, 360, 105, 232, 118, 255], "sum": 12353.0, "lines": ["213"]}}
```

### DEAadapter.py
#### methods

```
calDEA(_excelfile, _output_path, _head_busline_str, _head_input_set, _head_output_set)
```
__Description__

Calculate the coefficiency. 

__Parameters__

\_excelfile: the input excel file

\_output_path: the folder to store the output file

\_head_busline_str: the field name of bus line

\_head_input_set: the field names of input for linear programming

\_head_output_set: the field name of output for linear programming

__Example__

```
import DEAadapter as da
da.calDEA('../input/DEA_input_dataset.xlsx', '../output/', 'Bus Line', set(['Hours', 'Miles', 'Bus Count']), set(['Customer']))
```

__Output__

The return value is a dictionary: dict[bus line] -> coefficiency, e.g
```
{"990": 0.0461, "516": 0.4766, "313": 0.2049, "513": 0.2873}
```

The output file __cal_dea.json__ and __dea_csv.csv__ will be generated in the output folder.


### cal_glpk.py
#### methods
```
getResults(input_cal, input_dea, output_path, glpkPath)
```
__Description__

This method will calculate the performance of each bus line based on the results of DEA and equality.

 At first it will generate a standard lp file based on the input parameters (reference:                                                                                                                                              ([http://www.gurobi.com/documentation/6.5/refman/lp_format.html](http://www.gurobi.com/documentation/6.5/refman/lp_format.html))):

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

Then it will call glpsol.exe to solve this file. For each remaining bus lines, operational efficiency weight, and equality weight, it will generate a lp file and solve it.

__Parameters__

input_cal: cal_equality.json, which is the result of equality
input_dea: cal_dea.json, which is the result of DEA
output_path: the output folder used to store the result files
glpkPath: the location of glpsol.exe

__Example__

```
import cal_glpk as cg
cg.getResults('../output/cal_equality.json', '../output/cal_dea.json', '../output/', 'C:\\Software\\winglpk-4.61\\glpk-4.61\\w64\\glpsol')
```

__Output__

The output file dea_excel.xls will be generated in the output folder. It will also store the detailed info for each bus line.


### cal_rank.py
#### methods
```
cal_rank(input_cal, input_dea, output_path)
```
__Description__

This method will do the optimization according to remaining bus lines, operational efficiency, and equality.

__Parameters__

input_cal: cal_equality.json, which is the result of equality
input_dea: cal_dea.json, which is the result of DEA
output_path: the output folder used to store the result files

__Example__
```
import cal_rank as cr
cr.cal_rank('../output/cal_equality.json', '../output/cal_dea.json', '../output/rank/')
```

__Output__

The output files for each remaining bus, operational efficiency weight, and equality weight will be generated in output folder.
