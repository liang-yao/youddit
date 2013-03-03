# Create your views here.
from django.http import HttpResponse
from django.template import Context, loader
import youddit.videos as videos

def index(reqest):
    v = videos.get_videos('top', 1)

    template = loader.get_template('index.html')
    context = Context({ "videos": v })
    return HttpResponse(template.render(context))


