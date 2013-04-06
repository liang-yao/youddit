from django.http import HttpResponse
from django.template import RequestContext, loader
from django.views.generic import View
from pymongo import MongoClient
from time import time
import youddit.videos as videos, simplejson as json

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
    
    def dispatch(self, request, subreddit):
        if request.META['CONTENT_TYPE'] != "application/json":
            return HttpResponse(''):
        else:
            self.subreddit = subreddit
            return subreddit_vids(request) 
       
    def subreddit_vids(self, request):
        page = 1
        if 'page' in request.GET:
            page = int(request.GET['page'])
        limit = self.LIMIT
        if 'limit' in request.GET:
            limit = int(request.GET['limit'])
            if limit > 100:
                return self.error("Limit must be below 100", 422)
        cat = "top"
        if 'cat' in request.GET:
            cat = request.GET['cat']

        videos = get_videos(cat, page, limit)
        
        import pprint
        p = pprint.PrettyPrinter()
        p.pprint(data)
        return HttpResponse(json.dumps(videos))

    def get_videos(cat, page, limit):
        db = self.mongo_connect()
        # Check if we have the subreddit
        r = db.subreddit.find_one({ "name": subreddit })
        if not r:
            videos.load_videos(subreddit)
        data = db.find_one({ "name": reddit }, { "videos": { "$slice": [(page-1)*limit, limit] }})
         
    
     
    def mongo_connect(self):
        c = MongoClient()
        return c.Youddit

    def error(self, msg, code):
        err = { "error": msg, "status": code }
        response = HttpResponse(json.dumps(err))
        response.status = code
        return response

