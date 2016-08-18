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

GSPREAD_CONFIG = os.getenv("GSPREAD_AUTH")

CACHE_HOST = os.getenv("MEMCACHE_HOST")

SHEET_ID = "1H9lu9lrn3uu2vpX2bYadMp--LmfyrX257NMVHLJW3v0"

USER_CAP = 10

RABBITMQ = {}
RABBITMQ["host"] = os.getenv("RABBITMQ_HOST")
RABBITMQ["vhost"] = os.getenv("RABBITMQ_VHOST")
RABBITMQ["queue"] = os.getenv("RABBITMQ_QUEUE")
RABBITMQ["credentials"] = os.getenv("RABBITMQ_CREDENTIALS")

RECAPTCHA = {}
RECAPTCHA["verify_url"] = "https://www.google.com/recaptcha/api/siteverify"
RECAPTCHA["secret_key"] = os.getenv("RECAPTCHA_KEY")

TIMEOUTS = {}
TIMEOUTS["recaptcha"] = 5
TIMEOUTS["googlesheets"] = 5
