from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.views.generic import View
from pymongo import MongoClient
from time import time, strftime, gmtime
from youddit.videos import Videos
import simplejson as json

def index(request):
    v = Videos(subreddit='videos')
    data = v.get_videos('hot', 1, VideosView.LIMIT) 
    template = loader.get_template('index.html')
    context = RequestContext(request, { "data": json.dumps(data), "popular": getPopular() })
    return HttpResponse(template.render(context))

def subreddit(request, subreddit):
    template = loader.get_template('subreddit.html')
    
    v = Videos(subreddit=subreddit)
    data = v.get_videos('hot', 1, VideosView.LIMIT, remote=True)
    if data == '':
        # Subreddit not in db, set loading
        loading = True
        data = []
    else:
        loading = False

    context = RequestContext(request, { "loading": loading, "data_raw": json.dumps(data), "data": data, "subreddit": subreddit, "popular": getPopular() })
    return HttpResponse(template.render(context))

def getPopular():
    conn = MongoClient()
    db = conn.Youddit
    r = [ i['name'] for i in db.subreddits.find({'name': {'$ne': 'videos'}}, {'name': 1, '_id': 0}).sort('ver', -1).limit(5) ]
    return r

class FeedbackView(View):
    
    def post(self, request):
        email = request.POST['email']
        msg = request.POST['msg']
        conn = MongoClient()
        db = conn.Youddit
        db.feedback.insert({'email': email, 'msg': msg, 'time': strftime("%a, %d %b %Y %H:%M:%S", gmtime())})
        return HttpResponseRedirect('/')
    
    def get(self, request):
        conn = MongoClient()
        db = conn.Youddit

        fb = db.feedback.find({}, {'_id': 0}).sort('$natural', -1)
        return HttpResponse(fb)

class VideosView(View):
    # Page size, 100 max, 25 default
    LIMIT = 25
    
    def dispatch(self, request, subreddit):
        self.subreddit = subreddit
        return self.subreddit_vids(request) 
       
    def subreddit_vids(self, request):
        page = 1
        if 'page' in request.GET:
            page = int(request.GET['page'])
            if page <= 0:
                return self._error("Page must be greater than 0", 422)

        limit = self.LIMIT
        if 'limit' in request.GET:
            limit = int(request.GET['limit'])
            if limit > 100 or limit <= 0:
                return self._error("Limit must be between 1 and 100", 422)

        cat = "top"
        if 'cat' in request.GET:
            cat = request.GET['cat']
        
        v = Videos(subreddit=self.subreddit)
        videos = v.get_videos(cat, page, limit)
        """
        import pprint
        p = pprint.PrettyPrinter()
        p.pprint(videos)
        """

        return HttpResponse(json.dumps(videos))

    def _error(self, msg, code):
        err = { "error": msg, "status": code }
        response = HttpResponse(json.dumps(err))
        response.status = code
        return response

