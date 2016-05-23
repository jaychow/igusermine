from __future__ import division
from database import Db
import MySQLdb as _mysql
from config import ig_config
from instagram import client
import urlparse
from instagram.bind import InstagramAPIError
import multiprocessing, sys, logging, time

reload(sys)
sys.setdefaultencoding("utf-8")


__author__ = 'jaychow'

class igMine:

    #API var
    apiLimit = 5000
    apiCurrent = 0
    clientPosition = 0
    clientLength = 0

    #mine var
    usernames = [
        'sex_on_water',
        'lavimeer',
        'vita_century'
    ]

    def __init__(self):
        self.ig_config = ig_config
        self.clientLength = len(ig_config)
        print self.clientLength

    def initDB(self):
        self.db = Db()
        self.db.connect()

    def initIg(self):
        pos = self.clientPosition
        self.api = client.InstagramAPI(
            client_id=self.ig_config[pos]['client_id'],
            client_secret=self.ig_config[pos]['client_secret']
        )

    def search(self, user_id, max_id):
        user = self.api.user(user_id)
        media_search = self.api.user_recent_media(user_id=user_id, count=35, max_id=max_id);
        return media_search

    def getUserId(self, username):
        user_search = self.api.user_search(username)
        return int(user_search[0].id)



programStartTime = time.time()

apiCall = 0
totalCounter = 0


miner = igMine()
miner.initDB()
miner.initIg()

def addImage(media, tags):
    try:
        miner.db.addImage('user_ig', media)
        for tag in tags:
                tagId = miner.db.getTagId(tag=tag.name)
                if(tagId):
                    if(not miner.db.tagRelationExists(tagId, media['id'])):
                        miner.db.addTagRelation(tagId, media['id'])
                else:
                    tagId = miner.db.addTag(tag.name)
                    if(not miner.db.tagRelationExists(tagId, media['id'])):
                        miner.db.addTagRelation(tagId, media['id'])
    except Exception as e:
        logging.warning(media['id'] + " - " + str(e))

    return
for username in miner.usernames:
    elapseTime = time.time()-programStartTime
    for username in miner.usernames:
        user_id = miner.getUserId(username)

        more_records = True
        max_id = None
        count = 0
        while(more_records):
            result = miner.search(user_id, max_id)
            if result[1] is not None:
                next = urlparse.parse_qs(result[1])
            else:
                next = False
            collection = result[0]

            for media in collection:
                ids = media.id.split('_')

                lat = 0
                lon = 0
                location = 0
                caption = ""

                if hasattr(media, 'location'):
                    if(hasattr(media.location.point,'latitude')):
                        lat = media.location.point.latitude
                    if(hasattr(media.location.point,'longitude')):
                        lon = media.location.point.longitude
                if media.caption is not None:
                    caption = media.caption.text.replace("'", r"\'")
                image = {
                    'id': ids[0],
                    'type': media.type,
                    'like_count': media.like_count,
                    'caption': caption,
                    'filter': media.filter,
                    'link': media.link,
                    'user_id': media.user.id,
                    'username': media.user.username,
                    'created_time': media.created_time,
                    'low_res': media.images['low_resolution'].url,
                    'thumbnail': media.images['thumbnail'].url,
                    'standard_res': media.images['standard_resolution'].url,
                    'lat': lat,
                    'lon': lon
                }

                print image

                addImage(image,media.tags)
                count += 1

            if next is not False:
                more_records = True
                max_id = str(next['max_id'][0])
            else:
                more_records = False



    '''
    try:
        percentDone = (totalCounter/totalIter)*100
        print "Elapse Time:" + elapseTime.__str__()
        print str(percentDone) + "%.... - " + str(apiCall) + " - " + str(timeStart)
        nextTime = timeStart - advInterval
        media_search = miner.search(max_timestamp = timeStart, min_timestamp = nextTime)

        processList = []

        for media in media_search:
            #print "-----" + str(miner.apiCurrent) + ' - entry: ' + media.id + " - " + media.link
            miner.apiCurrent += 1

            ids = media.id.split('_')

            lat = 0
            lon = 0
            location = 0
            caption = ""
            
            if(hasattr(media, 'location')):
                lat = media.location.point.latitude
                lon = media.location.point.longitude
            if(media.caption is not None):
                caption = media.caption.text.replace("'", r"\'")
            image = {
                'id': ids[0],
                'type': media.type,
                'like_count': media.like_count,
                'caption': caption,
                'filter': media.filter,
                'link': media.link,
                'user_id': media.user.id,
                'username': media.user.username,
                'created_time': media.created_time,
                'low_res': media.images['low_resolution'].url,
                'thumbnail': media.images['thumbnail'].url,
                'standard_res': media.images['standard_resolution'].url,
                'lat': lat,
                'lon': lon
            }

            addImage(image,media.tags)
        apiCall += 1
        totalCounter += 1
        timeStart = nextTime
    except InstagramAPIError as e:
        logging.warning(str(timeStart) + " - " + str(e.status_code) + ": " + e.error_type + " - " + e.error_message)
        print e.status_code
        if(e.status_code == '429'):
            if miner.clientPosition == miner.clientLength-1:
                miner.clientPosition == 0
            else:
                miner.clientPosition += 1
                miner.initIg()
                '''



