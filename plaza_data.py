from config import PlazaConfig
from region import Region
from shapely.geometry import Point
from  element_interface import ElementInterface


def work():
    coordinates =  [PlazaConfig.min_lat, PlazaConfig.min_lng, PlazaConfig.max_lat, PlazaConfig.max_lng] 
    plaza_squares = Region(coordinates)
    plaza_squares = plaza_squares.divideRegions(25,25)

    valid_poly = PlazaConfig.poly


    ei = ElementInterface('citybeat_production', 'photos', 'photos')
    bad_number = 0
    all_number = 0
    for region in plaza_squares:
        all_number += 1
        mid_point = region.getMidCoordinates()
        point = Point( mid_point )
        region = region.toDict()
        print region['min_lat'], region['min_lng'], region['max_lat'], region['max_lng']
        if not point.within( valid_poly ):
            print 'not valid ' 
            continue
        cnt = 0
        bad_number += 1
        for p in ei.rangeQuery(region):
            cnt += 1
        print 'cnt = ',cnt 
    print "all number = ",all_number, " bad_number = ",bad_number

work()


pp = Point(40,40)
print pp.within( PlazaConfig.poly )
