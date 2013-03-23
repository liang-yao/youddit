from pymongo import MongoClient
from time import time
"""
Schema:

Subreddits:
    Stores general info on subreddits

    {
        "name":
        "updated_at":
        "cat": category [0, 1, 2]
        "vids": [] ids of videos 
    }

    Index: { name: 1, cat: 1}

Videos:
    
    {
        "_id": reddit id
        "subreddit":
        "vid": video id
        "provider": 
        "score":
        "permalink":
        "title":
        "created":
    }

    Index: {subreddit, category}
"""


def create():
    conn = MongoClient()
    db = conn.Youddit
    subreddits = db.subreddits
    videos = db.videos
    videos.create_index([ ("subreddit", 1) ])
    subreddits.create_index([ ("name", 1), ("cat", 1 ) ])
       
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

