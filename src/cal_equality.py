# ##################################################################################
# Project               Bus Line Analysis
# (c) copyright         2016
# Orgnization           University of Utah
#
# @file                 fileHandler.py
# Description           calculate equality
# Author                Yi Ou
# Date                  9/15/2016
# ##################################################################################

from shapely.ops import cascaded_union, polygonize
from shapely.geometry import Point, Polygon, mapping, LineString
from fileHandler import *
from GTFSReader import *

from fileWriter import *
from rtree import index
import time
import os, platform
import json
import fileHandler as fh

rf = "../input/routes.txt"
stf = "../input/stop_times.txt"
tf = "../input/trips.txt"
busStops = "../input/BusStops_UTA/BusStops_UTA.shp"
block = "../input/Utah_blck_grp/UT_blck_grp_2010.shp"
busRoutes = "../input/BusRoutes_UTA/BusRoutes_UTA.shp"
excelfile = "../input/DEA/UTA Runcut File  Aug2016.xlsx"
stopfile  = "../input/DEA/Bus Stop Ridership Apr2016 Aug2016.xlsx"
outputPath = "../output/"
outputFile = "cal_equality.json"
outputCSV = "equality_csv.csv"

sys_windows = "Windows"

class CalEquality:
    def __init__ (self, _rf, _stf, _tf, _bus_stops, _block, _bus_routes, stop_id, route_id):

        # user defined id.
        self.stop_id = stop_id
        self.route_id = route_id

        # GTFS files rf->routes.txt , stf -> stop_times.txt, tf->trips.txt
        self.rf = _rf
        self.stf = _stf
        self.tf = _tf

        self.bus_routes = _bus_routes
        #self.excel_file = _excel_file
        #self.stop_file = _stop_file

        self.blocks = []
        self.routes = []
        self.points = []
        start = time.clock()
        self.rpMap = self.getrpMap()
        end = time.clock()
        #print("GTFSReader cost:", end - start)
        startFile = time.clock()
        self.fileReader = FileReader(_bus_stops, _block, _bus_routes)
        self.fileReader.initData()
        self.fw = fileWriter()
        endFile = time.clock()
        #print("ShapeFile read and prepossesing cost:", endFile-startFile)
        self.routesPointsMap = self.connectPoints()


    def overLap(self, polygon1, polygon2):
        return polygon1.intersection(polygon2)

    def makeRound(self, point, size):
        return Point(point[0], point[1]).buffer(size)

    def unionRounds(self, roundList):
        #print (roundList)
        if(roundList == []):
            return Polygon([(0,0),(0,1),(1,0)])
        unionRound = roundList[0]
        for round in roundList:
            if unionRound is None:
                unionRound = round
            if round is not None:
                unionRound = unionRound.union(round)
        return unionRound

    def getPolygon(self, points):
        return Polygon(points)

    """
         Get (stops,route) mapping information.
    """
    def getrpMap(self):
        GTFSinfo = GTFSReader(self.rf, self.stf, self.tf)
        return GTFSinfo.mapStopsToRoute()

    """
         Map stops to route.
    """

    def connectPoints(self):
        routesPointsMap = dict()
        recordDict = self.fileReader.busStopsRecordDicts

        stopsRecords = self.fileReader.getBusStopsRecords()

        for k,v in self.rpMap.items():
            points = []
            for item in v:
                # if(int(item) != 17280 and int(item) != 21453):
                #     continue
                points.append((item, self.getPointById(item, recordDict, stopsRecords)))
            routesPointsMap[k] = points
        return routesPointsMap


    # use stop_id here
    def getPointById(self, sid, recordDict, stopsRecords):
        for i in range(len(recordDict)):
            # user_defined stop_id
            if(float(recordDict[i][self.stop_id]) == float(sid)):
                return self.makeRound(stopsRecords[i].shape.points[0],400)

    """
        Merge route from different system.
    """
    def reduceRoutes(self):

        #shortNames = DEAadapter.parse(self.bus_routes, self.excel_file, self.stop_file)[0]

        # map id to route, and merge.
        GTFSinfo = GTFSReader(self.rf, self.stf, self.tf)
        idToShortName = GTFSinfo.mapIdtoShortName()

        newMap = dict()
        shortNameList = []
        for k,v in idToShortName.items():
            #if v in shortNames:
            newMap[k] = v
            shortNameList.append(v)

        #print (idToShortName.values())
        #print (shortNames)
        # print newMap
        # print shortNameList
        return newMap, shortNameList

    """
        New Shapefile using reduced(merged) routes.
    """
    def regenerate_filter_shapefile(self):


        routeLines = self.calDisByCentroidDistance()

        print (routeLines)
        bus_route_dict = self.fileReader.busRoutesRecordDicts
        newMap, short_name_list = self.reduceRoutes()

        bus_route_records = self.fileReader.getBusRoutesRecords()

        # for i,item in enumerate(bus_route_dict):
        #     item['shape'] = LineString(bus_route_records[i].shape.points).coords[:]

        filter_route_dict = []
        for item in bus_route_dict:
            if item['LineAbbr'] in short_name_list:
                filter_route_dict.append(item)

        # print len(bus_route_dict)
        # print len(filter_route_dict)

        #print (self.routesPointsMap)
        # filter rp map
        newRouteLines = dict()
        for k,v in routeLines.items():
            if k in newMap.keys():
                newRouteLines[newMap[k]] = v


        for item in filter_route_dict:
            item['shape'] = newRouteLines[item['LineAbbr']]

        filter_bus_list = []
        filter_rp_map = dict()
        for k,v in self.getrpMap().items():
            if k in newMap.keys():
                filter_rp_map[newMap[k]] = v
                filter_bus_list += v

        bus_stop_dict = self.fileReader.busStopsRecordDicts
        bus_stop_record = self.fileReader.getBusStopsRecords()
        #print (filter_bus_list)


        # filter_route_point_map = dict()
        # for k,v in filter_rp_map.items():
        #     point_list = []
        #     for i,b_item in enumerate(bus_stop_dict):
        #         if float(b_item['StopId']) in v:
        #             point_list.append(bus_stop_record[i].shape.points[0])
        #     filter_route_point_map[k] = point_list


        # for item in filter_route_dict:
        #     item['shape'] = filter_route_point_map[item['LineAbbr']]

        #print (filter_route_point_map)



        print (filter_route_dict)
        self.fw.write_new_route_file(filter_route_dict)
        return

        filter_stop_dict = []
        for i,item in enumerate(bus_stop_dict):
            item['shape'] = bus_stop_record[i].shape.points
            stop_id = float(item[self.stop_id])
            if stop_id in filter_bus_list:
                for k,v in filter_rp_map.items():
                    if stop_id in v:
                        item['BelongToLine'] = k
                        filter_stop_dict.append(item)

        #print (list(filter_stop_dict[0].keys()))
        self.fw.write_new_stop_file(filter_stop_dict)
        #print (len(bus_stop_dict))

    def linesOverLap(self, population_name, choice = 'piece'):
        lines = dict()
        busLine = []

        # filter
        filtedRoutes_map = self.reduceRoutes()[0]
        filtedRoutes = filtedRoutes_map.keys()
        #print (filtedRoutes)
        filted_routesPointsMap = dict()
        for k,v in self.routesPointsMap.items():
            if k in filtedRoutes:
                filted_routesPointsMap[k] = v


        #print (filted_routesPointsMap)
        #print filtedRoutes_map

        #return
        # print len(self.routesPointsMap)
        # print len(filted_routesPointsMap)
        # get union for each lines.

        #for k,v in self.routesPointsMap.items():
        for k,v in filted_routesPointsMap.items():
            line = []
            for pos, point in enumerate(v):
                if point[1] is not None:
                    #busLine.append(point[1].buffer(0.0).boundary)
                    line.append(point[1].buffer(0.0))
            lines[k] = cascaded_union(line)
            #lines[k] = line

        # print len(lines)
        if (choice == 'normal'):
            resultMap = self.calUnion(filted_routesPointsMap)
            # new_resultMap = dict()
            # for k,v in resultMap.items():
            #     new_resultMap[filtedRoutes_map[k]] = v

            self.fw.write_to_file_dict(lines, resultMap, filtedRoutes_map)
            return

        for k,v in lines.items():
            busLine.append(v.buffer(0.0).boundary)

        #print (len(busLine))
        #return
        print ("do polygonize")
        nodeList = list(polygonize(cascaded_union(busLine)))
        #print "size1:" + ", " + str(len(nodeList))

        #intersect with original one. if not, get rid of it.
        realList = []

        print ("intersect")

        GTFSinfo = GTFSReader(self.rf, self.stf, self.tf)
        idToShortName = GTFSinfo.mapIdtoShortName()

        peice_in_lines = []
        test_list = []
        for i,node in enumerate(nodeList):
            flag = False
            lineStrList = []
            for k,v in lines.items():
                size = node.intersection(v).area
                #print(size)
                if(size > 1):
                    lineStrList.append(idToShortName[k])
                if(flag == False and size > 1):

                    test_list.append(node)
                    node_area = node.area
                    inter_area = node.intersection(v).buffer(0.0).area
                    if(float(inter_area)/node_area < 0.9):
                        realList.append(node.intersection(v).buffer(0.0))
                    else:
                        realList.append(node)
                    flag = True

            if len(lineStrList) != 0:
                peice_in_lines.append(lineStrList)

        #for i, r in enumerate(realList):
        #    if (i == 262 or i == 263):
        #        print ("cicici:", i)
        #        print ("xiixixixixi:", test_list[i].area)
        #        print r.area
        ###### Debug
        #return
