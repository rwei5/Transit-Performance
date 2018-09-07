# ##################################################################################
# Project               Bus Line Analysis
# (c) copyright         2016
# Orgnization           University of Utah
#
# @file                 launchBusAnalysis.py
# Description           Launch the whole project, GUI part
# Author                Yongjian Mu
# Date                  2/13/2017
# ##################################################################################

from Tkinter import *
import tkFileDialog as filedialog
import ttk
import tkMessageBox

import os, platform, sys
import thread
import json
import xlrd
from osgeo import ogr

from cal_equality import CalEquality
import DEAadapter as da
import cal_glpk as cg
import cal_rank as cr
import geoRender as gr
import fileHandler as fh

sys_windows = "Windows"

FRAME_START_X =                 50
FRAME_START_Y =                 50
FRAME_Width =                   1440
FRAME_Height =                  600

inputEqu = "cal_equality.csv and cal_equality.json"
inputDEA = "cal_dea.csv and cal_dea.json"
outputRet = "glpk_result"
outputPath = "../output"
outputRankPath = "../output/rank/"
shpBlckPath = "..\\input\\Utah_blck_grp\\UT_blck_grp_2010.shp"
shpBusRoutes = "..\\input\\BusRoutes_UTA\\BusRoutes_UTA.shp"

str_dea_excel_busline = ""
set_dea_excel_input = set()
set_dea_excel_output = set()
str_equ_busRoutes_shp_bus_id = ""
#str_equ_blck_shp_blck_id = ""
str_equ_blck_shp_population_id = ""
str_equ_stop_shp_stop_id = ""

# function
def _btn_equ_busStop_shp_input_action():
    filename = filedialog.askopenfilename()
    var_equ_busStop_shp_input.set(filename)

def _btn_equ_block_shp_input_action():
    filename = filedialog.askopenfilename()
    var_equ_block_shp_input.set(filename)

def _btn_equ_busRoutes_shp_input_action():
    filename = filedialog.askopenfilename()
    var_equ_busRoutes_shp_input.set(filename)

def _btn_equ_stops_txt_input_action():
    filename = filedialog.askopenfilename()
    var_equ_stops_txt_input.set(filename)

def _btn_equ_stops_times_txt_input_action():
    filename = filedialog.askopenfilename()
    var_equ_stops_times_txt_input.set(filename)

def _btn_equ_trips_txt_input_action():
    filename = filedialog.askopenfilename()
    var_equ_trips_txt_input.set(filename)

def _btn_output_path_input_action():
    dirname = filedialog.askdirectory()
    if (0 < len(dirname)):
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        if (platform.system() == sys_windows):
            dirname = dirname.replace("/", "\\")
            dirname += "\\"
        else:
            dirname += "/"
    var_output_path_input.set(dirname)

def _btn_output_rank_input_action():
    dirname = filedialog.askdirectory()
    if(0 < len(dirname)):
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        if (platform.system() == sys_windows):
            dirname = dirname.replace("/", "\\")
            dirname += "\\"
        else:
            dirname += "/"
    var_output_rank_input.set(dirname)

'''
def _btn_dea_runcut_input_action():
    filename = filedialog.askopenfilename()
    var_dea_runcut_input.set(filename)

def _btn_dea_stop_input_action():
    filename = filedialog.askopenfilename()
    var_dea_stop_input.set(filename)
'''

def _equ_popup_window_thread(argArray, var_equ_popup):
    cal = CalEquality(argArray[0], argArray[1], argArray[2], argArray[3], argArray[4], argArray[5], argArray[6], argArray[7])
    cal.calculate(var_output_path_input.get(), str_equ_blck_shp_population_id, argArray[8])
    # display results
    var_equ_popup.set("Output file generated in : " + var_output_path_input.get() + inputEqu)

def _equ_popup_window(stops_txt, stops_time_txt, trips_txt, busStop, block, busRoutes, stop_id, route_id, method):
    top = Toplevel()
    top.geometry(str(FRAME_Width / 2) + "x" + str(FRAME_Height))
    var_equ_popup = StringVar()
    var_equ_popup.set('Calculating Equality...It may take a long while, please wait...')
    label_equ_status = Label(top, textvariable = var_equ_popup)
    label_equ_status.grid(sticky = 'w', row = 0, column = 0)
    argArray = [stops_txt, stops_time_txt, trips_txt, busStop, block, busRoutes, stop_id, route_id, method]
    thread.start_new_thread(_equ_popup_window_thread, (argArray, var_equ_popup,))

def _btn_cal_equality_action(method):
    check_flag = True
    if(0 == len(var_equ_stops_txt_input.get())):
        check_flag = False
    if(0 == len(var_equ_stops_times_txt_input.get())):
        check_flag = False
    if(0 == len(var_equ_trips_txt_input.get())):
        check_flag = False
    if(0 == len(var_equ_busStop_shp_input.get())):
        check_flag = False
    if(0 == len(var_equ_block_shp_input.get())):
        check_flag = False
    if(0 == len(var_equ_busRoutes_shp_input.get())):
        check_flag = False
    if(0 == len(var_output_path_input.get())):
        check_flag = False
    if(0 == len(str_equ_busRoutes_shp_bus_id)):
        check_flag = False
    if(0 == len(str_equ_stop_shp_stop_id)):
        check_flag = False

    if check_flag == False:
        tkMessageBox.showwarning( "Input file missing", "Please fill item 1 ~ 10")
        return

    _equ_popup_window(var_equ_stops_txt_input.get(), var_equ_stops_times_txt_input.get(), var_equ_trips_txt_input.get(), var_equ_busStop_shp_input.get(), var_equ_block_shp_input.get(), var_equ_busRoutes_shp_input.get(), str_equ_stop_shp_stop_id, str_equ_busRoutes_shp_bus_id, method)

