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
    def __init__(self, time_of_day = 'afternoon', local_or_not = 'non_local'):
        self.coordinates =  [PlazaConfig.min_lat, PlazaConfig.min_lng, PlazaConfig.max_lat, PlazaConfig.max_lng] 
        self.valid_poly = PlazaConfig.poly
        self.file_prefix = PlazaConfig.file_prefix 
        self.m_ei = MongoDBInterface()
        self.m_ei.setDB('citybeat_production')
        self.m_ei.setCollection('photos')
        self.photos = self._getAllPhotosInPlaza()
        self.time_of_day = time_of_day 
        self.local_or_not = local_or_not
        self._loadLocalDic()
        self._timeFilter()  #filter the data according to constrains
        self.user_photos = self._buildUserIndex()

    def _isMorning(self, p):
        d = datetime.fromtimestamp(float(p['created_time']))
        print 'hour = ', d.hour
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
        print 'time of day = ', self.time_of_day
        print self.time_of_day == 'morning'
        if self.time_of_day == 'morning':
            print 'in here'
            return self._isMorning(p)
        elif self.time_of_day == 'afternoon':
            return self._isAfternoon(p)
        elif self.time_of_day == 'evening':
            return self._isEvening(p)
        elif self.time_of_day == 'all':
            return True
    
    def _buildUserIndex(self):
        u_idx  = {}
        for p in self.photos:
            un =  p['user']['username']
            if un in u_idx:
                u_idx[un].append(p)
            else:
                u_idx[un] = [p]
        return u_idx

    def _loadLocalDic(self):
        self.local_users = set()
        self.non_local_users = set()
        for u in open('./lib_data/'+self.file_prefix+'local_users.txt').readlines():
            u = u.strip()
            self.local_users.add(u)
        for u in open('./lib_data/'+self.file_prefix+'non_local_users.txt').readlines():
            u = u.strip()
            self.non_local_users.add(u)
    
    def _judgeLocal(self, p):
        u = p['user']['username']
        if self.local_or_not == 'local' and u in self.local_users:
            return True
        if self.local_or_not == 'non_local' and u in self.non_local_users:
            return True
        return False

    def _timeFilter(self):
        photos = []
        print 'begin filtering data to ', self.time_of_day
        print 'i have ', len(self.photos),' photos at begining'
        for p in self.photos:
            if self._isAtTime(p) :
                photos.append(p)
        self.photos = photos
        print 'after filter there are ', len(self.photos),' photos'

    def _getAllPhotosInPlaza(self):
        plaza_squares = Region(self.coordinates)
        plaza_squares = plaza_squares.divideRegions(25,25)
        ei = ElementInterface('citybeat_production', 'photos', 'photos')
        all_photos = []

        seen = set()
        for region in plaza_squares:
            mid_point = region.getMidCoordinates()
            point = Point( mid_point )
            if not point.within( self.valid_poly ):  #have to be in the polygon
                continue
            for p in ei.rangeQuery(region):
                if str(p['_id']) in seen:
                    continue
                seen.add(str(p['_id']))
                all_photos.append(p) 
        return all_photos
    

    def _getDis(self, lat1, lng1, lat2, lng2):
        return (85*(lat1-lat2)*(lat1-lat2) + 111*(lng1-lng2)*(lng1-lng2))*1000
    
    def computeSpeed(self, username):
        movements = self.getUserMovements(username)
        if len(movements)<1:
            return None
        speeds = []
        for move in movements:
            print movements
            for i in range(len(move)-1):
                print 'i = ', i, ' move[i] = ', move[i]
                print 'i+1 = ', i+1, 'move[i+1] = ', move[i+1]
                start_point = move[i][0]
                start_t = move[i][1]
                end_point = move[i+1][0]
                end_t = move[i+1][1]

                t_dif = end_t - start_t

                print 'start and end ',start_point, end_point
                dis = self._getDis(start_point[0], start_point[1], end_point[0],end_point[1])
                print 'dis tdif = ', dis, t_dif
                if t_dif!=0:
                    speeds.append( dis*1.0/t_dif)
        print speeds
        if len(speeds)!=0:
            return sum(speeds)*1.0/(len(speeds))
        return None
    


    def stayDuration(self, username):
        movements = self.getUserMovements(username)
        if len(movements)<1:
            return None
        stays = []
        for move in movements:
            print movements
            start_t = move[0][1]
            end_t = move[len(move)-1][1]
            t_dif = end_t - start_t
            if t_dif!=0:
                stays.append( t_dif)
        if len(stays)!=0:
            return sum(stays)*1.0/(len(stays))
        return None

    def getUserMovements(self, username):
        # (username, [(loc1,time1) (loc2,time2), ... ] )
        photos = self.user_photos[username]
        print 'for user ', username, ' we have ', len(photos)
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
        #print movements
        return movements

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

    f = file('./data/'+pa.file_prefix+pa.time_of_day+'.txt', 'w')
    for u in pa.user_photos:
        #pa.getUserMovements(u)
        #t = pa.computeSpeed(u)
        t = pa.stayDuration(u)
        if t is not None:
            print 'mean = ',t
            f.write(str(t)+'\n')
    #pa.doRegression()
    #pa.doClustering()
    #pa.doClusteringOnUser()
if __name__ == "__main__":
    main()
