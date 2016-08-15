from twitterstream.streaming import listener
from twitterstream.config import LOGGING
import tweepy, logging, uuid, sys


class Streamer(object):

    def __init__(self, logger=None):
        self.stream_listener = listener.Listener()
        self.stream_id = str(uuid.uuid4())
        self.logger = logger


    def start_user_stream(self, users=[]):
        '''
        start stream tracking user
        '''
        tweepy.Stream(
                listener.get_api(auth_only=True), self.stream_listener).filter(
                        follow=users).on_closed(
                                self.stream_listener.on_dropped_connection())
        #self.logger.info("Stream %s started." % self.stream_id)

    def start_hashtag_stream(self, hashtags=[]):
        '''
        start stream following hashtag
        '''
        tweepy.Stream(listener.get_api(auth_only=True), self.stream_listener).filter(track=hashtags)
        #self.logger.info("Stream %s started." % self.stream_id)


def main(stream_type, users=[], hashtags=[]):
    '''
    @stream_type:   <user / hashtag>
    @users:         <list> of users     (M when `stream_type` is 'user')
    @hashtags:      <list> of hashtags  (M when `stream_type` is 'hashtag')
    '''
    try:
        print "Creating logger..."
        logging.basicConfig(filename=LOGGING['location'] % stream_type,
                level=LOGGING['level'],
                format=LOGGING['format'])
        logging.info("Starting %s stream against %s %s" % (stream_type, users, hashtags))

        stream = Streamer(logging)
        if stream_type == "user":
            stream.start_user_stream(users)
        elif stream_type == "hashtag":
            stream.start_hashtag_stream(users)

    except AssertionError:
        print "ERROR: Invalid stream_type %s. Expects: ['user', 'hashtag']" % stream_type
        raise AssertionError
    except Exception, err:
        print "ERROR: %s" % err
        raise err



if __name__ == "__main__":
    stream_type = sys.argv[1]
    filters = sys.argv[2]
    main(stream_type, filters)