def _dea_popup_window_thread(argArray, var_dea_popup):
    da.calDEA(var_dea_excel_input.get(), argArray[0], argArray[1], argArray[2], argArray[3])
    # display results
    var_dea_popup.set("Output file " + inputDEA + " has generated in " + var_output_path_input.get())

def _dea_popup_window(_busline, _input, _output, _outputpath):
    top = Toplevel()
    top.geometry(str(FRAME_Width / 2) + "x" + str(FRAME_Height))
    var_dea_popup = StringVar()
    var_dea_popup.set('Calculating DEA...please wait...')
    label_dea_status = Label(top, textvariable = var_dea_popup)
    label_dea_status.grid(sticky = 'w', row = 0, column = 0)
    argArray = [_outputpath, _busline, _input, _output]
    thread.start_new_thread(_dea_popup_window_thread, (argArray, var_dea_popup,))


def _btn_cal_dea_action():
    print "str_dea_excel_busline", str_dea_excel_busline
    check_flag = True
    if(0 == var_output_path_input.get()):
        check_flag = False
    if(0 == var_dea_excel_input.get()):
        check_flag = False
    if(0 == len(str_dea_excel_busline)):
        check_flag = False
    if(0 == len(set_dea_excel_input)):
        check_flag = False
    if(0 == len(set_dea_excel_output)):
        check_flag = False

    if check_flag == False:
        tkMessageBox.showwarning("Some requirements are missing\n", "Please check item xxx")
        return

    _dea_popup_window(str_dea_excel_busline, set_dea_excel_input, set_dea_excel_output, var_output_path_input.get())

def _btn_textbox_update(event, combobox):
    remain_busline_num = combobox.get()
    root = Toplevel()
    root.geometry(str(FRAME_Width) + "x" + str(FRAME_Height))
    top = Canvas(root, bg='White')
    top.pack(expand=YES, fill=BOTH)

    # Create instruction
    top.create_text(200, 200, font=("courier", 14), text="Instruction:", fill = 'red')
    top.create_text(300, 300, font=("courier", 12), text="Please Click the red circle \nto see the detailed information. \nAfter clicking the circle, \nplease wait until the chart appeared. \nDo not click again before the chart appeared.")

    # open files to get max and min coeff / population
    coeff_min = sys.float_info.max
    coeff_max = sys.float_info.min
    population_min = sys.maxint
    population_max = 0

    coeff_set = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    for k in coeff_set:
        parse_file = var_output_rank_input.get() + "rank_excel_top_" + str(remain_busline_num) + "_operational_efficiency_weight_" + str(k) + ".xls"
        data = fh.parseInputFile(parse_file)
        table = data.sheets()[0]
        nrows = table.nrows
        cols = table.ncols
        if(nrows <= 1):
            continue
        coeff_min = min(coeff_min, float(table.cell(nrows - 2, 1).value))
        coeff_max = max(coeff_max, float(table.cell(nrows - 2, 1).value))
        population_min = min(population_min, float(table.cell(nrows - 1, 1).value))
        population_max = max(population_max, float(table.cell(nrows - 1, 1).value))

    # define circle button
    def _create_circle(self, x, y, r, **kwargs):
        return self.create_oval(x - r, y - r, x + r, y + r, **kwargs)

    Canvas.create_circle = _create_circle

    def onObjectClick(event, bus_line):
        print 'Got object click, bus line set = ', bus_line_set
        gr.drawMapView(var_equ_block_shp_input.get(), var_equ_busRoutes_shp_input.get(), bus_line, str_equ_blck_shp_population_id, str_equ_busRoutes_shp_bus_id)

    # draw coordinate
    x_x0, x_x1, x_y1, x_y2 = (1250, 460, 620, 460)
    y_x0, y_x1, y_y1, y_y2 = (620, 25, 620, 460)

    x_line = top.create_line(
        (x_x0, x_x1, x_y1, x_y2),
        arrow='first',
        arrowshape='8 10 3',
        joinstyle='miter',
    )

    y_line = top.create_line(
        (y_x0, y_x1, y_y1, y_y2),
        arrow='first',
        arrowshape='8 10 3',
        joinstyle='miter',
    )
    b = 11
    top.create_text(x_x1, y_y1 - 600, text='Total Operational Efficiency Score')
    population_step = (population_max - population_min) / 10.0
    for i in range(1, b + 1):
        x_x1 -= 40
        x_y2 -= 40
        if(i < b):
            top.create_line((x_x0 - 40, x_x1, x_y1, x_y2), dash=3, fill='gray')
        if(i % 2 == 1):
            top.create_text(x_x1 + 610, y_y1 - 600, text="%.2f" % ((b - i) * population_step + population_min))

    a = 11
    top.create_text(x_x1 - 30 + 950, y_y1 - 150, text='Total Disadvantaged Population Served')
    coeff_step = (coeff_max - coeff_min) / 10.0
    btn_circle = list(range(12))
    y_temp = y_y1
    for i in range(1, a + 1):
        y_x0 += 40
        y_y1 += 40
        '''
        print '-------------------------------'
        print 'Coordinate : [%d] '% i
        print '    x_x1 =  %s , x_y2 =  %s ' %(x_x1,x_y2)
        print '-------------------------------'
        '''
        if(i < a):
            top.create_line((y_x0, y_x1 + 20, y_y1, y_y2), dash=3, fill='gray')

        top.create_text(x_x1 - 30 + 580, y_y1 - 600, text="%.2f" % ((a - i) * coeff_step + coeff_min))

    # draw circle
    btn_cnt = 0
    last_coeff = -1.0
    last_population = -1.0
    for k in coeff_set:
        parse_file = var_output_rank_input.get() + "rank_excel_top_" + str(remain_busline_num) + "_operational_efficiency_weight_" + str(k) + ".xls"
        data = fh.parseInputFile(parse_file)
        table = data.sheets()[0]
        nrows = table.nrows
        cols = table.ncols
        if (nrows <= 1):
            continue
        coeff_cur = float(table.cell(nrows - 2, 1).value)
        population_cur = float(table.cell(nrows - 1, 1).value)

        if(coeff_cur == last_coeff and population_cur == last_population):
            continue
        bus_line_set = set('')
        bus_cnt = 1
        while (bus_cnt < nrows - 3):
            bus_line_set.add(str(table.cell(bus_cnt, 0).value))
            bus_cnt += 1

        #btn_circle[btn_cnt] = top.create_circle(x_x1 + 600, y_temp - 560, 5, fill="red", outline="#DDD", width=1)
        btn_circle[btn_cnt] = top.create_circle(x_x1 + 600 + (population_cur - population_min) / population_step * 40, y_temp - 560 + (coeff_cur - coeff_min) / coeff_step * 40, 5, fill="red", outline="#DDD", width=1)
        top.tag_bind(btn_circle[btn_cnt], '<ButtonPress-1>', lambda event, arg = bus_line_set: onObjectClick(event, arg))
        btn_cnt += 1

