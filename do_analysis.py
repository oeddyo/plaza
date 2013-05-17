from config import PlazaConfig
from region import Region
from shapely.geometry import Point
from  element_interface import ElementInterface
from sklearn import linear_model
from sklearn.preprocessing import normalize 
import random

from sklearn.cluster import KMeans, MiniBatchKMeans, DBSCAN, MeanShift, SpectralClustering
from sklearn import cluster
from datetime import datetime
import numpy as np
from mongodb_interface import MongoDBInterface
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

class PlazaAnalyzer():
    def __init__(self, time_of_day = 'morning', local_or_not = 'local'):
        self.coordinates =  [PlazaConfig.min_lat, PlazaConfig.min_lng, PlazaConfig.max_lat, PlazaConfig.max_lng] 
        self.valid_poly = PlazaConfig.poly
        self.file_name_prefix = PlazaConfig.file_prefix 
        self.m_ei = MongoDBInterface()
        self.m_ei.setDB('citybeat_production')
        self.m_ei.setCollection('photos')
        self.photos, self.user_photos = self._getAllPhotosInPlaza()
        self.time_of_day = time_of_day 
        self.local_or_not = local_or_not
        self._dataFilter()  #filter the data according to constrains

    def _isMorning(self, p):
        d = datetime.fromtimestamp(float(p['created_time']))
        if int(d.hour)>=6 and int(d.hour)<=12:
            return True
        return False

    def _isEvening(self, p):
        d = datetime.fromtimestamp(float(p['created_time']))
        if int(d.hour)>=18 and int(d.hour)<=24:
            return True
        return False
    
    def _isAfternoon(self, p):
        d = datetime.fromtimestamp(float(p['created_time']))
        if int(d.hour)>=12 and int(d.hour)<=18:
            return True
        return False
    
    def _isAtTime(self, p):
        if self.time_of_day == 'mornining':
            return self._isMorning(p)
        elif self.time_of_day == 'afternoon':
            return self._isAfternoon(p)
        elif self.time_of_day == 'evening':
            return self._isEvening(p)
    
    def _loadLocalDic(self):
        pass

    def _dataFilter(self):
        photos = []
        print 'begin filtering data to ', self.time_of_day
        for p in self.photos:
            if _isAtTime(p, self.time_of_day):
                photos.append(p)
        self.photos = photos

    def _getAllPhotosInPlaza(self):
        plaza_squares = Region(self.coordinates)
        plaza_squares = plaza_squares.divideRegions(25,25)
        ei = ElementInterface('citybeat_production', 'photos', 'photos')
        all_photos = []
        all_users = {}
        for region in plaza_squares:
            mid_point = region.getMidCoordinates()
            point = Point( mid_point )
            if not point.within( self.valid_poly ):  #have to be in the polygon
                continue
            for p in ei.rangeQuery(region):
                un = p['user']['username']
                if un in all_users:
                    all_users[un].append(p)
                    continue
                else:
                    all_users[un] = [p]
        return all_photos, all_users
    
    def getUserMovements(self, username):
        # (username, [(loc1,time1) (loc2,time2), ... ] )
        photos = self.user_photos[username]
        positions = []
        for p in photos:
            cor = self.getCoordinates(p)
            if self.inPoly(p):    
                positions.append( (cor, int(p['created_time'])))
        positions = sorted(positions, key=lambda tup:tup[1])
        positions.append( ((0,0),9999999999999))
        max_gap = 3600
        movements = []
        cur_mov = []
        for i in range(len(positions)-1):
            d = positions[i+1][1] - positions[i][1]
            if positions[i+1][1]-positions[i][1] < max_gap:
                cur_mov.append( positions[i] )
            else:
                if len(cur_mov)>=1:
                    cur_mov.append(positions[i])
                    movements.append(cur_mov)
                cur_mov = []
        print movements
        return (username, movements)
    
    def getCoordinates(self, p):
        return (float(p['location']['latitude']), float(p['location']['longitude']))

    def isWeekday(self, p):
        d = datetime.fromtimestamp(float(p['created_time']))
        if int(d.weekday())>=0 and int(d.weekday())<=4:
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
        if self.isEvening(p):
            return False

        #if not self.isMorning(p):
        #    return False

        return True
def main():
    pa = PlazaAnalyzer()

    for u in pa.user_photos:
        pa.getUserMovements(u)

    #pa.doRegression()
    #pa.doClustering()
    #pa.doClusteringOnUser()
if __name__ == "__main__":
    main()
