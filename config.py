import os
from shapely.geometry import Polygon
from shapely.geometry import Point

instagram_client_id = '4d9231b411eb4ef69435b40eb83999d6'
instagram_client_secret = '204c565fa1244437b9034921e034bdd6'

instagram_API_pause = 0.1

#mongodb_address = 'grande'
mongodb_address = 'grande.rutgers.edu'
mongodb_port = 27017

class BaseConfig(object):
        region_percentage = 1
        min_elements = 8
        # grand : res ; joust : grad
        @staticmethod
        def getRegionListPath():
                cp = os.getcwd()
                path = '/*/users/kx19/citybeat_online/distributed_gp/utility/region_cache/' 
                if '/res/' in cp:
                        return path.replace('*', 'res')
                if '/grad/' in cp:
                        return path.replace('*', 'grad')
              # in my pc
                return cp + '\\region_cache\\'

class PlazaConfig(BaseConfig):
    def __init__(self, plaza):
        if plaza == 'msp':
            points_list = ((40.74347, -73.98823), (40.74154, -73.98963),(40.74086, -73.98797), (40.74277, -73.98654))  #msp
            file_prefix = "msp_"   #wsp, msp 
        elif plaza == 'us':
            points_list = (((40.73729, -73.99053),(40.73668, -73.98884),(40.73419, -73.98999),(40.73517, -73.99206)))   #union square
            file_prefix = "us_"   #wsp, msp 
        elif plaza == 'wsp':
            points_list = (((40.7322,-73.9986),(40.7307,-73.9955),(40.7310, -73.9997),(40.7296,-73.9965)))   #wsp
            file_prefix = 'wsp_'
        
        self.points_list = points_list
        self.file_prefix = file_prefix
        self.poly = Polygon(((points_list)))  #madison square
        self.min_lat = min([t[0] for t in points_list])
        self.max_lat = max([t[0] for t in points_list])
        self.min_lng = min([t[1] for t in points_list])
        self.max_lng = max([t[1] for t in points_list])
        self.images_path = '/grande/local/kx19/images/'


class InstagramConfig(BaseConfig):
    photo_db = 'citybeat_production'
    event_db = 'citybeat_production'
    prediction_db = 'citybeat_production'
    #online setting
    photo_collection = 'photos'
    event_collection = 'online_candidate_instagram'
    prediction_collection = 'online_prediction_instagram'
    # in seconds
    merge_time_interval = 1
    zscore = 3
    min_phots = 8
    # bottom left: 40.690531,-74.058151
    # bottom right: 40.823163,-73.857994
    photo_min_lat = 40.74088
    photo_max_lat = 40.74344
    photo_min_lng = -73.9897
    photo_max_lng = -73.9865
    # cut the region into region_N * region_M subregions
    # try 10*10, 15*15, 20*20, 25*25
    #region_N = 25
    #region_M = 25

class TwitterConfig(BaseConfig):
    # we have not yet moved tweets from citybeat to production
    tweet_db = 'citybeat_production'
    event_db = 'citybeat_production'
    prediction_db = 'citybeat_production'
    tweet_collection = 'tweets'
    prediction_collection = 'online_prediction_twitter'
    event_collection = 'online_candidate_twitter'
    # grand : res ; joust : grad
    
if __name__ == '__main__':
    print BaseConfig.getRegionListPath()

    t = PlazaConfig()
    p = Point(40.7425757999999973, -73.9882029999999986)

    print p.within(t.poly)


