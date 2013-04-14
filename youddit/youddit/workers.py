from celery import Celery
from videos import Videos
import time
celery = Celery('workers', broker='redis://root@localhost//')

@celery.task(name='video_worker')
def video_worker(subreddit):
    v = Videos()
    v._load_videos(subreddit)
    
@celery.task
def add(x, y):
    time.sleep(10)
    return x + y

