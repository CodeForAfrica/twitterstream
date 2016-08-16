"""
Stream listener
"""
import tweepy
import logging
import gspread
import json
import memcache
from oauth2client.client import SignedJwtAssertionCredentials
from twitterstream.config import TW_AUTH_CREDENTIALS, GSPREAD_CONFIG, CACHE_HOST, SHEET_ID, USER_CAP

PRINCIPLE_TW_HANDLE = 'cfktwstream'

LOGGERS = {}



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
            '''
            payload = dict(
                      request_id=status.id,
                      created_at=status.created_at,
                      sender_id=status.user.id,
                      username=status.user.screen_name,
                      avatar=status.user.profile_image_url.replace('_normal', ''),
                      message=str(status.text.encode('utf-8')),
                      saved="",
                      source=status.source,
                      )
                      '''
            payload = json.loads(status)
            #payload["text"].encode("utf-8")
            #payload["user"]["screen_name"].encode("utf-8")
            logging.info("{id} - {created_at} - %s - {text}".format(**payload) % payload["user"]["screen_name"])
            self.r.update_acell("A%s" % str(self.rowcount), payload["created_at"])
            self.r.update_acell("B%s" % str(self.rowcount), payload["user"]["screen_name"])
            self.r.update_acell("C%s" % str(self.rowcount), payload["text"])
            logging.info("Updated worksheet - %s" % payload["id"])

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

GSPREADCLIENT = Rows(SHEET_ID)._get_sheet()

if __name__ == "__main__":
    pass
