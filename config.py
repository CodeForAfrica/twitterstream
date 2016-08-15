import os, logging

LOGGING = {}
LOGGING['location'] = 'logs/log-%s-twitterstream.log'
LOGGING['level'] = logging.DEBUG
LOGGING['format'] = '%(asctime)s : %(levelname)s: %(message)s'



TW_AUTH_CREDENTIALS = {}
# pylitwoops
TW_AUTH_CREDENTIALS['cfktwstream'] = {}
TW_AUTH_CREDENTIALS['cfktwstream']['consumer_key'] = os.getenv('TW_CONSUMER_KEY')
TW_AUTH_CREDENTIALS['cfktwstream']['consumer_secret'] = os.getenv('TW_CONSUMER_SECRET')
TW_AUTH_CREDENTIALS['cfktwstream']['access_token_key'] = os.getenv('TW_ACCESS_TOKEN_KEY')
TW_AUTH_CREDENTIALS['cfktwstream']['access_token_secret'] = os.getenv('TW_ACCESS_TOKEN_SECRET')


SENDER_ID = {}
SENDER_ID['cfktwstream'] = ''
