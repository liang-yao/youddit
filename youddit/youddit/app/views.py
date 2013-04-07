from django.http import HttpResponse
from django.template import RequestContext, loader
from django.views.generic import View
from pymongo import MongoClient
from time import time
import youddit.videos as Videos, simplejson as json

def index(request):
    conn = MongoClient()
    db = conn.Youddit
    vids = {}
    reddit = "videos"
    ver = db.subreddits.find_one({"name": reddit})['ver'] 
    v = []
    for i in db.videos.find({ "subreddit": reddit, "cat": videos.CATEGORIES['top'], "ver": ver }, {'_id': 0}).sort('pos', 1).limit(25):
        v.append(i)
    template = loader.get_template('index.html')
    context = RequestContext(request, { "data": json.dumps(v) })
    return HttpResponse(template.render(context))

class VideosView(View):
    # Page size, 100 max
    LIMIT = 25
    subreddit = ''
    internal_fields = {'_id': 0, 'subreddit': 0, 'cat': 0 , 'pos': 0 , 'ver': 0 }
    
    def dispatch(self, request, subreddit):
        self.subreddit = subreddit
        return self.subreddit_vids(request) 
       
    def subreddit_vids(self, request):
        page = 1
        if 'page' in request.GET:
            page = int(request.GET['page'])
            if page <= 0:
                return self.error("Page must be greater than 0", 422)

        limit = self.LIMIT
        if 'limit' in request.GET:
            limit = int(request.GET['limit'])
            if limit > 100 or limit <= 0:
                return self.error("Limit must be between 1 and 100", 422)

        cat = "top"
        if 'cat' in request.GET:
            cat = request.GET['cat']

        videos = self.get_videos(cat, page, limit)
        """
        import pprint
        p = pprint.PrettyPrinter()
        p.pprint(videos)
        """

        return HttpResponse(json.dumps(videos))

    def get_videos(self, cat, page, limit):
        db = self.mongo_connect()
        # Check if we have the subreddit
        r = db.subreddits.find_one({ "name": self.subreddit })
        data = {}
        data["subreddit"] = self.subreddit 
        data["cat"] = cat
        data["videos"] = [] 

        if not r:
            for v in Videos.load_videos(self.subreddit):
                data['videos'].append(self.remove_internal_fields(v))
        else:
            query = db.videos.find({ "subreddit": self.subreddit, 
                                      "cat": Videos.CATEGORIES[cat], 
                                      "ver": r['ver'] }, 
                                      self.internal_fields).sort('pos', 1).skip((page-1)*limit).limit(limit)
            data['videos'] = [ v for v in query ]
                
        return data

    def remove_internal_fields(self, source):
        for f in self.internal_fields:
            del source[f]
        return source

    def mongo_connect(self):
        c = MongoClient()
        return c.Youddit

    def error(self, msg, code):
        err = { "error": msg, "status": code }
        response = HttpResponse(json.dumps(err))
        response.status = code
        return response

