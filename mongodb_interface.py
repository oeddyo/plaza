##########
# Author: Chaolun Xia, 2013-Jan-09#
#
# A basic and private interface to connect and test the mongodb 
#
##########
#Edited by: (Please write your name here)#

from config import InstagramConfig

import pymongo
import config
import types

class MongoDBInterface(object):
    #A basic interface#
    
    def __init__(self):
        self._connection = pymongo.Connection(config.mongodb_address,
                                              config.mongodb_port)
                                                        
    def setDB(self,  name):
        self._db = self._connection[name]
        
    def setCollection(self, name):
        self._collection = self._db[name]
    
    def saveDocument(self, document):
        # document must be a json or a class from {event, photo, prediction}
        if not type(document) is types.DictType:
            document = document.toDict()
        self._collection.save(document)
    
    def _deleteDocument(self, condition):
        assert condition is not None
        self._collection.remove(condition)
    
    def getDocument(self, condition={}):
        return self._collection.find_one(condition)
        
    def getAllDocuments(self, condition={}, limit=0):
        return self._collection.find(condition, timeout=False, limit=limit)
        
    def updateDocument(self, document):
        if not type(document) is types.DictType:
            document = document.toDict()
        self._collection.update({'_id':document['_id']}, document, True)
            
    def getAllDocumentIDs(self):
        # return a list of _id which is ObjectId
        IDs = []
        query_res = self._collection.find({},{'_id':1})
        for ID in query_res:
            IDs.append(ID['_id'])
        return IDs

    def getAllFields(self, field, condition={}, limit=0):
        # field should be a string, this method cannot be run on get _id
        return self._collection.find(condition, {field:1, '_id':False}, limit=limit)

if __name__=='__main__':
    mi = MongoDBInterface()
    mi.setDB('historic_alarm')
    mi.setCollection('labeled_event')
    events = mi.getAllDocuments(limit=0)
    i = 0
    for event in events:
        i += 1
        print i
    
