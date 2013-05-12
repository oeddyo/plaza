import types
from base_element import BaseElement


class Photo(BaseElement):
    # before you save an instance of Photo, convert it to JSON first
    # by photo.toDict()
    
    def __init__(self, photo):
        super(Photo, self).__init__(photo)
        
    def getLocationName(self):
        mod_location = ''
        try:
            location = self._element['location']['name']
            for c in location.lower():
                if c >= 'a' and c <= 'z':
                    mod_location += c
        except Exception as e:
            pass
        return mod_location
    
    def getUserName(self):
        return self._element['user']['username']
        
    def getCaption(self):
        if 'caption' not in self._element.keys() or self._element['caption'] is None:
            return ''
        if ('text' not in self._element['caption'].keys() or
                self._element['caption']['text'] is None):
            return ''
        return self._element['caption']['text'].strip()
    
    def getText(self):
        # new interface
        return self.getCaption()        
