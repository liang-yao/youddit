from django.http import HttpResponse
from django.template import Context, loader
from pymongo import MongoClient
import youddit.videos as videos

def index(reqest):
    conn = MongoClient()
    coll = conn.Youddit.main_reddits
    v = {}
    for reddit in videos.MAIN_REDDITS:
        v[reddit] = coll.find_one({"name": reddit}, fields={"videos": { '$slice': [0, 25]}})

    template = loader.get_template('index.html')
    context = Context({ "data": v })
    return HttpResponse(template.render(context))


