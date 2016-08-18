"""
"""
import sys
import uuid
import memcache
from datetime import datetime
from twitterstream.streaming import start
from twitterstream import config

def spawn_child(stream_type, filters, sheet_id):
    #cache = memcache.Client([config.CACHE_HOST])
    session_id = str(uuid.uuid4())
    session = dict(
            stream_type = stream_type,
            filters = filters,
            sheet_id = sheet_id,
            created_at = datetime.now(),
            status = 'start'
            )
    #cache.set(session_id, session)
    start.main(sheet_id, stream_type, filters)


if __name__ == "__main__":
    #stream_type = sys.argv[1]
    #filters = sys.argv[2]
    #sheet_id = sys.argv[3]
    #spawn_child(stream_type, filters, sheet_id)
    spawn_child("hashtag", "olympics,rio,rudisha,phelps,bolt", "1ijKrMZ91REIGiowtdxfYPsRV6jikBv8_UCfLXPyz0-g")
    #spawn_child("user", "1237372231", config.SHEET_ID)
