# ##################################################################################
# Project               Bus Line Analysis
# (c) copyright         2016
# Orgnization           University of Utah
# 
# @file                 DEAadapter.py
# Description           API for data envelopment Analysis Core
# Author                Yongjian Mu
# Date                  11/12/2015
# ##################################################################################

import numpy as np
import xlrd
import time
import datetime
from DEA import DEA
import fileHandler as fh
import os, platform
import json

inputExcel = "../input/DEA_input_dataset.xlsx"
outputPath = "../output/"
outputFile = "cal_dea.json"
outputExcel = "dea_excel.xls"

headBuslineStr = "Bus Line"
headInputSet = set(['Hours', 'Miles', 'Bus Count'])
headOutputSet = set(['Customer'])

sys_windows = "Windows"

# ##################################################################################
# @brief                Calculate the bus line. This is the actually interface to
#                       provide the parameters to DEA core.
#
# @return               Bus name, output, input
# ##################################################################################
def parse(_excelfile, _head_busline_str, _head_input_set, _head_output_set):
    data = fh.parseInputFile(_excelfile)
    table = data.sheets()[0] # sheet id = 0, get Aug data
    nrows = table.nrows
    ncols = table.ncols

    # get DEA input
    y = []
    x = []
    names = []
    rowcnt = 1 # eat first row
    while(rowcnt < nrows):
        tempX = []
        tempY = []

        colcnt = 0
        while(colcnt < ncols):
            # check bus line name
            if(str(table.cell(0, colcnt).value) == _head_busline_str):
                names.append(str(table.cell(rowcnt, colcnt).value))
            #check input
            if (str(table.cell(0, colcnt).value) in _head_input_set):
                tempX.append(float(table.cell(rowcnt, colcnt).value))
            # check output
            if (str(table.cell(0, colcnt).value) in _head_output_set):
                tempY.append(float(table.cell(rowcnt, colcnt).value))
            colcnt += 1

        x.append(tempX)
        y.append(tempY)

        rowcnt += 1
        print names[len(names) - 1]
        print tempX
        print tempY

    print(len(names))
    return names, y, x


# ##################################################################################
# @brief                Calculate the coefficiency.
#
# @return               Dict: dict[bus line] -> coefficiency
# ##################################################################################
def calDEA(_excelfile, _output_path, _head_busline_str, _head_input_set, _head_output_set):
    names, _Y, _X = parse(_excelfile, _head_busline_str, _head_input_set, _head_output_set)
    X = np.array(_X)
    Y = np.array(_Y)
    #print(X)
    #print(Y)
    dea = DEA(X,Y)
    dea.name_units(names)
    dict = dea.getResult()
    jsonStr = json.dumps(dict)
    fd = fh.openRegularFile(_output_path + outputFile)
    fh.writeRegularFile(fd, jsonStr)
    fh.closeRegularFile(fd)

    # Extra parse
    '''
    excelHead = ["Line", "Miles Cost", "Time Cost", "Bus Quantity", "Customer", "Coefficiency"]
    file, table1 = fh.excelWritableCreate("result")
    for i in range (0,6):
        fh.excelWritableCell(table1, 0, i, excelHead[i])
        
    for row in range(0, len(names)):
        # Write to excel
        fh.excelWritableCell(table1, row + 1, 0, names[row])
        fh.excelWritableCell(table1, row + 1, 1, ("%.4f" % (_X[row][0])))
        fh.excelWritableCell(table1, row + 1, 2, ("%.4f" % (_X[row][1])))
        fh.excelWritableCell(table1, row + 1, 3, (_X[row][2]))
        fh.excelWritableCell(table1, row + 1, 4, ("%.4f" % _Y[row][0]))
        fh.excelWritableCell(table1, row + 1, 5, ("%.4f" % dict[names[row]]))
    fh.excelWritableSave(file, _output_path + outputExcel)
    '''

    return dict

if __name__ == "__main__":
    if(platform.system() == sys_windows):
        inputExcel = inputExcel.replace("/", "\\")
        outputFile = outputFile.replace("/", "\\")
        outputExcel = outputExcel.replace("/", "\\")
        outputPath = outputPath.replace("/", "\\")

        calDEA(inputExcel, outputPath, headBuslineStr, headInputSet, headOutputSet)
    #parse()


