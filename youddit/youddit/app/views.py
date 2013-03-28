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
    
    def dispatch(self, request):
        if 'main_reddit' in request.GET:
           return self.main_reddit(request)
        elif 'subreddit' in request.GET:
            return self.subreddit(request)
        else:   
            return self.error("Requires param 'subreddit' or 'main_reddit'", 422)
        
    def main_reddit(self, request):
        reddit = request.GET['main_reddit']
        if reddit not in videos.MAIN_REDDITS:
            return self.error("Main reddit not recognized", 422)
        
        page = 1
        if 'page' in request.GET:
            page = int(request.GET['page'])
        limit = self.LIMIT
        if 'limit' in request.GET:
            limit = int(request.GET['limit'])
            if limit > 100:
                return self.error("Limit must be below 100", 422)

        db = self.mongo_connect().main_reddits
        data = db.find_one({ "name": reddit }, { "videos": { "$slice": [(page-1)*limit, limit] }})
        
        import pprint
        p = pprint.PrettyPrinter()
        p.pprint(data)
        return HttpResponse(json.dumps(data['videos']))
    
    def subreddit(request):
        db = mongo_connect().subreddits
        r = request.GET['subreddit']
        # Check subreddit is in db
        reddit = db.find_one({ "name": r})

        # If not, then create it and get videos
        if not reddit:
            sid = db.insert({ "name": reddit, "status": 0 })
      
    def mongo_connect(self):
        c = MongoClient()
        return c.Youddit

    def error(self, msg, code):
        err = { "error": msg, "status": code }
        response = HttpResponse(json.dumps(err))
        response.status = code
        return response

