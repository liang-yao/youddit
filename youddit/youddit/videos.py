import urllib2, urllib, urlparse, simplejson as json, time, re, sys
from pymongo import MongoClient

MAIN_REDDITS = ["hot", "top", "controversial"]
PROVIDERS = { "youtube.com": 1, "vimeo.com": 2 }

def get_videos(source, pages):
    conn = MongoClient()
    db = conn.Youddit
    coll = db.main_reddits
    
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
        if len(response['data']['children']) == 0:
            break
        for reddit in response['data']['children']:
            if reddit['data']['domain'] in PROVIDERS:
                provider = PROVIDERS[reddit['data']['domain']] 
                r = reddit['data']
                vid = _get_vid(provider, r['url'])
                # Some videos dont have proper links, so we skip them
                if vid == '':
                    continue
                thumbnail = _get_thumbnail(r)

                # appending the video data to the videos list
                videos.append({ "title": r['title'],
                                "provider": provider, 
                                "vid": vid, 
                                "thumbnail": thumbnail,
                                "subreddit": r['subreddit'],
                                "id": r['id'], # Reddit id
                                "score": r['score'],
                                "permalink": r['permalink'],
                                "created": r['created'],
                })

            after = response['data']['after']
        time.sleep(1)
    # Update db
    coll.update({"name": source}, {'$set': {'videos': videos, 'updated_at': time.time()}})
    conn.close()

    return videos

# Returns the video id 
def _get_vid(provider, url):
    u = urlparse.urlparse(url)
    if provider == PROVIDERS['youtube.com']:
        try:
            return urlparse.parse_qs(u.query)['v'][0]
        except KeyError:
            return ''
    elif provider == PROVIDERS['vimeo.com']:
        return u.path[1:]

# Return the thumbnail url if its there
def _get_thumbnail(data):
    if "thumbnail" in data:
        return data['thumbnail']
    else:
        return ''

# Update the main reddits
# This should be called in a cron job
def update():
    for r in MAIN_REDDITS:
        print r
        get_videos(r, 30)


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'update':
        update()
        print 'Done'