#                print("inters",v.intersection(node))
        #print (realList)
        #print (peice_in_lines)
        #print len(peice_in_lines)

        #print "size2:" + ", " + str(len(realList))
        print ("ready to write file.")
        resultList = self.calUnionOfPiece(realList, population_name)

        resultMap = dict()
        counter = 0
        for i,item in enumerate(resultList):
            sums = 0.0
            for k,v in item.items():
                sums += v
            resultMap[i] = {"sum":sums, "lines": peice_in_lines[i]}

        self.fw.write_to_file(realList, resultList, population_name)

        print resultMap
        return resultMap

    # calculate intersection among block and stops regions.
    def calsbInter(self, blockPoly, point):
        overLap = self.overLap(point, blockPoly)
        ratio = float(overLap.area)/float(blockPoly.area)
        if(ratio >= 1.0):
            return 1.0

        return ratio

    def getRatioOfPeople(self, ratio, peopleType, blocksRecordsDict):
        return ratio*blocksRecordsDict[peopleType]

    def calUnion(self, filted_routesPointsMap):
        blocksRecords = self.fileReader.getBlocksRecords();
        blocksRecordsDict = self.fileReader.blocksRecordDicts
        blockPolyList = []
        poly = self.getPolygon(blocksRecords[0].shape.points)

        #------- get rounds union
        pointUnionMap = dict()
        startUnion = time.clock()

        lines = []
        linesPolys = []

        # # filter
        # filtedRoutes = self.reduceRoutes()[0].keys()
        # #print (filtedRoutes)
        # filted_routesPointsMap = dict()
        # for k,v in self.routesPointsMap.items():
        #         filted_routesPointsMap[k] = v

        for k,v in filted_routesPointsMap.items():
            idx = index.Index()
        #     if k in filtedRoutes:
            for pos, point in enumerate(v):
                if point[1] is not None:
                    #lines.append(point[1].boundary)
                    idx.insert(pos, point[1].bounds)
            pointUnionMap[k] = idx

        #nodeList = list(polygonize(cascaded_union(lines)))
        #print (lines)
        #self.fw.write_to_file(nodeList)
        endUnion = time.clock()
        print ("union cost:" + ", " + str(endUnion - startUnion))

        #return
        ############################################################
        #
        # Calutlate the insection and the percentage of minority.
        #
        ############################################################

        resultMap = dict()
        for k,v in pointUnionMap.items():
            tmpMap = dict()
            tmpMap["Age"] = 0
            tmpMap["Poverty"] = 0
            tmpMap["Disability"] = 0
            tmpMap["Race"] = 0
            tmpMap["Unemploy"] = 0
            tmpMap["Transporta"] = 0
            resultMap[k] = tmpMap

        start = time.clock()
        for i in range(len(blocksRecords)):
            #print i
            # if(blocksRecordsDict[i]["GEOID10"] != "490351134091"):
            #         continue
            poly = self.getPolygon(blocksRecords[i].shape.points)
            for k, v in pointUnionMap.items():
                # if(int(k) != 64188):
                #     continue
                if v is not None:
                    merged_points = cascaded_union([self.routesPointsMap[k][pos][1] for pos in v.intersection(poly.bounds)])
                    #print (merged_points)
                    overLapRatio = self.calsbInter(poly.buffer(0.0),merged_points)

                    resultMap[k]["Age"] += int(self.getRatioOfPeople(overLapRatio,"Age",blocksRecordsDict[i]))
                    resultMap[k]["Poverty"] += int(self.getRatioOfPeople(overLapRatio,"Poverty",blocksRecordsDict[i]))
                    resultMap[k]["Disability"] += int(self.getRatioOfPeople(overLapRatio,"Disability",blocksRecordsDict[i]))
                    resultMap[k]["Race"] += int(self.getRatioOfPeople(overLapRatio,"Race",blocksRecordsDict[i]))
                    resultMap[k]["Unemploy"] += int(self.getRatioOfPeople(overLapRatio,"Unemploy",blocksRecordsDict[i]))
                    resultMap[k]["Transporta"] += int(self.getRatioOfPeople(overLapRatio,"Transporta",blocksRecordsDict[i]))

        end = time.clock()
        #print"intersection cost:" + ", " + str(end - start)
