from django.http import HttpResponse
from django.template import RequestContext, loader
from pymongo import MongoClient
import youddit.videos as videos, simplejson

def index(request):
    conn = MongoClient()
    coll = conn.Youddit.main_reddits
    v = {}
    for reddit in videos.MAIN_REDDITS:
        v[reddit] = coll.find_one({"name": reddit}, fields={"videos": { '$slice': [0, 25]}})
        del v[reddit]['_id']

    template = loader.get_template('index.html')
    context = RequestContext(request, { "data": simplejson.dumps(v) })
    return HttpResponse(template.render(context))


