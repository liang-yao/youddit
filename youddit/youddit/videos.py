import urllib2, urllib, simplejson as json, time

def get_videos(source, pages):
    videos = []
    url = "http://www.reddit.com/%s.json"%(source)
    after = ''
    for page in range(0, pages):
        params = urllib.urlencode({'limit':100, 'after': after})
        request = urllib2.Request(url + '?' + params)
        request.add_header('User-Agent', 'reddit video stream youddit')
        request.add_header('Content-Type', 'application/json')
        
        response = urllib2.urlopen(request)
        response = json.loads(response.read())
        for reddit in response['data']['children']:
            if reddit['data']['domain'] == "youtube.com":
                #print reddit['data']['url'] 
                #print reddit['data']['score']
                videos.append(reddit['data']['url'])
        after = response['data']['after']
        #print "page: " + str(page)
    return videos
