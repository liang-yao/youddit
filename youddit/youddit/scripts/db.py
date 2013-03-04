from pymongo import MongoClient
from time import time

def create():
    conn = MongoClient()
    db = conn.Youddit
    subreddits = db.subreddits
    main_reddits = db.main_reddits
    subreddits.create_index([("name", 1)])

    # Create main reddits
    for r in ["hot", "top", "controversial"]:
        main_reddits.insert({ "name" : r,
                             "updated_at" : 0,
                             "videos" : []
        })
        

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

