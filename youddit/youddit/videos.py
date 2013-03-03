import urllib2, urllib, simplejson as json, time, re, sys

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
                
                ytURL = reddit['data']['url']
                
                # extracting the video id from url
                try:
                    m = re.search('v=', ytURL)
                    endInd = m.end()
                    print ytURL[endInd:endInd+11]
                except Exception, e:
                    sys.stderr.write("No v= pattern found in YT url" + str(e) + '\n')        
                    continue

                # appending the video url data to the videos list
                #print reddit['data']['url'] 
                #print reddit['data']['score']
                videos.append(ytURL)

        after = response['data']['after']
        #print "page: " + str(page)
    return videos
