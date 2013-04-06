import urllib2, urllib, urlparse, simplejson as json, time, re, sys
from pymongo import MongoClient

PROVIDERS = { "youtube.com": 1, "youtu.be": 2, "vimeo.com": 3 }
CATEGORIES = { "top": 0, "hot": 1, "controversial": 2 }
# List of subreddits we update per hour
COOL_REDDITS = ["videos"]

def get_videos(subreddit, category, **kwargs):
    url = "http://www.reddit.com/r/%s/%s.json"%(subreddit, category)
    pages = 30
    if "pages" in kwargs:
        pages = kwargs["pages"]
    videos = []

    after = ''
    position = 0
    for page in range(0, pages):
        response = request(url, {'limit':100, 'after': after})
        if len(response['data']['children']) == 0:
            break
        for reddit in response['data']['children']:
            if reddit['data']['domain'] in PROVIDERS:
                provider = PROVIDERS[reddit['data']['domain']] 
                
                # Remove vimeo for this version
                if provider == PROVIDERS["vimeo.com"]:
                    continue

                r = reddit['data']
                vid = _get_vid(provider, r['url'])
                # Some videos dont have proper links, so we skip them
                if vid == '':
                    continue
                position += 1
                # appending the video data to the videos list
                videos.append({ "rid": r['id'], # Reddit id
                                "title": r['title'],
                                "provider": provider, 
                                "vid": vid, 
                                "subreddit": r['subreddit'],
                                "score": r['score'],
                                "permalink": r['permalink'],
                                "created": r['created'],
                                "pos": position
                              })

        after = response['data']['after']
        print "After: ", after
        if not after:
            break
        time.sleep(1)
    return videos

def request(url, params):
    params = urllib.urlencode(params)
    request = urllib2.Request(url + '?' + params)
    request.add_header('User-Agent', 'reddit video stream youddit')
    request.add_header('Content-Type', 'application/json')
   
    try:
        response = urllib2.urlopen(request)
    except Exception as e:
        print e
        time.sleep(5)
        return request(url, params)
        
    response = json.loads(response.read())
    return response
  
# Returns the video id 
def _get_vid(provider, url):
    u = urlparse.urlparse(url)
    if provider == PROVIDERS['youtube.com']:
        try:
            return urlparse.parse_qs(u.query)['v'][0]
        except KeyError:
            return ''
    elif provider == PROVIDERS['youtu.be'] or provider == PROVIDERS['vimeo.com']:
        return u.path[1:]

# Return the thumbnail url if its there
def _get_thumbnail(data):
    if "thumbnail" in data:
        return data['thumbnail']
    else:
        return ''

# Update the cool reddits
# This should be called in a cron job
def update():
    conn = MongoClient()
    db = conn.Youddit

    for r in COOL_REDDITS:
        reddit = db.subreddits.find_one({"name": r})
        if reddit:
            ver = reddit['ver']
        else:
            ver = 0
        ver += 1
        for cat in CATEGORIES:
            print cat
            videos = get_videos(r, cat, pages=30)
            # Add version and category to each video in list
            videos = [ merge(v, {"ver": ver, "cat": CATEGORIES[cat]}) for v in videos ]
            db.videos.insert(videos)
            db.subreddits.update({ "name": r }, { "name": r,
                                                  "updated_at": time.time(),
                                                  "ver": ver
                                                }, True )
    conn.close()

def clean_up():
    conn = MongoClient()
    db = conn.Youddit
    for r in COOL_REDDITS:
        reddit = db.subreddits.find_one({"name": r})
        print r
        if not reddit:
            continue
        db.videos.remove({"subreddit": reddit['name'], "ver": { "$lt": reddit['ver'] }}) 
    conn.close()

def merge(d1, d2):
    d1.update(d2)
    return d1

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'update':
        update()
        clean_up()
        print 'Done'


