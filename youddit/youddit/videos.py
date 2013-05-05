import urllib2, urllib, urlparse, simplejson as json, time, re, sys, traceback
from pymongo import MongoClient

class Videos():
    PROVIDERS = { "youtube.com": 1, "youtu.be": 2, "vimeo.com": 3 }
    CATEGORIES = { "hot": 0, "top": 1, "controversial": 2 }
    
    # List of subreddits we update per hour
    COOL_REDDITS = ["videos"]
    INTERNAL_FIELDS = {'_id': 0, 'subreddit': 0, 'cat': 0 , 'pos': 0 , 'ver': 0 }

    # Updating status
    UPDATING = 1
    FREE = 0

    def __init__(self, **kwargs):
        self.subreddit = kwargs.get('subreddit', '')
        self.conn = MongoClient()
        self.db = self.conn.Youddit

    def get_videos(self, cat, page, limit, **kwargs):
        # Check if we have the subreddit
        r = self.db.subreddits.find_one({ "name": self.subreddit })

        if not r:
            if 'remote' in kwargs:
                self._load_videos_remote(self.subreddit)
                return ''
        else:
            if 'ver' not in r:
                r['ver'] = 1
            query = self.db.videos.find({ "subreddit": self.subreddit, 
                                      "cat": self.CATEGORIES[cat], 
                                      "ver": r['ver'] }, 
                                      self.INTERNAL_FIELDS).sort('pos', 1).skip((page-1)*limit).limit(limit)
            data = {}
            data["subreddit"] = self.subreddit 
            data["cat"] = cat
            data['videos'] = [ v for v in query ]
        
            # If data is older than a day, update videos
            if 'updated_at' in r and r['updated_at'] <= (time.time()-24*60*60):
                self._load_videos_remote(self.subreddit)

            return data

    def _load_videos(self, r):
        print "Subreddit: ", r
        reddit = self.db.subreddits.find_and_modify(query={"name": r}, update={'$set': {'status': self.UPDATING}}, upsert=True)
        print reddit
        if reddit:
            # Check if this reddit is already being updated
            if reddit['status'] == self.UPDATING:
                return []
            ver = reddit['ver']
        else:
            ver = 0
        ver += 1
        videos = []
        for cat in self.CATEGORIES:
            print cat
            try:
                videos = self._get_videos(r, cat, pages=30)
            except Exception as e:
                print e
                print traceback.format_exc()
                pass
            if len(videos) == 0:
                continue
            # Add version and category to each video in list
            videos = [ self._merge(v, {"ver": ver, "cat": self.CATEGORIES[cat]}) for v in videos ]
            self.db.videos.insert(videos)
        self.db.subreddits.update({ "name": r }, { "name": r,
                                                   "updated_at": time.time(),
                                                   "ver": ver, 
                                                   "status": 0
                                                 }, True )
        self._clean_up(r, ver)
        self._generate_bg_remote(r);

    def _load_videos_remote(self, r):
        from workers import video_worker
        video_worker.delay(r)

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
            if not response:
                return []
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
                                    "subreddit": subreddit,
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
        except urllib2.HTTPError as e:
            print e
            if e.code == 502:
                time.sleep(5)
                return self._request(url, params)
            else:
                return None
        except Exception as e:
            return None
        try:
            response = json.loads(response.read())
        except Exception as e:
            return None
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

    def _clean_up(self, r, ver):
        """ Remove all vids from a subreddit with a version lower than 'ver'"""
        self.db.videos.remove({"subreddit": r, "ver": { "$lt": ver }}) 

    # Update the cool reddits
    # This should be called in a cron job
    @staticmethod
    def update():
        v =  Videos()
        for r in Videos.COOL_REDDITS:
            v._load_videos(r)
    
    """ Background images """
    def _generate_bg_remote(self, subreddit):
        from workers import generate_bg_worker
        generate_bg_worker.delay(subreddit)

    def _generate_bg(self, vid):
        import os
        if not os.getcwd().endswith('/static/bg/temp'):
            os.chdir("../../static/bg/temp")
        
        if not self._bg_exists(vid):
            try:
                os.system("wget http://img.youtube.com/vi/%(id)s/mqdefault.jpg -O %(id)s.jpg"%{'id': vid})
                os.system("convert %(id)s.jpg -modulate 200,0 -blur 0x5 -resize 1200 ../%(id)s.png"%{'id': vid})
                os.remove("%(id)s.jpg"%{'id': vid})
            except Exception as e:
                print e
                pass

    def _bg_exists(self, vid):
        import os
        return os.path.exists("../%s.png"%(vid))

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'update':
        Videos.update()
        print 'Done'


