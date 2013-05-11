from pymongo import MongoClient
import os

def bg_cleanup():
    conn = MongoClient()
    db = conn.Youddit
    os.chdir("../../../static/bg")
    pics = [ p.split('.png')[0] for p in os.walk('.').next()[2]] 
    
    vids = db.videos.find({"rid": { "$nin": pics})
    print vids
    
bg_cleanup()
