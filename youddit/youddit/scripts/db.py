from pymongo import MongoClient
from time import time
"""
Schema:

Subreddits:
    Stores general info on subreddits

    {
        "name":
        "updated_at":
        "ver": version - Incremented each time the data is updated
    }

    Index: { name: 1 } 

Videos:
    
    {
        "rid": reddit id
        "subreddit":
        "cat": category
        "ver": version
        "vid": video id
        "provider": 
        "score":
        "permalink":
        "title":
        "created":
    }

    Index: {subreddit: 1, category: 1, ver: -1}
"""


def create():
    conn = MongoClient()
    db = conn.Youddit
    subreddits = db.subreddits
    videos = db.videos
    videos.create_index([ ("subreddit", 1), ("cat", 1), ("ver", -1) ])
    subreddits.create_index([("name", 1)])
       
def destroy():
    conn = MongoClient()
    conn.drop_database('Youddit')

def recreate():
    destroy()
    create()

if __name__ == "__main__":
    import sys
    if sys.argv[1] == "create":
        create()
    elif sys.argv[1] == "destroy":
        destroy()
    elif sys.argv[1] == "recreate":
        recreate()
    else:
        print "Options: create, destory, recreate"

