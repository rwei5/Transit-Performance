import math
import os, platform, sys
import time
import json
import fileHandler as fh

inputCal = "../output/cal_equality.json"
inputDea = "../output/cal_dea.json"
outputPath = "../output/rank/"
outputExcel = "rank_excel"
sys_windows = "Windows"

def cal_rank(input_cal, input_dea, output_path):
    # Read dict file
    with open(input_cal) as f:
        dict_equality = json.load(f)
    with open(input_dea) as f:
        dict_dea = json.load(f)

    # Standardize equlity, get the max and min value of served population
    min_sum = sys.float_info.max
    max_sum = sys.float_info.min
    for key, value in dict_equality.items():
        if(value['sum'] < min_sum):
            min_sum = value['sum']
        if(value['sum'] > max_sum):
            max_sum = value['sum']

    top = []
    for i in range(1, 95):
        top.append(i)
    coeff_weight = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]
    for i in top:
        for j in coeff_weight:
            outputFileName = output_path + outputExcel + "_top_" + str(i) + "_operational_efficiency_weight_" + str(j) + ".xls"
            #excelHead = ["Bus Line", "Coeff Weight", "Equality Weight", "Grade", "Total Coefficient", "Total Population Served"]
            excelHead = ["Bus Line", "Disadvantaged Population Served"]
            file, table = fh.excelWritableCreate("result")
            for k in range (0,2):
                fh.excelWritableCell(table, 0, k, excelHead[k])
        
            dict_rank = {}
            dict_people = {}
            for key, value in dict_dea.items():
                dict_rank[key] = j * value
                dict_people[key] = 0
            for key, value in dict_equality.items():
                for line in value['lines']:
                    dict_rank[line] +=  (1 - j) * ((value['sum'] - min_sum) / (max_sum - min_sum))
                    dict_people[line] += value['sum']

            l = sorted(dict_rank.items(), key = lambda d:d[1], reverse = True)
            dict_output = []
            for k in l:
                dict_output.append(k)
            print(dict_output)
            row = 1
            cnt = 0
            total_coeff = 0
            last_grade = 0
            dict_bus = set([])
            for e in dict_output:
                if((cnt >= i) and (last_grade > e[1])):
                    break;
                fh.excelWritableCell(table, row, 0, e[0])
                #fh.excelWritableCell(table, row, 1, str(j))
                #fh.excelWritableCell(table, row, 2, str("%.2f" % (1 - j)))
                fh.excelWritableCell(table, row, 1, str("%.2f " % (dict_people[e[0]])))
                total_coeff += dict_dea[e[0]]
                dict_bus.add(e[0])
                cnt += 1
                row += 1
                last_grade = e[1]

            # calculate total served people
            total_people = 0
            for key, value in dict_equality.items():
                for line in value['lines']:
                    if(line in dict_bus):
                        total_people += value['sum']
                        break
            
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