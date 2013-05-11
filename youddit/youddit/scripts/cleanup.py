from pymongo import MongoClient
import os, sys
sys.path.append(os.path.join(os.getcwd(), "../"))
from videos import Videos

def bg_cleanup():
    conn = MongoClient()
    db = conn.Youddit
    os.chdir("../../../static/bg")
    pics = [ p.split('.png')[0] for p in os.walk('.').next()[2]] 
    vids = getVidsWithBg(db)    
    for p in pics:
        if p not in vids:
            remove(p)

def getVidsWithBg(db):
    subreddits = db.subreddits.find()
    print subreddits
    vids = []
    for r in subreddits:
        print r['name']
        v = Videos(subreddit=r['name'])
        for cat in Videos.CATEGORIES:
            vids += [ video['vid'] for video in v.get_videos(cat,1, 100).get('videos', []) ]
    print len(vids)
    return vids

def remove(pic):
    try:
        os.remove(pic + ".png")
    except Exception as e:
        print e
    

    
bg_cleanup()
