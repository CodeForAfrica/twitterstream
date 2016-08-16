"""
Stream listener
"""
import tweepy
import logging
import gspread
import json
import memcache
from celery import Celery
from twitterstream import config
from oauth2client.client import SignedJwtAssertionCredentials
from twitterstream.config import TW_AUTH_CREDENTIALS, GSPREAD_CONFIG, CACHE_HOST, SHEET_ID, USER_CAP
from twitterstream.config import LOGGING
import tweepy, logging

BROKER = "amqp://%s:%s@%s/%s" % (
        config.RABBITMQ["credentials"].split(",")[0].strip(),
        config.RABBITMQ["credentials"].split(",")[1].strip(),
        config.RABBITMQ["host"].strip(),
        config.RABBITMQ["vhost"].strip()
        )
PRINCIPLE_TW_HANDLE = 'cfktwstream'
LOGGERS = {}
celery_app = Celery(config.RABBITMQ["queue"], broker=BROKER)

def get_cache():
    return memcache.Client([CACHE_HOST], debug=1, socket_timeout=3)

def get_api(auth_only=False):
    """
    returns authenticated API object
    """
    try:
        creds = TW_AUTH_CREDENTIALS.get(PRINCIPLE_TW_HANDLE)
        auth = tweepy.OAuthHandler(creds['consumer_key'], creds['consumer_secret'])
        auth.set_access_token(creds['access_token_key'], creds['access_token_secret'])
        if auth_only:
            return auth
        api = tweepy.API(auth_handler=auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        return api
    except Exception, err:
        api_err = 'Cannot create API object: {}'.format(str(err))
        raise err


def epoch_to_date(time_in_epoch):
    """
    convert time in epoch to formatted datetime
    """
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time_in_epoch))


def check_rate_limits(endpoint="/statuses/show/:id"):
    '''
    '''
    try:
        tw = get_api()
        resp = tw.rate_limit_status()
        limits = resp['resources']['statuses'][endpoint]
        seconds_to_reset = limits['reset'] - time.time()
        print "{remaining} out of {limit} | Resetting in %d seconds".format(**limits) % int(seconds_to_reset)
        limits['seconds_to_reset'] = seconds_to_reset
        return limits

    except Exception, err:
        print "ERROR: Cannot get rate limits - %s" % str(err)


class Listener(tweepy.StreamListener):
    """
    instance of tweepy's StreamListener
    """
    def __init__(self,):
        tweepy.StreamListener.__init__(self)
        self.rowcount = 1
        self.r = GSPREADCLIENT 

    def on_data(self, status):
        """
        do this when a status comes in
        """
        try:
            payload = json.loads(status)
            #payload["text"].encode("utf-8")
            #payload["user"]["screen_name"].encode("utf-8")
            logging.info("{id} - {created_at} - %s - {text}".format(**payload) % payload["user"]["screen_name"])
            publish.delay(payload, self.r, self.rowcount)

            self.rowcount += 1
            if self.rowcount >= USER_CAP:
                logging.debug("Enough for now. Closing stream...")
                return False

        except Exception, err:
            logging.error('on_data -- {}'.format(str(err)))


    
    def keep_alive(self,):
        logging.info("Heartbeat")

    def on_limit(self, track):
        logging.debug("WARNING: Rate limits: %s" % track)
    
    def on_dropped_connection(self,):
        """
        do this when Twitter closes connection
        """
        print "You probably need to restart me"

    
    def on_error(self, status_code):
        """
        handles errors
        """
        if int(status_code) == 420:
            # handle rate limiting
            return False


class Rows(object):
    def __init__(self, sheet_id, worksheet="Sheet1"):
        #self.logger = logger
        self.scope = "https://spreadsheets.google.com/feeds"
        self.sheet_id = sheet_id
        self.worksheet = worksheet
        self.writer = self._get_sheet()

    def _get_sheet(self):
        try:
            print "AUTHENTICATING *********"
            json_key = json.load(open(GSPREAD_CONFIG))
            credentials = SignedJwtAssertionCredentials(
                    json_key['client_email'],
                    json_key['private_key'].encode(),
                    self.scope)
            gc = gspread.authorize(credentials)
            sheet = gc.open_by_key(self.sheet_id)
            worksheet = sheet.worksheet(self.worksheet)
            return worksheet
        except Exception, err:
            #self.logger.error("Cannot open spreadsheet: %s" % str(err))
            print "Cannot open spreadsheet: %s" % str(err)
            raise err

GSPREADCLIENT = Rows(SHEET_ID, worksheet="Sheet2")._get_sheet()


@celery_app.task(name="twitterstream.streaming.listener.publish")
def publish(payload, gspread_client, rownumber):
    geo = payload.get("geo")
    if not geo:
        geo = dict(coordinates=[0,0])
    gspread_client.update_acell("A%s" % str(rownumber), payload["created_at"])
    gspread_client.update_acell("B%s" % str(rownumber), payload["user"]["screen_name"])
    gspread_client.update_acell("C%s" % str(rownumber), payload["text"])
    gspread_client.update_acell("D%s" % str(rownumber), geo.get("coordinates")[0])
    gspread_client.update_acell("E%s" % str(rownumber), geo.get("coordinates")[1])
    print "Updated worksheet - %s" % payload["id"]


class Streamer(object):

    def __init__(self, session_id):
        self.stream_listener = Listener()
        self.stream_id = session_id
        #self.logger = logger


    def start_user_stream(self, users=[]):
        '''
        start stream tracking user
        '''
        tweepy.Stream(get_api(auth_only=True), self.stream_listener, session_id=self.stream_id).filter(
                        follow=users).on_closed(
                                self.stream_listener.on_dropped_connection())
        #self.logger.info("Stream %s started." % self.stream_id)

    def start_hashtag_stream(self, hashtags=[]):
        '''
        start stream following hashtag
        '''
        tweepy.Stream(get_api(auth_only=True), self.stream_listener, session_id=self.stream_id).filter(track=hashtags)
        #self.logger.info("Stream %s started." % self.stream_id)


def main(session_id, stream_type, filters=[]):
    '''
    @stream_type:   <user / hashtag>
    @users:         <list> of users     (M when `stream_type` is 'user')
    @hashtags:      <list> of hashtags  (M when `stream_type` is 'hashtag')
    '''
    try:
        assert stream_type in ["hashtag", "user"]
        print "Creating logger... %s - %s - %s" % (session_id, stream_type, filters)
        logging.basicConfig(filename=LOGGING['location'] % stream_type,
                level=LOGGING['level'],
                format=LOGGING['format'])
        logging.info("Starting %s stream against %s [ %s ]" % (stream_type, filters, session_id))


        stream = Streamer(session_id)
        if stream_type == "user":
            stream.start_user_stream(filters.split(","))
        elif stream_type == "hashtag":
            print filters.split(",")
            print "==" * 20
            stream.start_hashtag_stream(filters.split(","))

    except AssertionError:
        print "ERROR: Invalid stream_type %s. Expects: ['user', 'hashtag']" % stream_type
        raise AssertionError
    except Exception, err:
        print "ERROR: %s" % err
        raise err


if __name__ == "__main__":
    pass
