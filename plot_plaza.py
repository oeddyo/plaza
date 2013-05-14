
from config import PlazaConfig
from region import Region
from shapely.geometry import Point
from  element_interface import ElementInterface
from sklearn import linear_model


class PlazaAnalyzer():
    def __init__(self):
        self.coordinates =  [PlazaConfig.min_lat, PlazaConfig.min_lng, PlazaConfig.max_lat, PlazaConfig.max_lng] 
        self.valid_poly = PlazaConfig.poly
     
    def readAttractions(self):
        f = open('attraction_msq.txt').readlines()
        attraction_list = []
        for line in f:
            t = line.split(',')
            lat = float(t[0])
            lng = float(t[1])
            attraction_list.append( (lat, lng, t[2]) )
        return attraction_list

    def getDis(self, lat1, lng1, lat2, lng2):
        return (85*(lat1-lat2)*(lat1-lat2) + 111*(lng1-lng2)*(lng1-lng2))*1000

    def doRegression(self):
        features = []
        labels = []
        attraction_list = self.readAttractions()
        for sq in self.plaza_squares:
            lat = sq[0].getMidCoordinates()[0]
            lng = sq[0].getMidCoordinates()[1]
            t_feature = []
            for attraction in attraction_list:
                dis = self.getDis(lat, lng, attraction[0], attraction[1])
                t_feature += [dis]
            features.append(t_feature)
            labels.append(sq[1]) 
        print features
        print labels

        clf = linear_model.LinearRegression()
        clf.fit(features, labels)
        
        names = [at[2] for at in attraction_list]
        coef = clf.coef_
        print [str(n)+":"+str(c) for n,c in zip(names, coef)]
    def getRegions(self):
        plaza_squares = Region(self.coordinates)
        plaza_squares = plaza_squares.divideRegions(25,25)
        valid_squares = []
        ei = ElementInterface('citybeat_production', 'photos', 'photos')
        bad_number = 0
        all_number = 0
        for region in plaza_squares:
            all_number += 1
            mid_point = region.getMidCoordinates()
            point = Point( mid_point )
            if not point.within( self.valid_poly ):
                print 'not valid ' 
                continue
            cnt = 0
            bad_number += 1
            for p in ei.rangeQuery(region):
                cnt += 1
            valid_squares.append( (region, cnt) )
            print 'cnt = ',cnt 
        self.plaza_squares = valid_squares
        print "all number = ",all_number, " bad_number = ",bad_number




def main():
    pa = PlazaAnalyzer()
    pa.getRegions();

    pa.doRegression()

if __name__ == "__main__":
    main()
