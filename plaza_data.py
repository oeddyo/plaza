
from config import PlazaConfig
from region import Region
from shapely.geometry import Point
from  element_interface import ElementInterface
from sklearn import linear_model
from sklearn.preprocessing import normalize 

from sklearn.cluster import KMeans, MiniBatchKMeans


from datetime import datetime

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
        clf = linear_model.LinearRegression()
        clf.fit((features), labels)
        
        names = [at[2] for at in attraction_list]
        coef = clf.coef_
        
        res_sorted = sorted(zip(names, coef), key=lambda tup: tup[1])
        
        print [str(n)+":"+str(c) for n,c in res_sorted]
    
    
    def getRegions(self):
        plaza_squares = Region(self.coordinates)
        plaza_squares = plaza_squares.divideRegions(25,25)
        valid_squares = []
        ei = ElementInterface('citybeat_production', 'photos', 'photos')
        bad_number = 0
        all_number = 0
        all_photo_number = 0
        for region in plaza_squares:
            all_number += 1
            mid_point = region.getMidCoordinates()
            point = Point( mid_point )
            if not point.within( self.valid_poly ):
                continue
            cnt = 0
            bad_number += 1
            for p in ei.rangeQuery(region):
                cnt += 1
            if cnt>1000:
                region.display()
                continue
            valid_squares.append( (region, cnt) )
            print 'cnt = ',cnt
            all_photo_number+=cnt
        self.plaza_squares = valid_squares
        print "all number = ",all_number, " bad_number = ",bad_number
        print 'all photos = ',all_photo_number
   
    def getCoordinates(self, p):
        return (float(p['location']['latitude']), float(p['location']['longitude']))

    def isWeekday(self, p):
        d = datetime.fromtimestamp(float(p['created_time']))
        if int(d.weekday())>=0 and int(d.weekday())<=4:
            return True
        return False
    def isMorning(self, p):
        d = datetime.fromtimestamp(float(p['created_time']))
        if int(d.hour)>=6 and int(d.hour)<=11:
            return True
        return False

    def isEvening(self, p):
        d = datetime.fromtimestamp(float(p['created_time']))
        if int(d.hour)>=18 and int(d.hour)<=23:
            return True
        return False

    def inPoly(self, p):
        tmp = self.getCoordinates(p)
        p = Point(  tmp[0], tmp[1] )

        if p.within(self.valid_poly):
            return True
        return False

    def checkCondition(self, p):
        if not self.inPoly(p):
            return False
        #if  self.isWeekday(p):
        #    return False
        if not self.isMorning(p):
            return False

        return True

    def getClusteringData(self):
        ei = ElementInterface('citybeat_production', 'photos', 'photos')
        region = Region(self.coordinates)

        photos = ei.rangeQuery(region)
        ok_photos = []
        photo_cnt = 1
        for p in photos:
            if self.checkCondition(p):
                ok_photos.append(p)
                photo_cnt += 1
            if photo_cnt % 100 == 0:
                print 'accepting photo data', photo_cnt
        return ok_photos

    def doClustering(self):
        photos = self.getClusteringData()
        
        features = []

        for p in photos:
            features.append( list(self.getCoordinates(p)))
        km = KMeans(n_clusters = 10, init='k-means++', max_iter=100)
        km.fit(features) 
        f = file('morning_msp_10.txt', 'w')

        for idx in range(len(photos)):
            p = photos[idx]
            f.write( (str(p['location']['latitude'])+','+str(p['location']['longitude'])+','+str(km.labels_[idx])+'\n' ))

         



def main():
    pa = PlazaAnalyzer()
    #pa.getRegions();

    #pa.doRegression()
    pa.doClustering()
if __name__ == "__main__":
    main()
