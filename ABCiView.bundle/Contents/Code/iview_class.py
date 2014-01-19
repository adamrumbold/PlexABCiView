class iView_Config():
    BASE_URL = 'http://www.abc.net.au/iview/'

    CFG_URL = BASE_URL + 'xml/config.xml'
    CFG_XML = XML.ElementFromURL(CFG_URL)

    AUTH_URL = CFG_XML.xpath('/config/param[@name="auth"]')[0].get("value")
    API_URL = CFG_XML.xpath('/config/param[@name="api"]')[0].get("value")

    CAT_URL = BASE_URL + CFG_XML.xpath('/config/param[@name="categories"]')[0].get("value")

    RTMP_Server = CFG_XML.xpath('/config/param[@name="server_streaming"]')[0].get("value") + '?auth='
    SWF_URL = 'http://www.abc.net.au/iview/images/iview.jpg'

    CAT_XML = XML.ElementFromURL(CAT_URL)
    SERIES_URL = API_URL + 'seriesIndex'
    SERIES_JSON = JSON.ObjectFromURL(SERIES_URL)
    category_list = {}
    
    FALLBACK_PATH = 'rtmp://cp53909.edgefcs.net/ondemand'

    @classmethod
    def RTMP_URL(self):

        xml = XML.ElementFromURL(url=self.AUTH_URL) 
        token = xml.xpath('//a:token/text()', namespaces={'a': 'http://www.abc.net.au/iView/Services/iViewHandshaker'})[0]
	server = xml.xpath('//a:server/text()', namespaces={'a': 'http://www.abc.net.au/iView/Services/iViewHandshaker'})[0]
	
	if 'http' in server:
            return self.FALLBACK_PATH + '?auth=' + token
        else:
	    return server + '?auth=' + token
    
    
    @classmethod
    def CLIP_PATH(self):
        return 'mp4:flash/playback/_definst_/'
      
	xml = XML.ElementFromURL(self.AUTH_URL)
        path = xml.xpath('//a:path/text()', namespaces={'a': 'http://www.abc.net.au/iView/Services/iViewHandshaker'})
        if not path:
            return 'mp4:'

        return 'mp4:' + path[0]

    @classmethod
    def List_Categories(self):
        cats = {}
        for cat in self.CAT_XML.xpath('/categories/category'):
            id = cat.get('id')
            name = cat.find('name').text
            if id in ['test', 'index']:
                continue
            cats[id] = name

        return cats


class iView_Series(object):
    def __init__(self, key):
        self.id = key
        Log('Getting iView series info for:' + iView_Config.API_URL + 'series=' + key)
	json = JSON.ObjectFromURL(iView_Config.API_URL + 'series=' + key)
	for result in json:
	    Log('Checking series ID ' + str(key) + ' against results ' + str(result['a']) )
	    if str(result['a']) == str(key):
		Log('Got match for series ID')
		self.title = result['b']
		self.description = result['c']
		self.category = result['e']
		self.img = result['d']
		self.episode_count = len(result['f'])
		self.episodes = self.Episodes(result['f'])
	    else:
		Log('rejected series ID match')

    def Episodes(self, json):
        eps = []
        for ep in json:
            episode = {}
	    episode['id'] = ep['a']
            episode['title'] = ep['b']
            episode['description'] = ep['d']

            episode['live'] = 0
            if 'n' in ep:
                episode['url'] = ep['n'][:-4]
            else:
                episode['url'] = ep['r']
                episode['live'] = 1

            episode['thumb'] = ep['s']

            if 'j' in ep:
                episode['duration'] = int(ep['j']) * 1000
            else:
                episode['duration'] = 0
		
            eps.append(episode)

        return eps


class iView_Category(object):
    def __init__(self, key):

        self.id = key
        cats = iView_Config.List_Categories()
        self.title = cats[key]
        self.series_list = self.Series(key)

    def Series(self, search):
        series = []
        for show in iView_Config.SERIES_JSON:
            id = show['a']
            title = show['b']
            category = show['e']
            count = len(show['f'])
            tmp = []
            tmp.append(id)
            tmp.append(title)
            tmp.append(category)
            tmp.append(count)

            if category.find(search) >= 0:
                series.append(tmp)

        return series
	
	
	
	