def _optimize_thread(label):
    cg.getResults(var_opt_equ_input.get(), var_opt_dea_input.get(), var_output_path_input.get(), var_glpsol_input.get())
    cr.cal_rank(var_opt_equ_input.get(), var_opt_dea_input.get(), var_output_rank_input.get())
    label.set("Optimization finished, you can click the combobox now.")

def _btn_optimization(flag):
    print("optimization......")
    check_flag = True
    if flag == True:
        if(0 == len(var_equ_busRoutes_shp_input.get())):
            check_flag = False
        if(0 == len(var_equ_block_shp_input.get())):
            check_flag = False
        if (0 == len(var_opt_equ_input.get())):
            check_flag = False
        if(0 == len(var_opt_dea_input.get())):
            check_flag = False
        if(0 == len(var_output_path_input.get())):
            check_flag = False
        if(0 == len(var_glpsol_input.get())):
            check_flag = False
        if(0 == len(var_output_rank_input.get())):
            check_flag = False

        if check_flag == False:
            tkMessageBox.showwarning("Input file missing", "Please fill item 2, 3, 7, 11, 13 ~ 15")
            return
    else:
        if (0 == len(var_equ_busRoutes_shp_input.get())):
            check_flag = False
        if (0 == len(var_equ_block_shp_input.get())):
            check_flag = False
        if (0 == len(var_opt_dea_input.get())):
            check_flag = False
        if (0 == len(var_output_path_input.get())):
            check_flag = False
        if (0 == len(var_output_rank_input.get())):
            check_flag = False

        if check_flag == False:
            tkMessageBox.showwarning("Input file missing", "Please fill item 2, 3, 7, 13, 15")
            return

    root = Toplevel()
    root.geometry(str(FRAME_Width / 2) + "x" + str(FRAME_Height))
    top = Canvas(root, bg = 'White')
    top.pack(expand=YES, fill=BOTH)

    var_optimization_label = StringVar()
    check_flag = True
    if flag == True:
        var_optimization_label.set('Optimizing...Please Wait...Do NOT click the combobox!!!')
    else:
        var_optimization_label.set('Optimization finished, you can click the combobox now.')
    label_opt_status = Label(top, textvariable = var_optimization_label)
    label_opt_status.grid(sticky = 'w', row = 0, column = 0)

    var_choose_remain = StringVar()
    var_choose_remain.set('Please choose remaining number of bus line')
    label_choose_remain = Label(top, textvariable = var_choose_remain)
    label_choose_remain.grid(sticky = 'w', row = 1, column = 0)

    # read json file
    with open(var_opt_dea_input.get()) as f:
        dict_dea = json.load(f)

    # init combobox
    number = StringVar()
    numberChosen = ttk.Combobox(top, width = 4, textvariable = number)
    numList = []
    for i in range (1, len(dict_dea) + 1):
        numList.append(i)
    numberChosen['values'] = numList
    print numberChosen['values']
    numberChosen.grid(column = 1, row = 1)
    numberChosen.current(0)
    numberChosen.bind('<<ComboboxSelected>>', lambda event, combobox = numberChosen : _btn_textbox_update(event, combobox))

    # start thread to cal optimization and rank
    if flag == True:
        # check if data is consistency
        consistency_flag = True
        with open(var_opt_equ_input.get()) as f:
            dict_equality = json.load(f)
        with open(var_opt_dea_input.get()) as f:
            dict_dea = json.load(f)

        set_equ = set()
        for key, value in dict_equality.items():
            if (False == consistency_flag):
                break
            for line in value['lines']:
                set_equ.add(line)
                if(line not in dict_dea):
                    consistency_flag = False
                    print "Error on line: {}".format(line)
                    break

        if(len(set_equ) != len(dict_dea)):
            print "Dict data length different"
            for key1, value1 in dict_dea.items():
                if key1 not in set_equ:
                    print key1
            consistency_flag = False

        if(False == consistency_flag):
            tkMessageBox.showwarning("Error", "The data of Equality are not the same as Operational Efficiency")
            return
        thread.start_new_thread(_optimize_thread, (var_optimization_label,))



