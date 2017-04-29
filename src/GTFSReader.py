# ###############################################################################
# Project                UTA Analysis
# (c) copyright          2016
# Orgnization            University of Utah
#
# @file                  GTFSReader.py
# Description            Read GTFS file to connect stops and routes
# Author                 Yi Ou
# Date
# ###############################################################################

import sys
import os, platform

sf = "../input/stops.txt"
stf = "../input/stop_times.txt"
tf = "../input/trips.txt"
sys_windows = "Windows"

class GTFSReader:
    def __init__ (self, routesFile, stopsTimeFile, tripFile):
        #self.stops = self.readData(stopsFile)
        self.stopsTime = self.readData(stopsTimeFile)
        self.trip = self.readData(tripFile)
        self.routes = self.readData(routesFile)

    def readData(self, fileName):
        content = []
        with open(fileName) as f:
            content = f.readlines()
        return content

    def mapIdtoShortName(self):

        maps = dict()
        for line in self.routes[1:]:
            lineList = line.split(",")
            maps[lineList[0]] = lineList[2]
        return maps

    def mapStopsToRoute(self):
        routeTripMap = self.getRouteTrip()
        routeStopMap = dict()

        routeStop = []

        for line in self.stopsTime[1:]:
            oneStopsTime = line.split(",")
            routeStop.append(oneStopsTime)

        for k,v in routeTripMap.items():
            routeStopMap[k] = []

        for k,v in routeTripMap.items():

            for stop in routeStop:
                if(stop[0] == v[0] or stop[0] == v[-1]):
                    routeStopMap[k].append(int(stop[3]))


        return routeStopMap

    def getRouteTrip(self):
        routeTrip = []
        routeTripMap = dict()
        for line in self.trip[1:]:
            oneRouteTrip = line.split(",")
            routeTrip.append(oneRouteTrip)

        for route in routeTrip:
            routeTripMap[route[0]] = []

        for route in routeTrip:
            routeTripMap[route[0]].append(route[2])

        return routeTripMap


if __name__ == '__main__':
    # check OS
    if(platform.system() == sys_windows):
        sf = sf.replace("/", "\\")
        stf = stf.replace("/", "\\")
        tf = tf.replace("/", "\\")
    reader = GTFSReader(sf, stf, tf)
    reader.mapIdtoShortName()
#    reader.readData(sf)
#    reader.mapStopsnToRoute()
