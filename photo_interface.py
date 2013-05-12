import config
import time
import logging
import string
import types

from datetime import datetime
from mongodb_interface import MongoDBInterface
from config import InstagramConfig
from element_interface import ElementInterface

class PhotoInterface(ElementInterface):
    
    def __init__(self, db=InstagramConfig.photo_db,  
                 collection=InstagramConfig.photo_collection):
        # initialize an interface for accessing photos from mongodb
        super(PhotoInterface, self).__init__(db, collection, 'photos')
    
    def _computeBoundaryOfPhotos(self):
        cnt = 0
        min_lat = 1000
        min_lng = 1000
        max_lat = -1000
        max_lng = -1000
        photos = self.getAllDocuments()
        print type(photos)
        for photo in photos:
            cnt += 1
            if photo['location'] is None:
                continue
            lat = float(photo['location']['latitude'])
            lng = float(photo['location']['longitude'])
            max_lat = max(max_lat, lat)
            min_lat = min(min_lat, lat)
            max_lng = max(max_lng, lng)
            min_lng = min(min_lng, lng)
            if cnt % 10000 == 0:
                print cnt
        return [min_lat, max_lat, min_lng, max_lng]
        
    def findTimeInterval(self):
        pc = self.getAllDocuments()
        t1 = -1
        t2 = -1
        for photo in pc:
            if t1 == -1:
                t1 = int(photo['created_time'])
                t2 = t1
            else:
                t = int(photo['created_time'])
                if t < t1:
                    t1 = t
                if t > t2:
                    t2 = t
        return [t1, t2]
    
def getPhotoDistribution():
    ti = PhotoInterface()
    ti.setDB('citybeat_production')
    ti.setCollection('photos')
    cur = ti.getAllFields('created_time')
    earliest = 2363910281
    latest = 363910281
    histagram = {}
    for tuple in cur:
        time = int(tuple['created_time'])
        if time > latest:
            latest = time
        if time < earliest:
            earliest = time
        hour = time / (3600)
        histagram[hour] = histagram.get(hour, 0) + 1
        
    for key, value in histagram.items():
        print key, value

if __name__=="__main__":
    getPhotoDistribution()
