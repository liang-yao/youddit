from celery import Celery
from videos import Videos
import time
celery = Celery('workers', broker='redis://root@localhost//')

@celery.task(name='video_worker')
def video_worker(subreddit):
    v = Videos()
    v._load_videos(subreddit)

@celery.task(name='generate_bg_worker')
def generate_bg_worker(r):
    v = Videos(subreddit=r)
    print v
    for cat in Videos.CATEGORIES:
        videos = v.get_videos(cat, 1, 100).get('videos', [])
        for video in videos:
            v._generate_bg(video['vid'])
        
