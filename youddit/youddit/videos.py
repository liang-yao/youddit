import urllib2, urllib, urlparse, simplejson as json, time, re, sys
from pymongo import MongoClient

class Videos():
    PROVIDERS = { "youtube.com": 1, "youtu.be": 2, "vimeo.com": 3 }
    CATEGORIES = { "top": 0, "hot": 1, "controversial": 2 }
    # List of subreddits we update per hour
    COOL_REDDITS = ["videos"]
    INTERNAL_FIELDS = {'_id': 0, 'subreddit': 0, 'cat': 0 , 'pos': 0 , 'ver': 0 }


    def __init__(self, **kwargs):
        self.subreddit = kwargs.get('subreddit', '')
        self.conn = MongoClient()
        self.db = self.conn.Youddit

    def load_videos(self, r):
        print "Subreddit: ", r
        reddit = self.db.subreddits.find_one({"name": r})
        if reddit:
            ver = reddit['ver']
        else:
            ver = 0
        ver += 1
        videos = []
        for cat in self.CATEGORIES:
            print cat
            videos = self._get_videos(r, cat, pages=30)
            # Add version and category to each video in list
            videos = [ self._merge(v, {"ver": ver, "cat": self.CATEGORIES[cat]}) for v in videos ]
            self.db.videos.insert(videos)
            self.db.subreddits.update({ "name": r }, { "name": r,
                                                  "updated_at": time.time(),
                                                  "ver": ver
                                                }, True )
        return videos

    def get_videos(self, cat, page, limit):
        # Check if we have the subreddit
        r = self.db.subreddits.find_one({ "name": self.subreddit })
        data = {}
        data["subreddit"] = self.subreddit 
        data["cat"] = cat
        data["videos"] = [] 

        if not r:
            for v in self.load_videos(self.subreddit):
                data['videos'].append(self._remove_internal_fields(v))
        else:
            query = self.db.videos.find({ "subreddit": self.subreddit, 
                                      "cat": self.CATEGORIES[cat], 
                                      "ver": r['ver'] }, 
                                      self.INTERNAL_FIELDS).sort('pos', 1).skip((page-1)*limit).limit(limit)
            data['videos'] = [ v for v in query ]
                
        return data

    def _remove_internal_fields(self, source):
        for f in self.INTERNAL_FIELDS:
            del source[f]
        return source

    def _get_videos(self, subreddit, category, **kwargs):
        url = "http://www.reddit.com/r/%s/%s.json"%(subreddit, category)
        pages = 30
        if "pages" in kwargs:
            pages = kwargs["pages"]
        videos = []

        after = ''
        position = 0
        for page in range(0, pages):
            response = self._request(url, {'limit':100, 'after': after})
            if len(response['data']['children']) == 0:
                break
            for reddit in response['data']['children']:
                if reddit['data']['domain'] in self.PROVIDERS:
                    provider = self.PROVIDERS[reddit['data']['domain']] 
                    
                    # Remove vimeo for this version
                    if provider == self.PROVIDERS["vimeo.com"]:
                        continue

                    r = reddit['data']
                    vid = self._get_vid(provider, r['url'])
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

    def _request(self, url, params):
        params = urllib.urlencode(params)
        req = urllib2.Request(url + '?' + params)
        req.add_header('User-Agent', 'reddit video stream youddit')
        req.add_header('Content-Type', 'application/json')
       
        try:
            response = urllib2.urlopen(req)
        except Exception as e:
            print e
            time.sleep(5)
            return request(url, params)
            
        response = json.loads(response.read())
        return response
      
    # Returns the video id 
    def _get_vid(self, provider, url):
        u = urlparse.urlparse(url)
        if provider == self.PROVIDERS['youtube.com']:
            try:
                return urlparse.parse_qs(u.query)['v'][0]
            except KeyError:
                return ''
        elif provider == self.PROVIDERS['youtu.be'] or provider == self.PROVIDERS['vimeo.com']:
            return u.path[1:]

    # Return the thumbnail url if its there
    def _get_thumbnail(self, data):
        if "thumbnail" in data:
            return data['thumbnail']
        else:
            return ''

    def _merge(self, d1, d2):
        d1.update(d2)
        return d1

    # Update the cool reddits
    # This should be called in a cron job
    @staticmethod
    def update():
        v =  Videos()
        for r in Videos.COOL_REDDITS:
            v.load_videos(r)

    @staticmethod
    def clean_up():
        db = MongoClient().Youddit
        for r in Videos.COOL_REDDITS:
            reddit = db.subreddits.find_one({"name": r})
            print r
            if not reddit:
                continue
            db.videos.remove({"subreddit": reddit['name'], "ver": { "$lt": reddit['ver'] }}) 

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'update':
        Videos.update()
        Videos.clean_up()
        print 'Done'


