import shapefile
import csv
from shapely.ops import polygonize_full, polygonize, cascaded_union
from shapely.geometry import mapping, Polygon, Point

class fileWriter:
    def __init__ (self):
        self.w = shapefile.Writer(shapefile.POLYGON)

    '''
    return: void

    Write csv file of comparison of two methods calculating disability population.

    Output file attributes: Id, Disability, DisabilityCentroid, DisabilityDiff.

    '''
    def writeExcel(self, resultList, fileName):

        with open(fileName+'.csv','w') as csvfile:
            fieldnames = ["id","Age","AgeCentroid","AgeDiff","Poverty", "PovertyCentroid","PovertyDiff","Disability", "DisabilityCentroid", "DisabilityDiff", "Race", "RaceCentroid", "RaceDiff","Unemploy", "UnemployCentroid", "UnemployDiff","Transporta", "TransportaCentroid", "TransportaDiff"]
            writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
            writer.writeheader()
            for item in resultList:
                writer.writerow(item)

    '''
    return: coordinates list

    Convert coordinates tuple to list.
    '''
    def tupleToList(self, t):
        polyList = []
        for item in t:
            if len(item)!=2:
                for i in item:
                    tmp = [float(i[0]),float(i[1])]
                    polyList.append(tmp)
            else:
                tmp = [float(item[0]),float(item[1])]
                polyList.append(tmp)
        return polyList

    '''
    return: void

    write shapefiles from lists.

    Use: generate polygon overlay pieces shapefile.

    '''
    def write_to_file(self, polys, resultMap, population_name):

        print resultMap
        print population_name
        self.w = shapefile.Writer(shapefile.POLYGON)

        polylist = []
        for poly in polys:
            polyTuples = (mapping(poly)["coordinates"])[0]
            polylist.append(self.tupleToList(polyTuples))

        #print (polylist)

        # print (len(resultMap))
        # print (len(polylist))

        self.w.field('Id','C','40')
        self.w.field(population_name,'C','40')

        for k,poly in enumerate(polylist):
            try:
                self.w.poly(parts=[poly])
                self.w.record(k, resultMap[k][population_name])
            except ShapefileException:
                print ("can't write this poly")

        self.w.save('shapefiles/test/polygonPieces_filtered')

    '''
    return: void

    write shapefiles from dict generated using bus stops overlay method.

    Use: generate each bus line as polygons.

    '''
    def write_to_file_dict(self, polys, resultMap, filted_Routes_map):

        for k,v in polys.items():
            polylist = []
            if v.is_empty == False:
                polyTuples = mapping(v)["coordinates"]
                if type(polyTuples[0][0][0]) is tuple:
                    cleanList = []
                    for ct in polyTuples:
                        for c in ct:
                            cleanList.append(self.tupleToList(c))
                    polys[k] = cleanList
                else:
                    polys[k] = [self.tupleToList(polyTuples[0])]
            else:
                polys[k] = []

        # Call shapefile writer.
        #print (polys)
        self.writeShapeFile("polygonLines_normal", polys, resultMap, filted_Routes_map)

    '''
    return: void

    write shapefiles from dict generated using blocks centroid method.

    use: generate each bus line as polygons using centroid method.

    '''

    def write_to_file_dict_centroid(self, polys, resultMap):

        self.w = shapefile.Writer(shapefile.POLYLINE)
        for k,v in polys.items():
            polys[k] = self.tupleToList(v)

        # Call shapefile writer.
        self.writeShapeFile_centroid("polygonLines_Centroid", polys, resultMap)


    '''
    return: void

    write shape file.
    '''
    def writeShapeFile(self, fileName, polys, resultMap, filted_Routes_map):

        print ('shape: ',len(polys))
        print ('map: ',len(resultMap))

        self.w = shapefile.Writer(shapefile.POLYGON)
        self.w.field('BUSLINE_ID','C','40')
        self.w.field('Age','C','40')
        self.w.field('Poverty','C','40')
        self.w.field('Disability','C','40')
        self.w.field('Race','C','40')
        self.w.field('Unemploy','C','40')
        self.w.field('Transporta','C','40')

        for k,v in polys.items():
            if len(v) == 0:
                print ('0: ', resultMap[k])
            if len(v) != 0:
                #print (resultMap[k])
                self.w.poly(parts=v)
                self.w.record(filted_Routes_map[k], resultMap[k]["Age"], resultMap[k]["Poverty"], resultMap[k]["Disability"], resultMap[k]["Race"], resultMap[k]["Unemploy"], resultMap[k]["Transporta"])

        self.w.save('shapefiles/test/'+str(fileName))

    def writeShapeFile_centroid(self,fileName, polys, resultMap):

        self.w.field('BUSLINE_ID','C','40')
        self.w.field('Age','C','40')
        self.w.field('Poverty','C','40')
        self.w.field('Disability','C','40')
        self.w.field('Race','C','40')
        self.w.field('Unemploy','C','40')
        self.w.field('Transporta','C','40')

        for k,v in polys.items():
            if len(v) != 0:
                print (v)
                self.w.poly(parts=[v])
                self.w.record(k, resultMap[k]["AgeCentroid"], resultMap[k]["PovertyCentroid"], resultMap[k]["DisabilityCentroid"], resultMap[k]["RaceCentroid"], resultMap[k]["UnemployCentroid"], resultMap[k]["TransportaCentroid"])

        self.w.save('shapefiles/test/'+str(fileName))


    def write_new_route_file(self, resultList, fields = ['LineName', 'Shape_Leng', 'Service', 'Frequency', 'LineAbbr']):

        self.w = shapefile.Writer(shapefile.POLYLINE)

        for f in fields:
            if f != 'shape':
                self.w.field(f, 'C', '60')

        for v in resultList:
            self.w.poly(parts=[v['shape']])
            self.w.record(v[fields[0]], v[fields[1]], v[fields[2]], v[fields[3]], v[fields[4]])
        self.w.save('../output/BusRoutes_UTA_New')
        print ('write succeed!')

    def write_new_stop_file(self, resultList, fields = ['Bench', 'StopId', 'Shelter', 'StreetNum', 'LocationUs', 'City', 'InService', 'Lighting', 'UTAStopID', 'AtStreet', 'BelongToLine', 'Transfer', 'Bicycle', 'OnStreet', 'StopName', 'Garbage']):


        self.w = shapefile.Writer(shapefile.POINT)
        for f in fields:
            if f != 'shape':
                self.w.field(f, 'C', '60')

        for v in resultList:
            self.w.point(v['shape'][0][0], v['shape'][0][1])
            self.w.record(v[fields[0]], v[fields[1]], v[fields[2]], v[fields[3]], v[fields[4]], v[fields[5]], v[fields[6]], v[fields[7]],  v[fields[8]],  v[fields[9]], v[fields[10]],  v[fields[11]],  v[fields[12]],  v[fields[13]],  v[fields[14]],  v[fields[15]])
        self.w.save('../output/BusStops_UTA_New')
        print ('write succeed!')

if __name__ == '__main__':
    '''
       Test
    '''
    lines = [
        ((0,0),(0,1)),
        ((0,1),(1,1)),
        ((1,0),(1,1)),
        ((0,0),(1,0)),
        ((5,5.5),(5,6.5)),
        ((5,6,5.5),(5.5,6.5)),
        ((6.5,5),(6.5,6.5)),
        ((5,5.5),(5.5,5))
    ]

    a = Polygon([(0, 0), (0, 1),(1,1), (1,0)])
    b = Polygon([(2, 0), (2, 1),(1,1), (1,0)])
    print(a.intersection(b).area == 0)
