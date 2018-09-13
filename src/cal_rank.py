# ##################################################################################
# Project               Bus Line Analysis
# (c) copyright         2016
# Orgnization           University of Utah
#
# @file                 cal_rank.py
# Description           Calculate the solution by remain bus lines, operational efficiency and equality
# Author                Yongjian Mu
# Date                  2/13/2017
# ##################################################################################

import os, platform, sys
import json
import fileHandler as fh
from cal_glpk import glpkSolve

inputCal = "../output/cal_equality.json"
inputDea = "../output/cal_dea.json"
outputPath = "../output/"
outputExcel = "rank_excel"
sys_windows = "Windows"

def cal_rank(input_cal, input_dea, output_path):
    # Read dict file
    with open(input_cal) as f:
        dict_equality = json.load(f)
    with open(input_dea) as f:
        dict_dea = json.load(f)

    ## Standardize equlity, get the max and min value of served population
    #min_sum = sys.float_info.max
    #max_sum = sys.float_info.min
    #for key, value in dict_equality.items():
        #if(value['sum'] < min_sum):
            #min_sum = value['sum']
        #if(value['sum'] > max_sum):
            #max_sum = value['sum']

    top = []
    for i in range(1, len(dict_dea.keys())):
        top.append(i)
    coeff_weight = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    
    dict_people = {}
    for key, value in dict_dea.items():
        dict_people[key] = 0
    for key, value in dict_equality.items():
        for line in value['lines']:                    
            dict_people[line] += value['sum']
            
    for i in top:
        for j in coeff_weight:
            outputFileName = output_path + outputExcel + "_top_" + str(i) + "_operational_efficiency_weight_" + str(j) + ".xls"
            #excelHead = ["Bus Line", "Coeff Weight", "Equality Weight", "Grade", "Total Coefficient", "Total Population Served"]
            excelHead = ["Bus Line", "Disadvantaged Population Served", "Operational Efficiency Score"]
            file, table = fh.excelWritableCreate("result")
            for k in range (0,len(excelHead)):
                fh.excelWritableCell(table, 0, k, excelHead[k])
        
            #fix rank problem
            XSol, Z1, Z2, Z3 = glpkSolve(output_path + "glpk_result_remain_" + str(i) + "_weight_operational_efficiency_" + str(j) + ".txt")
            if (1.0 == j):
                for key, value in dict_equality.items():
                    for line in value['lines']:
                        if ((line) in XSol):
                            Z3 += value['sum']
                            break;            
        

            row = 1
            total_coeff = Z1
            total_people = Z3
            for e in XSol:
                fh.excelWritableCell(table, row, 0, e)
                #fh.excelWritableCell(table, row, 1, str(j))
                #fh.excelWritableCell(table, row, 2, str("%.2f" % (1 - j)))
                fh.excelWritableCell(table, row, 1, str("%.2f " % (dict_people[e])))
                fh.excelWritableCell(table, row, 2, str("%.4f " % (dict_dea[e])))
                row += 1
            
            # write the excel again for total coeff and total served people
            #row = 1
            row += 1
            #for row in range (1, cnt + 1):
            fh.excelWritableCell(table, row, 0, str("Total Operational Efficiency Score"))
            fh.excelWritableCell(table, row, 1, str("%.2f" % total_coeff))
            row += 1
            fh.excelWritableCell(table, row, 0, str("Total Disadvantaged Population Served"))
            fh.excelWritableCell(table, row, 1, str("%.2f" % total_people))

            print outputFileName
            fh.excelWritableSave(file, outputFileName)
    
if __name__ == '__main__':
    if(platform.system() == sys_windows):
        inputCal = inputCal.replace("/", "\\")
        inputDea = inputDea.replace("/", "\\")
        outputPath.replace("/", "\\")

    cal_rank(inputCal, inputDea, outputPath)