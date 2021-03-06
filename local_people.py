
from config import PlazaConfig
from region import Region
from shapely.geometry import Point
from  element_interface import ElementInterface
from sklearn import linear_model
from sklearn.preprocessing import normalize 

from sklearn.cluster import KMeans, MiniBatchKMeans, DBSCAN, MeanShift, SpectralClustering
from sklearn import cluster
from datetime import datetime
import numpy as np
from mongodb_interface import MongoDBInterface
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer



class LocalUsers():
    def __init__(self):
        self.coordinates = [PlazaConfig.min_lat, PlazaConfig.min_lng, PlazaConfig.max_lat, PlazaConfig.max_lng] 
        self.valid_poly = PlazaConfig.poly
    
        self.m_ei = MongoDBInterface()
        self.m_ei.setDB('citybeat_production')
        self.m_ei.setCollection('photos')
        self.file_prefix = PlazaConfig.file_prefix

    def isLocal(self, username):
        check_time = 1366033832
        user_photos = self.m_ei.getAllDocuments({'user.username':username})
        one_week = 7*24*3600
        t_end = check_time+4*one_week
        cur_time = check_time
        while cur_time<t_end:
            ok = False
            for p in user_photos:
                t = int(p['created_time'])
                if t>cur_time and t<cur_time + one_week:
                    ok = True
                    break
            if ok:
                cur_time += one_week
            else:
                return False
        return True

    
    def getLocalUsers(self):
        plaza_squares = Region(self.coordinates)
        plaza_squares = plaza_squares.divideRegions(25,25)
        users_in_park = set()
        ei = ElementInterface('citybeat_production', 'photos', 'photos')
        for region in plaza_squares:
            mid_point = region.getMidCoordinates()
            point = Point( mid_point )
            if not point.within( self.valid_poly ):
                continue
            for p in ei.rangeQuery(region):
                users_in_park.add(p['user']['username'])
        f = file('./lib_data/'+self.file_prefix+'non_local_users.txt', 'w') 
        for u in users_in_park:
            if self.isLocal(u)==False:
                f.write(u+'\n')
        
        f = file('./lib_data/'+self.file_prefix+'local_users.txt', 'w')
        for u in users_in_park:
            if self.isLocal(u):
                f.write(u+'\n')



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
        if self.isEvening(p):
            return False


        return True

def main():
    pa = LocalUsers()
    pa.getLocalUsers()
if __name__ == "__main__":
    main()