def _btn_opt_equ_input_action():
    filename = filedialog.askopenfilename()
    var_opt_equ_input.set(filename)

def _btn_opt_dea_input_action():
    filename = filedialog.askopenfilename()
    var_opt_dea_input.set(filename)

def _bnt_glpsol_input_action():
    filename = filedialog.askopenfilename()
    var_glpsol_input.set(filename)

def _btn_dea_excel_input_action():
    filename = filedialog.askopenfilename()
    var_dea_excel_input.set(filename)

def _btn_dea_excel_setting_action():
    if(0 == len(var_dea_excel_input.get())):
        tkMessageBox.showwarning("Error", "Please choose you DEA input excel file")
        return
    data = fh.parseInputFile(var_dea_excel_input.get())
    table = data.sheets()[0]
    nrows = table.nrows
    ncols = table.ncols

    # check data validation
    if(1 >= nrows or 2 >= ncols):
        tkMessageBox.showwarning("Error", "DEA input excel file is invalid")
        return
    colcnt = 0
    input_fields = []
    while(colcnt < ncols):
        input_fields.append(str(table.cell(0, colcnt).value))
        colcnt += 1

    dea_excel_setting_root = Toplevel()
    dea_excel_setting_root.geometry(str(FRAME_Width / 2) + "x" + str(FRAME_Height))
    dea_excel_setting_root.configure(background='White')

    frame_col = 0
    # put busline frame
    busline_frame = LabelFrame(dea_excel_setting_root, text="Select busline field", padx=10, pady=10, width=100, height=100, background='white')
    busline_frame.grid(sticky='n', row=0, column=frame_col)
    frame_col += 1

    dea_busline_lb = Listbox(busline_frame, selectmode = SINGLE)
    for item in input_fields:
        dea_busline_lb.insert(END, item)
    dea_busline_lb.pack()

    def _btn_dea_busline_add_action():
        global str_dea_excel_busline
        for b in dea_busline_lb.curselection():
            str_dea_excel_busline = dea_busline_lb.get(b)
        print str_dea_excel_busline

    btn_dea_busline_add = Button(busline_frame, text='Set', command = _btn_dea_busline_add_action)
    btn_dea_busline_add.pack()

    # put input frame
    input_frame = LabelFrame(dea_excel_setting_root, text="Select input field(s)", padx=10, pady=10, width=100, height=100,
                               background='white')
    input_frame.grid(sticky='n', row=0, column=frame_col)
    frame_col += 1

    dea_input_lb = Listbox(input_frame, selectmode=MULTIPLE)
    for item in input_fields:
        dea_input_lb.insert(END, item)
    dea_input_lb.pack()

    def _btn_dea_input_add_action():
        global set_dea_excel_input
        set_dea_excel_input.clear()
        for b in dea_input_lb.curselection():
            set_dea_excel_input.add(dea_input_lb.get(b))
        print set_dea_excel_input

    btn_dea_input_add = Button(input_frame, text='Set', command = _btn_dea_input_add_action)
    btn_dea_input_add.pack()

    # put output frame
    output_frame = LabelFrame(dea_excel_setting_root, text="Select output field(s)", padx=10, pady=10, width=100, height=100,
                             background='white')
    output_frame.grid(sticky='n', row=0, column=frame_col)
    frame_col += 1

    dea_output_lb = Listbox(output_frame, selectmode=MULTIPLE)
    for item in input_fields:
        dea_output_lb.insert(END, item)
    dea_output_lb.pack()

    def _btn_dea_output_add_action():
        global set_dea_excel_output
        set_dea_excel_output.clear()
        for b in dea_output_lb.curselection():
            set_dea_excel_output.add(dea_output_lb.get(b))
        print set_dea_excel_output

    btn_dea_output_add = Button(output_frame, text='Set', command = _btn_dea_output_add_action)
    btn_dea_output_add.pack()

    # the Done button
    def _btn_done():
        dea_excel_setting_root.destroy()

    btn_dea_excel_setting_done = Button(dea_excel_setting_root, text='Done', command = _btn_done)
    btn_dea_excel_setting_done.grid(sticky='w', row= 2, column= 2)


