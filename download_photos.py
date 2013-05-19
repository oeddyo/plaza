from do_analysis import PlazaAnalyzer
from urllib import urlretrieve
from config import PlazaConfig


def work():
    plazas = ['us', 'wsp', 'wsp']

    for plaza in plazas:
        print 'plaza = ',plaza
        analyzer = PlazaAnalyzer(plaza = plaza, time_of_day = 'afternoon', local_or_not = 'non_local')
        cfg = PlazaConfig( plaza )
        path_prefix = cfg.images_path
        f = file('file_mapping.txt', 'a')
        cnt = 0
        n_photos = len(analyzer.photos)
        for p in analyzer.photos:
            print 'downloading %d/%d'%(cnt,n_photos)
            cnt+=1
            try:
                url = p['images']['standard_resolution']['url']
                file_name = url[url.find('com') + 4 : ]
                f.write(url+"\t"+file_name+'\n')
                urlretrieve(url, path_prefix+file_name)
            except:
                continue

work()