#        print (resultMap)
        # print resultmap
        #print("routesID,Age,Poeverty,Disability,Race,Unemploy,Transporta")
        # for k,v in resultMap.items():
        #     print(k, ",", v["Age"], ",", v["Poverty"], ",", v["Disability"], ",", v["Race"], ",", v["Unemploy"], ",", v["Transporta"])
        return resultMap
        #return resultMap

    ################################
    #
    #
    #
    ################################

    def calUnionOfPiece(self, pieceList, population_name):
        blocksRecords = self.fileReader.getBlocksRecords();
        blocksRecordsDict = self.fileReader.blocksRecordDicts
        blockPolyList = []
        poly = self.getPolygon(blocksRecords[0].shape.points)

        #------- get rounds union
        pointUnionMap = []
        startUnion = time.clock()

        lines = []
        linesPolys = []
        for i, val in enumerate(pieceList):
            idx = index.Index()
            #lines.append(point[1].boundary)
            idx.insert(i, val.bounds)
            pointUnionMap.append(idx)

        #nodeList = list(polygonize(cascaded_union(lines)))
        #print (lines)
        #self.fw.write_to_file(nodeList)
        endUnion = time.clock()
        #print "union cost:" + ", " + str(endUnion - startUnion)

        #return

        ############################################################
        #
        # Calutlate the insection and the percentage of minority.
        #
        ############################################################

        resultList = []
        for i in range(len(pieceList)):
            tmpMap = dict()
            tmpMap[population_name] = 0
            # tmpMap["Poverty"] = 0
            # tmpMap["Disability"] = 0
            # tmpMap["Race"] = 0
            # tmpMap["Unemploy"] = 0
            # tmpMap["Transporta"] = 0
            resultList.append(tmpMap)

        start = time.clock()
        for i in range(len(blocksRecords)):
            #print i
            # if(blocksRecordsDict[i]["GEOID10"] != "490351134091"):
            #         continue
            poly = self.getPolygon(blocksRecords[i].shape.points)
            for k, v in enumerate(pieceList):
                if v is not None:
                    # merged_points =  v.intersection(poly.bounds)
                    # print (merged_points)
                    # if(v not in v.bounds.intersection(poly.bounds)):
                    #     continue;
                    overLapRatio = self.calsbInter(poly.buffer(0.0),v)

                    resultList[k][population_name] += int(self.getRatioOfPeople(overLapRatio,population_name,blocksRecordsDict[i]))
                    # resultList[k]["Poverty"] += int(self.getRatioOfPeople(overLapRatio,"Poverty",blocksRecordsDict[i]))
                    # resultList[k]["Disability"] += int(self.getRatioOfPeople(overLapRatio,"Disability",blocksRecordsDict[i]))
                    # resultList[k]["Race"] += int(self.getRatioOfPeople(overLapRatio,"Race",blocksRecordsDict[i]))
                    # resultList[k]["Unemploy"] += int(self.getRatioOfPeople(overLapRatio,"Unemploy",blocksRecordsDict[i]))
                    # resultList[k]["Transporta"] += int(self.getRatioOfPeople(overLapRatio,"Transporta",blocksRecordsDict[i]))

        # manually fix
        #resultList[262]["Age"] = 15
        #resultList[262]["Poverty"] = 2
        #resultList[262]["Disability"] = 2
        #resultList[262]["Race"] = 15
        #resultList[262]["Unemploy"] = 2
        #resultList[262]["Transporta"] = 0

        end = time.clock()
        #print "intersection cost:" + ", " + str(end - start)