def _btn_equ_busRoutes_setting_action():
    if(0 == len(var_equ_busRoutes_shp_input.get())):
        tkMessageBox.showwarning("Error", "Equality input bus routes shp file is invalid")
        return

    # get features from shp file
    field_name_list = []
    ds_blck1 = ogr.Open(var_equ_busRoutes_shp_input.get(), 0)
    # nlay_blck1 = ds_blck1.GetLayerCount()
    lyr_blck1 = ds_blck1.GetLayer(0)
    layerDefinition = lyr_blck1.GetLayerDefn()
    for i in range(layerDefinition.GetFieldCount()):
        field_name_list.append(layerDefinition.GetFieldDefn(i).GetName())

    # window
    equ_busRoutes_setting_root = Toplevel()
    equ_busRoutes_setting_root.geometry(str(FRAME_Width / 2) + "x" + str(FRAME_Height))
    equ_busRoutes_setting_root.configure(background='White')

    frame_col = 0
    # put busline frame
    busline_frame = LabelFrame(equ_busRoutes_setting_root, text="Select busline field", padx=10, pady=10, width=100,
                               height=100, background='white')
    busline_frame.grid(sticky='n', row=0, column=frame_col)
    frame_col += 1

    equ_busRoutes_bus_id_lb = Listbox(busline_frame, selectmode=SINGLE)
    for item in field_name_list:
        equ_busRoutes_bus_id_lb.insert(END, item)
    equ_busRoutes_bus_id_lb.pack()

    def _btn_equ_busRoutes_add_action():
        global str_equ_busRoutes_shp_bus_id
        for b in equ_busRoutes_bus_id_lb.curselection():
            str_equ_busRoutes_shp_bus_id = equ_busRoutes_bus_id_lb.get(b)
        print str_equ_busRoutes_shp_bus_id

    btn_equ_input_add = Button(busline_frame, text='Set', command = _btn_equ_busRoutes_add_action)
    btn_equ_input_add.pack()

    # Done button
    def _btn_done():
        equ_busRoutes_setting_root.destroy()

    btn_equ_busRoutes_setting_done = Button(equ_busRoutes_setting_root, text='Done', command=_btn_done)
    btn_equ_busRoutes_setting_done.grid(sticky='w', row=1, column=1)

def _btn_equ_block_setting_action():
    if(0 == len(var_equ_block_shp_input.get())):
        tkMessageBox.showwarning("Error", "Equality input bus block shp file is invalid")
        return

    # get features from shp file
    field_name_list = []
    ds_blck1 = ogr.Open(var_equ_block_shp_input.get(), 0)
    # nlay_blck1 = ds_blck1.GetLayerCount()
    lyr_blck1 = ds_blck1.GetLayer(0)
    layerDefinition = lyr_blck1.GetLayerDefn()
    for i in range(layerDefinition.GetFieldCount()):
        field_name_list.append(layerDefinition.GetFieldDefn(i).GetName())

    # window
    equ_block_setting_root = Toplevel()
    equ_block_setting_root.geometry(str(FRAME_Width / 2) + "x" + str(FRAME_Height))
    equ_block_setting_root.configure(background='White')

    frame_col = 0
    # put population frame
    popuplation_frame = LabelFrame(equ_block_setting_root, text="Select served population field", padx=10, pady=10, width=100,
                               height=100, background='white')
    popuplation_frame.grid(sticky='n', row=0, column=frame_col)
    frame_col += 1

    equ_block_served_poplation_id_lb = Listbox(popuplation_frame, selectmode=SINGLE)
    for item in field_name_list:
        equ_block_served_poplation_id_lb.insert(END, item)
    equ_block_served_poplation_id_lb.pack()

    def _btn_equ_block_pop_add_action():
        global str_equ_blck_shp_population_id
        for b in equ_block_served_poplation_id_lb.curselection():
            str_equ_blck_shp_population_id = equ_block_served_poplation_id_lb.get(b)
        print str_equ_blck_shp_population_id

    btn_equ_input_pop_add = Button(popuplation_frame, text='Set', command = _btn_equ_block_pop_add_action)
    btn_equ_input_pop_add.pack()

    # put blck id frame
    '''
    block_frame = LabelFrame(equ_block_setting_root, text="Select block id field", padx=10, pady=10,
                                   width=100,
                                   height=100, background='white')
    block_frame.grid(sticky='n', row=0, column=frame_col)
    frame_col += 1

    equ_block_id_lb = Listbox(block_frame, selectmode=SINGLE)
    for item in field_name_list:
        equ_block_id_lb.insert(END, item)
    equ_block_id_lb.pack()

    def _btn_equ_block_id_add_action():
        global str_equ_blck_shp_blck_id
        for b in equ_block_id_lb.curselection():
            str_equ_blck_shp_blck_id = equ_block_id_lb.get(b)
        print str_equ_blck_shp_blck_id

    btn_equ_input_blck_add = Button(block_frame, text='Set', command=_btn_equ_block_id_add_action)
    btn_equ_input_blck_add.pack()
    '''

    # Done button
    def _btn_done():
        equ_block_setting_root.destroy()

    btn_equ_block_setting_done = Button(equ_block_setting_root, text='Done', command=_btn_done)
    btn_equ_block_setting_done.grid(sticky='w', row=1, column=1)


