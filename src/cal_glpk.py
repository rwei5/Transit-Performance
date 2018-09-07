# ##################################################################################
# Project               Bus Line Analysis
# (c) copyright         2016
# Orgnization           University of Utah
#
# @file                 cal_glpk.py
# Description           Use glpk package to optimize model
# Author                Yongjian Mu
# Date                  2/13/2017
# ##################################################################################

# C:\Software\winglpk-4.61\glpk-4.61\w64\glpsol --lp .\model_overlay.lp -o 2
import os, platform
import time
import json
import model_overlay as mo
import fileHandler as fh

inputLpFile = "model_overlay.lp"
inputCal = "../output/cal_equality.json"
inputDea = "../output/cal_dea.json"
outputRet = "glpk_result"
outputExcel = "glpk_excel"
outputPath = "../output/"
glpkPath = "C:\\Software\\winglpk-4.61\\glpk-4.61\\w64\\glpsol"
glpkSuffix = " --lp "
glpkFlag = " -o "

sys_windows = "Windows"

def glpkSolve(input_file):
    print "****Got input file"
    print input_file
    fd = open(input_file, 'r')
    start_parse = False
    XSol = set('')
    Z1 = 0.0
    Z2 = 0.0
    Z3 = 0.0
    while True:
        line = fd.readline()
        # print line
        if line.find("Integer feasibility conditions") >= 0:
            break
        if line.find("No. Column name") >= 0:
            start_parse = True
            continue
        if start_parse and line.find("X") >= 0:
            r = line.split()
            if(r[3] == "1"):
                XSol.add(r[1][1:])
        if start_parse and line.find("Z1") >= 0:
            r = line.split()
            print "***split Z1***\n"
            print r
            Z1 = float(r[2])
        if start_parse and line.find("Z2") >= 0:
            r = line.split()
            Z2 = float(r[2])
        if start_parse and line.find("Z3") >= 0:
            r = line.split()
            Z3 = float(r[2])
    fd.close()
    print "***** finish glpk parse"
    print XSol
    print Z1
    print Z2
    print Z3
    return XSol, Z1, Z2, Z3

def getResults(input_cal, input_dea, output_path, glpkPath):
    with open(input_cal) as f:
        dict_equality = json.load(f)
    with open(input_dea) as f:
        dict_dea = json.load(f)

    remain_buslines = len(dict_dea)
    coeff_weight = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    output_excel_file = output_path + outputExcel + time.strftime('%Y-%m-%d-%H-%I-%M-%S',time.localtime(time.time())) + ".xls"
    excelHead = ["Remain BusLine", "Operational Efficiency Weight", "Equality Weight", "Z1 for Coeff", "Z2 for Equality", "Z3 for Equality not Normalize"]
    file, table = fh.excelWritableCreate("result")
    for i in range (0,6):
        fh.excelWritableCell(table, 0, i, excelHead[i])

    row = 1
    for p in range (1, remain_buslines + 1):
        for w in coeff_weight:
            mo.mainFunc(p, w, 1 - w, input_cal, input_dea)
            retFile = output_path + outputRet + "_remain_" + str(p) + "_weight_operational_efficiency_" + str(w) + ".txt"
            # use glpk to calculate results
            current_output_file = glpkPath + glpkSuffix + inputLpFile + glpkFlag + retFile
            os.system(current_output_file)
            XSol, Z1, Z2, Z3 = glpkSolve(retFile)
            if (1.0 == w and p > 0.0):
                for key, value in dict_equality.items():
                    for line in value['lines']:
                        if ((line) in XSol):
                            Z3 += value['sum']
                            break;
                            # Write to excel
            fh.excelWritableCell(table, row, 0, str(p))
            fh.excelWritableCell(table, row, 1, str(w))
            fh.excelWritableCell(table, row, 2, str("%.1f" % (1 - w)))
            fh.excelWritableCell(table, row, 3, str("%.4f" % Z1))
            fh.excelWritableCell(table, row, 4, str("%.4f" % Z2))
            fh.excelWritableCell(table, row, 5, str("%.4f" % Z3))
            row += 1
    fh.excelWritableSave(file, output_excel_file)

if __name__ == '__main__':
    if(platform.system() == sys_windows):
        inputLpFile = inputLpFile.replace("/", "\\")
        inputCal = inputCal.replace("/", "\\")
        inputDea = inputDea.replace("/", "\\")
        outputPath = outputPath.replace("/", "\\")
        outputRet = outputRet.replace("/", "\\")
        outputExcel = outputExcel.replace("/", "\\")
        glpkPath = glpkPath.replace("/", "\\")

    getResults(inputCal, inputDea, outputPath, glpkPath)