#        print (resultMap)
        #print("routesID,Age,Poeverty,Disability,Race,Unemploy,Transporta")
        # print resultmap
        # for k,v in resultMap.items():
        #     print(k, ",", v["Age"], ",", v["Poverty"], ",", v["Disability"], ",", v["Race"], ",", v["Unemploy"], ",", v["Transporta"])

        return resultList

    def calDisByCentroidDistance(self, population_name):
        blocksRecords = self.fileReader.getBlocksRecords()
        blocksRecordsDicts = self.fileReader.blocksRecordDicts
        polys = [self.getPolygon(blockRecord.shape.points) for blockRecord in blocksRecords]
        polyCentroids = [poly.centroid for poly in polys]


         # filter
        # filtedRoutes_map = self.reduceRoutes()[0]

        # filtedRoutes = filtedRoutes_map.keys()
        # #print (filtedRoutes)
        # filted_routesPointsMap = dict()
        # for k,v in self.routesPointsMap.items():
        #     if k in filtedRoutes:
        #         filted_routesPointsMap[k] = v

        routesStopsMap = dict()
        for k,v in self.routesPointsMap.items():
            tmp = []
            for item in v:
                if item[1] is not None:
                    tmp.append(item[1].centroid)
            routesStopsMap[k] = tmp


        #print "----------routesstopsmap-------------"
        #print routesStopsMap

        routesLines = dict()
        for k,v in routesStopsMap.items():
            # if k != '64832':
            #     continue
            #print (v)
            routesLines[k] = [item.coords[:][0] for item in v]
            #print (routesLines[k])

        #print (routesLines)
        routesBlockSet = dict()
        for k,v in routesStopsMap.items():
            # if k != '64832':
            #     continue
            blockSet = set()
            for stop in v:
                for id,block in enumerate(polyCentroids):
                    if stop.distance(block) < 400:
                        blockSet.add(id)

            #print (blockSet)
            routesBlockSet[k] = blockSet

        print "----------routesBlockSet-------------"
        print routesBlockSet

        resultMap = dict()
        for k,v in routesBlockSet.items():
            # if k != '64832':
            #     continue
            tmpMap = dict()

            tmpMap[population_name] = 0
            # tmpMap["PovertyCentroid"] = 0
            # tmpMap["DisabilityCentroid"] = 0
            # tmpMap["RaceCentroid"] = 0
            # tmpMap["UnemployCentroid"] = 0
            # tmpMap["TransportaCentroid"] = 0

            for item in v:
                tmpMap[population_name] += self.getRatioOfPeople(1.0,population_name, blocksRecordsDicts[item])
                # tmpMap["PovertyCentroid"] += self.getRatioOfPeople(1.0,"Poverty", blocksRecordsDicts[item])
                # tmpMap["DisabilityCentroid"] += self.getRatioOfPeople(1.0,"Disability", blocksRecordsDicts[item])
                # tmpMap["RaceCentroid"] += self.getRatioOfPeople(1.0,"Race", blocksRecordsDicts[item])
                # tmpMap["UnemployCentroid"] += self.getRatioOfPeople(1.0,"Unemploy", blocksRecordsDicts[item])
                # tmpMap["TransportaCentroid"] += self.getRatioOfPeople(1.0,"Transporta", blocksRecordsDicts[item])
            resultMap[k] = tmpMap

        #return routesLines
        centroid_result_map = dict()

        # get id short name map.
        GTFSinfo = GTFSReader(self.rf, self.stf, self.tf)
        idToShortName = GTFSinfo.mapIdtoShortName()
        for k,v in resultMap.items():
            dis_sum = 0.0
            for k1,v1 in v.items():
                dis_sum = dis_sum + v1

            if k in idToShortName.keys():
                centroid_result_map[idToShortName[k]] = {'sum':dis_sum, 'lines': [idToShortName[k]], 'blocks': list(routesBlockSet[k])}

        return centroid_result_map
        #self.fw.write_to_file_dict_centroid(routesLines, resultMap)

    def handleMagicPiece(self):
        data = shapefile.Reader("../input/Magic_piece/piece.shp")
        print (data.shapeRecords()[0].shape.points)

        blocksRecords = self.fileReader.getBlocksRecords()
        blocksRecordsDict = self.fileReader.blocksRecordDicts

        resultList = dict()

        resultList["Age"] = 0
        resultList["Poverty"] = 0
        resultList["Disability"] = 0
        resultList["Race"] = 0
        resultList["Unemploy"] = 0
        resultList["Transporta"] = 0

        for i in range(len(blocksRecords)):
            print (i)
            # if(blocksRecordsDict[i]["GEOID10"] != "490351134091"):
            #         continue
            poly = self.getPolygon(blocksRecords[i].shape.points)

            overLapRatio = self.calsbInter(poly.buffer(0.0), self.getPolygon(data.shapeRecords()[0].shape.points).buffer(0.0))

            resultList["Age"] += int(self.getRatioOfPeople(overLapRatio,"Age",blocksRecordsDict[i]))
            resultList["Poverty"] += int(self.getRatioOfPeople(overLapRatio,"Poverty",blocksRecordsDict[i]))
            resultList["Disability"] += int(self.getRatioOfPeople(overLapRatio,"Disability",blocksRecordsDict[i]))
            resultList["Race"] += int(self.getRatioOfPeople(overLapRatio,"Race",blocksRecordsDict[i]))
            resultList["Unemploy"] += int(self.getRatioOfPeople(overLapRatio,"Unemploy",blocksRecordsDict[i]))
            resultList["Transporta"] += int(self.getRatioOfPeople(overLapRatio,"Transporta",blocksRecordsDict[i]))

        print (resultList)

    def compareDiffWays(self):


        resultMap1 = self.calUnion()
        resultMap2 = self.calDisByCentroidDistance()
        resultList = []
        for k,v in resultMap1.items():
            tmpDict = dict()
            v.update(resultMap2[k])
            v["AgeDiff"] = v["Age"] - int(v["AgeCentroid"])
            v["PovertyDiff"] = v["Poverty"] - int(v["PovertyCentroid"])
            v["DisabilityDiff"] = v["Disability"] - int(v["DisabilityCentroid"])
            v["RaceDiff"] = v["Race"] - int(v["RaceCentroid"])
            v["UnemployDiff"] = v["Unemploy"] - int(v["UnemployCentroid"])
            v["TransportaDiff"] = v["Transporta"] - int(v["TransportaCentroid"])
            tmpDict["id"] = k
            tmpDict.update(v)
            resultList.append(tmpDict)

        self.fw.writeExcel(resultList, 'resultDiff')

    '''
        Choose calculation methods.
    '''
    def calculate(self, output_path, population_name,  method = "overlap"):
        resultMap = dict()
        if method == "overlap":
            resultMap = self.linesOverLap(population_name)
            # Write CSV
            csv_filename = output_path + outputCSV
            csv_fd = fh.openRegularFile(csv_filename)
            csv_fw = fh.getCSVFileWriter(csv_fd, ['ID', 'Total Served People', 'Bus line'])
            fh.writeCSVFileHeader(csv_fw)
            bus_line_str = ""
            for key, value in resultMap.items():
                for line in value['lines']:
                    bus_line_str += line + " "
                fh.writeCSVRow(csv_fw, {'ID': key, 'Total Served People': value['sum'], 'Bus line' : bus_line_str})
            fh.closeRegularFile(csv_fd)
        elif method == "centroid":
            resultMap = self.calDisByCentroidDistance(population_name)
            # Write CSV
            csv_filename = output_path + outputCSV
            csv_fd = fh.openRegularFile(csv_filename)
            csv_fw = fh.getCSVFileWriter(csv_fd, ['ID', 'Total Served People', 'Bus line', 'Block ID'])
            fh.writeCSVFileHeader(csv_fw)
            bus_line_str = ""
            blocks_str = ""
            for key, value in resultMap.items():
                for line in value['lines']:
                    bus_line_str += line + " "
                for block in value['blocks']:
                    blocks_str += str(block) + " "
                fh.writeCSVRow(csv_fw, {'ID': key, 'Total Served People': value['sum'], 'Bus line': bus_line_str, 'Block ID' : blocks_str})
            fh.closeRegularFile(csv_fd)

        # dump json file
        jsonStr = json.dumps(resultMap)
        fd = fh.openRegularFile(output_path + outputFile)
        fh.writeRegularFile(fd, jsonStr)
        fh.closeRegularFile(fd)
        return resultMap

if __name__ == '__main__':
    # check OS
    if(platform.system() == sys_windows):
        rf = rf.replace("/", "\\")
        stf = stf.replace("/", "\\")
        tf = tf.replace("/", "\\")
        busStops = busStops.replace("/", "\\")
        block = block.replace("/", "\\")
        busRoutes = busRoutes.replace("/", "\\")
        outputFile = outputFile.replace("/", "\\")

    stop_id = "StopId"
    route_id = "RouteId"
    cal = CalEquality(rf, stf, tf, busStops, block, busRoutes, stop_id, route_id)
    cal.calculate(outputPath, "Age", "overlap")