def _btn_equ_busStop_setting_action():
    if(0 == len(var_equ_busStop_shp_input.get())):
        tkMessageBox.showwarning("Error", "Equality input bus stop shp file is invalid")
        return

    # get features from shp file
    field_name_list = []
    ds_blck1 = ogr.Open(var_equ_busStop_shp_input.get(), 0)
    # nlay_blck1 = ds_blck1.GetLayerCount()
    lyr_blck1 = ds_blck1.GetLayer(0)
    layerDefinition = lyr_blck1.GetLayerDefn()
    for i in range(layerDefinition.GetFieldCount()):
        field_name_list.append(layerDefinition.GetFieldDefn(i).GetName())

    # window
    equ_busStop_setting_root = Toplevel()
    equ_busStop_setting_root.geometry(str(FRAME_Width / 2) + "x" + str(FRAME_Height))
    equ_busStop_setting_root.configure(background='White')

    frame_col = 0
    # put population frame
    stop_frame = LabelFrame(equ_busStop_setting_root, text="Select stop id field", padx=10, pady=10, width=100,
                               height=100, background='white')
    stop_frame.grid(sticky='n', row=0, column=frame_col)
    frame_col += 1

    equ_stop_id_lb = Listbox(stop_frame, selectmode=SINGLE)
    for item in field_name_list:
        equ_stop_id_lb.insert(END, item)
    equ_stop_id_lb.pack()

    def _btn_equ_stop_add_action():
        global str_equ_stop_shp_stop_id
        for b in equ_stop_id_lb.curselection():
            str_equ_stop_shp_stop_id = equ_stop_id_lb.get(b)
        print str_equ_stop_shp_stop_id

    btn_equ_input_stop_add = Button(stop_frame, text='Set', command = _btn_equ_stop_add_action)
    btn_equ_input_stop_add.pack()

    # Done button
    def _btn_done():
        equ_busStop_setting_root.destroy()

    btn_equ_block_setting_done = Button(equ_busStop_setting_root, text='Done', command=_btn_done)
    btn_equ_block_setting_done.grid(sticky='w', row=1, column=1)


# main()
if(platform.system() == sys_windows):
    outputPath = outputPath.replace("/", "\\")
    outputRankPath = outputRankPath.replace("/", "\\")


root = Tk()  
root.title('Bus Line Performance Analysis')
root.geometry(str(FRAME_Width) + "x" + str(FRAME_Height) + "+" + str(FRAME_START_X) + "+" + str(FRAME_START_Y))
root.configure(background = 'White')
root.resizable(width=True, height=True)

equality_row = 0

# put labelframe
equ_frame = LabelFrame(root, text="Equality Group", padx=10, pady=10, width=100, height=100, background = 'white')
equ_frame.grid(sticky = 'n', row=equality_row, column=0)
equality_row += 1

# Equality bus stop input shape file
label_equ_busStop_shp_input = Label(equ_frame, text = 'Please choose the equality bus stop input shape file', background = 'light sky blue').grid(sticky = 'w', row = equality_row, column = 0)
btn_equ_busStop_shp_input = Button(equ_frame, text = '1. Browser', command = _btn_equ_busStop_shp_input_action)
btn_equ_busStop_shp_input.grid(sticky = 'w', row = equality_row, column = 1)
var_equ_busStop_shp_input = StringVar()
label_equ_busStop_shp_display = Label(equ_frame, textvariable = var_equ_busStop_shp_input, width = 40, anchor = E)
label_equ_busStop_shp_display.grid(sticky = 'w', row = equality_row + 1, column = 0)
btn_equ_busStop_shp_setting = Button(equ_frame, text = '2. Setting', command = _btn_equ_busStop_setting_action)
btn_equ_busStop_shp_setting.grid(sticky = 'w', row = equality_row + 1, column = 1)
equality_row += 2

# Equality block input shape file
label_equ_block_shp_input = Label(equ_frame, text = 'Please choose the equality block input shape file', background = 'light sky blue').grid(sticky = 'w', row = equality_row, column = 0)
btn_equ_block_shp_input = Button(equ_frame, text = '3. Browser', command = _btn_equ_block_shp_input_action)
btn_equ_block_shp_input.grid(sticky = 'w', row = equality_row, column = 1)
var_equ_block_shp_input = StringVar()
label_equ_block_shp_display = Label(equ_frame, textvariable = var_equ_block_shp_input, width = 40, anchor = E)
label_equ_block_shp_display.grid(sticky = 'w', row = equality_row + 1, column = 0)
btn_equ_block_shp_setting = Button(equ_frame, text = '4. Setting', command = _btn_equ_block_setting_action)
btn_equ_block_shp_setting.grid(sticky = 'w', row = equality_row + 1, column = 1)
equality_row += 2

