from osgeo import ogr
import numpy as np
import matplotlib.path as mpath
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import sys

shpBlckPath = "..\\input\\Utah_blck_grp\\UT_blck_grp_2010.shp"
shpBusRoutes = "..\\input\\BusRoutes_UTA\\BusRoutes_UTA.shp"

def drawMapView(shp_blck_path, shp_bus_routes, bus_line_set, populationf_field, busline_id_field):
    # get max and min population for density
    ds_blck1 = ogr.Open(shp_blck_path, 0)
    #nlay_blck1 = ds_blck1.GetLayerCount()
    lyr_blck1 = ds_blck1.GetLayer(0)
    population_min = sys.maxint
    population_max = 0
    for feat1 in lyr_blck1:
        cur_population = int(feat1.GetField(populationf_field))
        #cur_population += int(feat1.GetField("Age"))
        #cur_population += int(feat1.GetField("Race"))
        #cur_population += int(feat1.GetField("Poverty"))
        #cur_population += int(feat1.GetField("Transporta"))
        #cur_population += int(feat1.GetField("Unemploy"))
        #cur_population += int(feat1.GetField("Disability"))
        population_max = max(cur_population, population_max)
        population_min = min(cur_population, population_min)

    print "max population " + str(population_max)
    print "min population " + str(population_min)


    # Extract first layer of features from shapefile using OGR
    ds_blck = ogr.Open(shp_blck_path, 0)
    #nlay_blck = ds_blck.GetLayerCount()
    lyr_blck = ds_blck.GetLayer(0)

    # Get extent and calculate buffer size
    ext_blck = lyr_blck.GetExtent()
    xoff = (ext_blck[1]-ext_blck[0])/50
    yoff = (ext_blck[3]-ext_blck[2])/50

    # Prepare figure
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlim(ext_blck[0]-xoff,ext_blck[1]+xoff)
    ax.set_ylim(ext_blck[2]-yoff,ext_blck[3]+yoff)

    paths_blck = []
    lyr_blck.ResetReading()
    alpha_blck = []

    # Read all features in layer and store as paths
    for feat in lyr_blck:
        cur_population = int(feat.GetField(populationf_field))
        #cur_population += int(feat.GetField("Age"))
        #cur_population += int(feat.GetField("Race"))
        #cur_population += int(feat.GetField("Poverty"))
        #cur_population += int(feat.GetField("Transporta"))
        #cur_population += int(feat.GetField("Unemploy"))
        #cur_population += int(feat.GetField("Disability"))

        geom = feat.geometry()
        codes = []
        all_x = []
        all_y = []
        for i in range(geom.GetGeometryCount()):
            # Read ring geometry and create path
            r = geom.GetGeometryRef(i)
            x = [r.GetX(j) for j in range(r.GetPointCount())]
            y = [r.GetY(j) for j in range(r.GetPointCount())]
            # skip boundary between individual rings
            codes += [mpath.Path.MOVETO] + (len(x)-1)*[mpath.Path.LINETO]
            all_x += x
            all_y += y
        path = mpath.Path(np.column_stack((all_x,all_y)), codes)
        paths_blck.append(path)
        alpha_blck.append(float(cur_population * 1.00 / population_max))

    # Add paths as patches to axes

    k = 0
    for path in paths_blck:
        patch = mpatches.PathPatch(path, facecolor='blue', edgecolor='blue', alpha = alpha_blck[k])
        ax.add_patch(patch)
        k += 1
    ax.set_aspect(1.0)

    ###############################################
    # Draw bus routes
    ###############################################

    ds_route = ogr.Open(shp_bus_routes, 0)
    #nlay_route = ds_route.GetLayerCount()
    lyr_route = ds_route.GetLayer(0)

    paths_route = []
    lyr_route.ResetReading()

    # Read all features in layer and store as paths
    for feat in lyr_route:
        cur_bus_line =  feat.GetField(busline_id_field)
        if cur_bus_line not in bus_line_set:
            continue
        geom = feat.geometry()
        codes = []
        all_x = []
        all_y = []
        for i in range(geom.GetGeometryCount()):
            # Read ring geometry and create path
            r = geom.GetGeometryRef(i)
            x = [r.GetX(j) for j in range(r.GetPointCount())]
            y = [r.GetY(j) for j in range(r.GetPointCount())]
            # skip boundary between individual rings
            codes += [mpath.Path.MOVETO] + (len(x)-1)*[mpath.Path.LINETO]
            all_x += x
            all_y += y
        path = mpath.Path(np.column_stack((all_x,all_y)), codes)
        paths_route.append(path)

    # Add paths as patches to axes

    for path in paths_route:
        patch = mpatches.PathPatch(path, facecolor='white', edgecolor='red')
        ax.add_patch(patch)
    ax.set_aspect(1.0)

    red_patch = mpatches.Patch(color='red', label='Bus Lines')
    blue_patch = mpatches.Patch(color='blue', label='Population Density')
    plt.legend(handles=[red_patch, blue_patch], loc = 1, prop = {'size':6})
    plt.show()

if __name__ == '__main__':
    bus_line = set(['200', '217'])
    drawMapView(shpBlckPath, shpBusRoutes, bus_line, 'Age', 'LineAbbr')