import urllib2, urllib, simplejson as json, time, re, sys
from pymongo import MongoClient

MAIN_REDDITS = ["hot", "top", "controversial"]

def get_videos(source, pages):
    conn = MongoClient()
    db = conn.Youddit
    coll = db.main_reddits
    
    videos = []
    url = "http://www.reddit.com/%s.json"%(source)
    after = ''
    for page in range(0, pages):
        params = urllib.urlencode({'limit':100, 'after': after})
        request = urllib2.Request(url + '?' + params)
        request.add_header('User-Agent', 'reddit video stream youddit')
        request.add_header('Content-Type', 'application/json')
        
        response = urllib2.urlopen(request)
        response = json.loads(response.read())
        if len(response['data']['children']) == 0:
            break
        for reddit in response['data']['children']:
            if reddit['data']['domain'] == "youtube.com":
                r = reddit['data']
                ytURL = r['url']
                
                # extracting the video id from url
                try:
                    m = re.search('v=', ytURL)
                    endInd = m.end()
                except Exception, e:
                    sys.stderr.write("No v= pattern found in YT url" + str(e) + '\n')        
                    continue

                # appending the video data to the videos list
                videos.append({ "title": r['title'],
                                "url": r['url'],
                                "subreddit": r['subreddit'],
                                "id": r['id'],
                                "score": r['score'],
                                "permalink": r['permalink'],
                                "created": r['created'],
                })

            after = response['data']['after']
        time.sleep(1)
    # Update db
    coll.update({"name": source}, {'$set': {'videos': videos, 'updated_at': time.time()}})
    conn.close()

    return videos

# Update the main reddits
# This should be called in a cron job
def update():
    for r in MAIN_REDDITS:
        print r
        get_videos(r, 30)


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'update':
        update()
        print 'Done'