# Equality bus routes input shape file
label_equ_busRoutes_shp_input = Label(equ_frame, text = 'Please choose the equality bus routes input shape file', background = 'light sky blue').grid(sticky = 'w', row = equality_row, column = 0)
btn_equ_busRoutes_shp_input = Button(equ_frame, text = '5. Browser', command = _btn_equ_busRoutes_shp_input_action)
btn_equ_busRoutes_shp_input.grid(sticky = 'w', row = equality_row, column = 1)
var_equ_busRoutes_shp_input = StringVar()
label_equ_busRoutes_shp_display = Label(equ_frame, textvariable = var_equ_busRoutes_shp_input, width = 40, anchor = E)
label_equ_busRoutes_shp_display.grid(sticky = 'w', row = equality_row + 1, column = 0)
btn_equ_busRoutes_shp_setting = Button(equ_frame, text = '6. Setting', command = _btn_equ_busRoutes_setting_action)
btn_equ_busRoutes_shp_setting.grid(sticky = 'w', row = equality_row + 1, column = 1)
equality_row += 2

# Equality stops input txt file
label_equ_stops_txt_input = Label(equ_frame, text = 'Please choose the equality GTFS routes input txt file', background = 'light sky blue').grid(sticky = 'w', row = equality_row, column = 0)
btn_equ_stops_txt_input = Button(equ_frame, text = '7. Browser', command = _btn_equ_stops_txt_input_action)
btn_equ_stops_txt_input.grid(sticky = 'w', row = equality_row, column = 1)
var_equ_stops_txt_input = StringVar()
label_equ_stops_txt_display = Label(equ_frame, textvariable = var_equ_stops_txt_input, width = 40, anchor = E)
label_equ_stops_txt_display.grid(sticky = 'w', row = equality_row + 1, column = 0)
equality_row += 2

# Equality stops times input txt file
label_equ_stops_times_txt_input = Label(equ_frame, text = 'Please choose the equality GTFS stops times input txt file', background = 'light sky blue').grid(sticky = 'w', row = equality_row, column = 0)
btn_equ_stops_times_txt_input = Button(equ_frame, text = '8. Browser', command = _btn_equ_stops_times_txt_input_action)
btn_equ_stops_times_txt_input.grid(sticky = 'w', row = equality_row, column = 1)
var_equ_stops_times_txt_input = StringVar()
label_equ_stops_times_txt_display = Label(equ_frame, textvariable = var_equ_stops_times_txt_input, width = 40, anchor = E)
label_equ_stops_times_txt_display.grid(sticky = 'w', row = equality_row + 1, column = 0)
equality_row += 2

# Equality trips input txt file
label_equ_trips_txt_input = Label(equ_frame, text = 'Please choose the equality GTFS trips input txt file', background = 'light sky blue').grid(sticky = 'w', row = equality_row, column = 0)
btn_equ_trips_txt_input = Button(equ_frame, text = '9. Browser', command = _btn_equ_trips_txt_input_action)
btn_equ_trips_txt_input.grid(sticky = 'w', row = equality_row, column = 1)
var_equ_trips_txt_input = StringVar()
label_equ_trips_txt_display = Label(equ_frame, textvariable = var_equ_trips_txt_input, width = 40, anchor = E)
label_equ_trips_txt_display.grid(sticky = 'w', row = equality_row + 1, column = 0)
equality_row += 2

# Output file directory
label_output_path_input = Label(equ_frame, text = 'Please choose the output directory', background = 'light sky blue').grid(sticky = 'w', row = equality_row, column = 0)
btn_output_path_input = Button(equ_frame, text = '10. Browser', command = _btn_output_path_input_action)
btn_output_path_input.grid(sticky = 'w', row = equality_row, column = 1)
var_output_path_input = StringVar()
label_output_path_display = Label(equ_frame, textvariable = var_output_path_input, width = 40, anchor = E)
label_output_path_display.grid(sticky = 'w', row = equality_row + 1, column = 0)
equality_row += 2

# Generate equality results button
label_cal_equality = Label(equ_frame, text = 'Calculate Spatial Equality. Require: 1 ~ 10', background = 'light sky blue').grid(sticky = 'w', row = equality_row, column = 0)
equality_row += 1
btn_cal_equality_overlap = Button(equ_frame, text = 'Calculate Overlap', command = lambda : _btn_cal_equality_action("overlap"))
btn_cal_equality_overlap.grid(sticky = 'w', row = equality_row, column = 0)
equality_row += 1
btn_cal_equality_centroid = Button(equ_frame, text = 'Calculate Centroid', command = lambda: _btn_cal_equality_action("centroid"))
btn_cal_equality_centroid.grid(sticky = 'w', row = equality_row, column = 0)
equality_row += 1


# DEA group
dea_row = 0

# put labelframe
dea_frame = LabelFrame(root, text="DEA Group", padx=10, pady=10, width=100, height=100, background = 'white')
dea_frame.grid(sticky = 'n', row=dea_row, column=4)
dea_row += 1

