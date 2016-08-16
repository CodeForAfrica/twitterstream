consume:
	celery -A twitterstream.streaming.listener.celery_app  worker -c 5 -l DEBUG -f /var/log/twitterstream-consumer.log --pidfile celery.pid &

stream:
	python client.py

testwebserver:
	python core.py

webserver:
	gunicorn --workers 3 --bind unix:twitterstream.sock --log-level debug --log-file logs/gunicorn.log web:app &
