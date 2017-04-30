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
from DEA import DEA
import fileHandler as fh
import platform
import json

inputExcel = "../input/DEA_input_dataset.xlsx"
outputPath = "../output/"
outputFile = "cal_dea.json"
outputCSV = "dea_csv.csv"
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
    table = data.sheets()[0]
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
                if (isinstance(table.cell(rowcnt, colcnt).value, float)):
                    names.append(str(int(table.cell(rowcnt, colcnt).value)))
                else:
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

    # Write json file
    jsonStr = json.dumps(dict)
    fd = fh.openRegularFile(_output_path + outputFile)
    fh.writeRegularFile(fd, jsonStr)
    fh.closeRegularFile(fd)

    # Write CSV file
    csv_filename = _output_path + outputCSV
    csv_fd = fh.openRegularFile(csv_filename)
    csv_fw = fh.getCSVFileWriter(csv_fd, ['Bus Line', 'Operational Efficiency'])
    fh.writeCSVFileHeader(csv_fw)
    for key, value in dict.items():
        fh.writeCSVRow(csv_fw, {'Bus Line' : key, 'Operational Efficiency' : value})
    fh.closeRegularFile(csv_fd)

    # Write excel
    ref_data = fh.parseInputFile(_excelfile)
    ref_table = ref_data.sheets()[0]
    ref_nrows = ref_table.nrows
    ref_ncols = ref_table.ncols
    rowcnt = 0
    outfile, outtable = fh.excelWritableCreate("result")

    # get busline id column
    colcnt = 0
    busline_column_id = 0
    while(colcnt < ref_ncols):
        if(str(ref_table.cell(rowcnt, colcnt).value) == _head_busline_str):
            busline_column_id = colcnt
            break
        colcnt += 1

    while(rowcnt < ref_nrows):
        colcnt = 0
        while(colcnt < ref_ncols):
            fh.excelWritableCell(outtable, rowcnt, colcnt, ref_table.cell(rowcnt, colcnt).value)
            colcnt += 1
        if(0 == rowcnt):
            fh.excelWritableCell(outtable, rowcnt, colcnt, 'Operational Efficiency')
        else:
            cur_busline = ""
            if (isinstance(ref_table.cell(rowcnt, busline_column_id).value, float)):
                cur_busline = str(int(ref_table.cell(rowcnt, busline_column_id).value))
            else:
                cur_busline = str(ref_table.cell(rowcnt, busline_column_id).value)
            fh.excelWritableCell(outtable, rowcnt, colcnt, dict[cur_busline])
        rowcnt += 1

    fh.excelWritableSave(outfile, _output_path + outputExcel)

    return dict

if __name__ == "__main__":
    if(platform.system() == sys_windows):
        inputExcel = inputExcel.replace("/", "\\")
        outputFile = outputFile.replace("/", "\\")
        outputExcel = outputExcel.replace("/", "\\")
        outputPath = outputPath.replace("/", "\\")

        calDEA(inputExcel, outputPath, headBuslineStr, headInputSet, headOutputSet)