# Optimize equ input
label_dea_excel_input = Label(dea_frame, text = 'Please choose the dea input excel file', background = 'light sky blue').grid(sticky = 'w', row = dea_row, column = 4)
btn_dea_excel_input = Button(dea_frame, text = '11. Browser', command = _btn_dea_excel_input_action)
btn_dea_excel_input.grid(sticky = 'w', row = dea_row, column = 5)
var_dea_excel_input = StringVar()
label_dea_excel_display = Label(dea_frame, textvariable = var_dea_excel_input, width = 40, anchor = E)
label_dea_excel_display.grid(sticky = 'w', row = dea_row + 1, column = 4)
btn_dea_excel_setting = Button(dea_frame, text = '12. Setting', command = _btn_dea_excel_setting_action)
btn_dea_excel_setting.grid(sticky = 'w', row = dea_row + 1, column = 5)
dea_row += 2


# Generate DEA results button
label_cal_dea = Label(dea_frame, text = 'Calculate Operational Efficiency. Require: 10 ~ 12', background = 'light sky blue').grid(sticky = 'w', row = dea_row, column = 4)
dea_row += 1
btn_cal_dea = Button(dea_frame, text = 'Calculate Operational Efficiency', command = _btn_cal_dea_action)
btn_cal_dea.grid(sticky = 'w', row = dea_row, column = 4)
dea_row += 1



# Optimization group
opt_row = 0

# put labelframe
opt_frame = LabelFrame(root, text="Optimization Group", padx=10, pady=10, width=100, height=100, background = 'white')
opt_frame.grid(sticky = 'n', row=opt_row, column=6)
opt_row += 1

# Optimize equ input
label_opt_equ_input = Label(opt_frame, text = 'Please choose the spatial equality json file\n(cal_equality.json)', background = 'light sky blue').grid(sticky = 'w', row = opt_row, column = 6)
btn_opt_equ_input = Button(opt_frame, text = '13. Browser', command = _btn_opt_equ_input_action)
btn_opt_equ_input.grid(sticky = 'w', row = opt_row, column = 7)
var_opt_equ_input = StringVar()
label_opt_equ_display = Label(opt_frame, textvariable = var_opt_equ_input, width = 40, anchor = E)
label_opt_equ_display.grid(sticky = 'w', row = opt_row + 1, column = 6)
opt_row += 2


# Optimize dea input
label_opt_dea_input = Label(opt_frame, text = 'Please choose the operational efficiency dea json file\n(cal_dea.json)', background = 'light sky blue').grid(sticky = 'w', row = opt_row, column = 6)
btn_opt_dea_input = Button(opt_frame, text = '14. Browser', command = _btn_opt_dea_input_action)
btn_opt_dea_input.grid(sticky = 'w', row = opt_row, column = 7)
var_opt_dea_input = StringVar()
label_opt_dea_display = Label(opt_frame, textvariable = var_opt_dea_input, width = 40, anchor = E)
label_opt_dea_display.grid(sticky = 'w', row = opt_row + 1, column = 6)
opt_row += 2

# Optimize dea input
label_glpsol_input = Label(opt_frame, text = 'Please choose the glpsol binary file (glpsol.exe)', background = 'light sky blue').grid(sticky = 'w', row = opt_row, column = 6)
btn_glpsol_input = Button(opt_frame, text = '15. Browser', command = _bnt_glpsol_input_action)
btn_glpsol_input.grid(sticky = 'w', row = opt_row, column = 7)
var_glpsol_input = StringVar()
label_glpsol_display = Label(opt_frame, textvariable = var_glpsol_input, width = 40, anchor = E)
label_glpsol_display.grid(sticky = 'w', row = opt_row + 1, column = 6)
opt_row += 2

# Output rank directory
label_output_rank_input = Label(opt_frame, text = 'Please choose the output rank directory', background = 'light sky blue').grid(sticky = 'w', row = opt_row, column = 6)
btn_output_rank_input = Button(opt_frame, text = '16. Browser', command = _btn_output_rank_input_action)
btn_output_rank_input.grid(sticky = 'w', row = opt_row, column = 7)
var_output_rank_input = StringVar()
label_output_rank_display = Label(opt_frame, textvariable = var_output_rank_input, width = 40, anchor = E)
label_output_rank_display.grid(sticky = 'w', row = opt_row + 1, column = 6)
opt_row += 2

label_do_optimization = Label(opt_frame, text = 'Please click the button below to optimization.\nRequire: 3 ~ 6, 10, 13 ~ 16', background = 'light sky blue').grid(sticky = 'w', row = opt_row, column = 6)
opt_row += 1
btn_optimization = Button(opt_frame, text = 'Do Optimization', command = lambda : _btn_optimization(True))
btn_optimization.grid(sticky = 'w', row = opt_row, column = 6)
opt_row += 1

label_do_optimization = Label(opt_frame, text = 'If already calculated, click "View" button.\nRequire: 3 ~ 6, 10, 13, 14, 16', background = 'light sky blue').grid(sticky = 'w', row = opt_row, column = 6)
opt_row += 1
btn_optimization = Button(opt_frame, text = 'View', command = lambda : _btn_optimization(False))
btn_optimization.grid(sticky = 'w', row = opt_row, column = 6)
opt_row += 1

def shutdownProgram():
    print "Program Quit"
    os.system('TASKKILL /F /IM launchBusAnalysis.exe"')
    root.destroy()
root.protocol('WM_DELETE_WINDOW', shutdownProgram)

root.mainloop()
