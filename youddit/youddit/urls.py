from django.conf.urls import patterns, include, url
from app.views import VideosView

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'youddit.app.views.index', name='index'),
    url(r'^r/(?P<subreddit>\w+)$', 'youddit.app.views.subreddit', name='subreddit'),
    url(r'^(?P<subreddit>\w+)$', VideosView.as_view(), name='get_videos'),

    # url(r'^youddit/', include('youddit.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
