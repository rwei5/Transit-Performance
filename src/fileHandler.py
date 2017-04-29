# ##################################################################################
# Project               Bus Line Analysis
# (c) copyright         2016
# Orgnization           University of Utah
#
# @file                 fileHandler.py
# Description           Read file and write output files
# Author                Yi Ou / Yongjian Mu
# Date                  9/15/2016
# ##################################################################################
import shapefile
import sys, os
import xlrd
import xlwt
import csv

# Constant Var
type_xlsx =                     ".xlsx"
type_xls =                      ".xls"
type_shp =                      ".shp"
type_txt =                      ".txt"

# ##################################################################################
# @brief                Create writable excel file with table
#
# @param    tablename   Table name
# @return               file handler and table
# ##################################################################################
def excelWritableCreate(tablename):
    file = xlwt.Workbook()
    table = file.add_sheet(tablename)
    return file, table
    
# ##################################################################################
# @brief                Save excel file with name
#
# @param    file        File handler
# @param    filename    Filename
# @return               
# ##################################################################################
def excelWritableSave(file, filename):
    file.save(filename)
    
# ##################################################################################
# @brief                Write cell to excel file
#
# @param    table       Current table
# @param    row         Current row
# @param    col         Current col
# @param    value       Value to write
# @return               
# ##################################################################################
def excelWritableCell(table, row, col, value):
    table.write(row, col, value)
    

# ##################################################################################
# @brief                Parse txt file as input data
#
# @param filename       Input file name
# @return               File data
# ##################################################################################

def _parseTXT(filename):
    print("Start parse input file " + filename)
    data = open(filename, "r")
    return data

# ##################################################################################
# @brief                Parse excel file as input data
#
# @param filename       Input file name
# @return               Miles dict
# ##################################################################################

def _parseShp(filename):
    dict = {}
    sf = shapefile.Reader(filename)
    shapes = sf.shapes()
    for i in range (len(shapes)):
        dict[sf.records()[i][0]] = float(sf.records()[i][4]) / 1000.0
    return dict


# ##################################################################################
# @brief                Parse excel file as input data
#
# @param filename       Input file name
# @return               File data
# ##################################################################################

def _parseXLSX(filename):
    #print("Start parse input file " + filename)
    data = xlrd.open_workbook(filename)
    return data

# ##################################################################################
# @brief                Get csv file writer
#
# @param full_name      File handler
# @return               File writer
# ##################################################################################
def getCSVFileWriter(fd, fields):
    return csv.DictWriter(fd, fieldnames=fields, lineterminator='\n')

# ##################################################################################
# @brief                Write csv file header
#
# @param full_name      File writer
# @return
# ##################################################################################
def writeCSVFileHeader(fw):
    fw.writeheader()

# ##################################################################################
# @brief                Write single line of a csv file
#
# @param full_name      File writer
# @return
# ##################################################################################
def writeCSVRow(fw, profile):
    fw.writerow(profile)

# ##################################################################################
# @brief                Open regular file
#
# @param filename       Input file name
# @return               File handler
# ##################################################################################
def openRegularFile(filename):
    return open(filename, 'w')
    
# ##################################################################################
# @brief                Close regular file
#
# @param fd             File handlers
# @return               
# ##################################################################################
def closeRegularFile(fd):
    fd.close()
    
# ##################################################################################
# @brief                Write regular file
#
# @param fd             File handler
# @param str            The string will be written to the file
# @return               
# ##################################################################################
def writeRegularFile(fd, str):
    fd.writelines(str)

# ##################################################################################
# @brief                Exception for error file type
#
# @return
# ##################################################################################

def _errhandler():
    print("File type cannot support")

# map the inputs to the function blocks
file_type = {
    type_xlsx : _parseXLSX,
    type_xls : _parseXLSX,
    type_shp  : _parseShp,
    type_txt  : _parseTXT,
}

# ##################################################################################
# @brief                Parse the input file. 
#                       This function will call different internal functions 
#                       according to the extend name of the input file.
#
# @param filename       Input file name
# @param sheed_id       Excel sheet NO.
# @return               File data
# ##################################################################################

def parseInputFile(filename, sheet_id = 0):
    split_name = os.path.splitext(filename)
    get_type = split_name[len(split_name) - 1].lower()
    return file_type.get(get_type, _errhandler)(filename)


class FileReader:

    def __init__ (self, busStops="../input/BusStops_UTA/BusStops_UTA.shp", blocks="../input/Utah_blck_grp/UT_blck_grp_2010.shp", busRoutes="../input/BusRoutes_UTA/BusRoutes_UTA.shp"):
        # init fileName
        self.busStops_fileName = busStops
        self.blocks_fileName = blocks
        self.busRoutes_fileName = busRoutes
        # shapeFile Readers
        self.busStopsReader = None
        self.blocksReader = None
        self.busRoutesReader = None
        # dicts for bus stops, blocks, busRoutes records.
        self.busStopsRecordDicts = dict()
        self.blocksRecordDicts = dict()
        self.busRoutesRecordDicts = dict()

    def initData(self):

        self.busStopsReader = self.readData(self.busStops_fileName)
        self.blocksReader = self.readData(self.blocks_fileName)
        self.busRoutesReader = self.readData(self.busRoutes_fileName)

        self.busStopsRecordDicts = self.createDicts(self.getBusStopsRecords(), self.getBusStopsFields())
        self.blocksRecordDicts = self.createDicts(self.getBlocksRecords(), self.getBlocksFields())
        self.busRoutesRecordDicts = self.createDicts(self.getBusRoutesRecords(), self.getBusRoutesFields())

    def readData(self, fileName):
        shp_reader = shapefile.Reader(fileName)
        return shp_reader

    def createDicts(self, records, fields):
        maps = []
        for i in range(len(records)):
            d = dict()
            for j in range(len(records[i].record)):
                d[str(fields[j+1][0])] = records[i].record[j]
            maps.append(d)
        return maps

    def getBusStopsRecords(self):
        return self.busStopsReader.shapeRecords()

    def getBlocksRecords(self):
        return self.blocksReader.shapeRecords()

    def getBusRoutesRecords(self):
        return self.busRoutesReader.shapeRecords()

    def getBusStopsFields(self):
        return self.busStopsReader.fields

    def getBlocksFields(self):
        return self.blocksReader.fields

    def getBusRoutesFields(self):
        return self.busRoutesReader.fields
