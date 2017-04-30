# ##################################################################################
# Project               Bus Line Analysis
# (c) copyright         2016
# Orgnization           University of Utah
# 
# @file                 model_overlay.py
# Description           Generate of model overlay lp file
# Author                Yongjian Mu
# Date                  12/21/2016
# ##################################################################################

import sys
import os, platform
import json

# import local modules
import fileHandler as fh


# Constant var
inputCal = "../output/cal_equality.json"
inputDEA = "../output/cal_dea.json"
output =                    "model_overlay.lp"
ratio_coeff =               0.5
ratio_equality =            0.5
ratio_percentage =          24

sys_windows =               "Windows"

def mainFunc(r_percentage, r_coeff, r_equality):
    with open(inputCal) as f:
        dict_equality = json.load(f)
    print "Cal Equality Finished\n"

    with open(inputDEA) as f:
        dict_coeff = json.load(f)
    print "DEA Finished\n"
    print dict_coeff

    #dict_equality = {1770: {'sum': 154.0, 'lines': ['205', '200']}, 1771: {'sum': 48.0, 'lines': ['902']}}
    #dict_coeff = {'200': 0.84, '205': 0.5, '902': 1.0}
    len_coeff = len(dict_coeff)
    len_equality = len(dict_equality)

    # open file
    fd = fh.openRegularFile(output)
    
    # 1 write Maximize
    fh.writeRegularFile(fd, "Maximize\n")
    strObj = str(r_coeff) + " Z1 + " + str(r_equality) + " Z2" 
    fh.writeRegularFile(fd, strObj + "\n")
    

    # 2 write subject to
    fh.writeRegularFile(fd, "Subject To\n")
    
    # 2.05 write Z1 Z2 Z3
    # write coeff
    str_coeff = "    "
    cnt = 0
    for key, value in dict_coeff.items():
        str_coeff += str(value) + " " + "X" + str(key)
        if(cnt < len_coeff - 1):
            str_coeff += " + "
        cnt += 1

    # normalize sum
    min_sum = sys.float_info.max
    max_sum = sys.float_info.min
    for key, value in dict_equality.items():
        if(value['sum']< min_sum):
            min_sum = value['sum']
        if(value['sum'] > max_sum):
            max_sum = value['sum']

    # write equality
    cnt = 0
    str_equality = "    "
    str_equality_orig = "   "
    for key, value in dict_equality.items():
        check_flag = True
        for line in value['lines']:
            check = None
            check = dict_coeff.get(line)
            #print(check)
            if(None == check):
                check_flag = False
                break
        if(False == check_flag):
            cnt += 1
            continue
        if(cnt > 0):
            str_equality += " + "
            str_equality_orig += " + "
        str_equality += str((value['sum'] - min_sum) / (max_sum - min_sum)) + " " + "Y" + str(key)
        str_equality_orig += str(value['sum']) + " " + "Y" + str(key)
        cnt += 1

    # write to file
    fh.writeRegularFile(fd, str_coeff + " - Z1 = 0" + "\n")
    fh.writeRegularFile(fd, str_equality + " - Z2 = 0" + "\n")
    fh.writeRegularFile(fd, str_equality_orig + " - Z3 = 0" + "\n")

    # 2.1
    str_coeff = "    "
    cnt = 0
    for key, value in dict_coeff.items():
        str_coeff += "X" + str(key)
        if(cnt < len_coeff - 1):
            str_coeff += " + "
        cnt += 1
    str_coeff += " <= " + str(r_percentage) + "\n"
    fh.writeRegularFile(fd, str_coeff)

    # 2.2
    for key, value in dict_equality.items():
        str_equality = "    "
        cnt_sub = 0
        len_value = len(value['lines'])
        dict_sub = value['lines']
        check_flag = True
        for line in value['lines']:
            check = None
            check = dict_coeff.get(line)
            #print(check)
            if(None == check):
                check_flag = False
                break
            str_equality += "X" + line
            if(cnt_sub < len_value - 1):
                str_equality += " + "
            cnt_sub += 1
        if(False == check_flag):
            continue
        str_equality += " - " + "Y" + str(key) + " >= 0 \n"
        fh.writeRegularFile(fd, str_equality)
    
    # 3 write binary
    # 3.1 bus line
    str_coeff = "    "
    fh.writeRegularFile(fd, "Binary\n")
    for key, value in dict_coeff.items():
        str_coeff += "X" + str(key) + " "

    # 3.2 piece id
    cnt = 0
    for key, value in dict_equality.items():
        check_flag = True
        for line in value['lines']:
            check = None
            check = dict_coeff.get(line)
            #print(check)
            if(None == check):
                check_flag = False
                break
        if(False == check_flag):
            continue
        str_coeff += "Y" + str(key)
        if(cnt < len_equality - 1):
            str_coeff += " "
    str_coeff += "\n"
    fh.writeRegularFile(fd, str_coeff)

    # 4 write End
    fh.writeRegularFile(fd, "End\n")

    # close file
    fh.closeRegularFile(fd)
    print output + " generated successfully\n"

if __name__ == "__main__":
    if(platform.system() == sys_windows):
        inputCal = inputCal.replace("/", "\\")
        inputDEA = inputDEA.replace("/", "\\")
    mainFunc(ratio_percentage, ratio_coeff, ratio_equality)

