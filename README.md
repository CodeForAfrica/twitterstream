## Summary
`twitterstream` is a tool that streams real-time content from Twitter and channels it into a Google Spreadsheet. `twitterstream` can be started and controlled via a [web interface](https://twitterstream.codeforafrica.tech/), or the command line.

## Use case
For data wranglers, analysts, and developers, data on structured, open, and standard formats (such as `xls` or `csv`) is far more useful and malleable than unstructured sources.
Twitter is a great source of conversation, news, entertainment, etc.

The aim of this project is to make content on Twitter easily accessible for data analysts.


## Components
* Flask web app
* Streaming service: opens [streaming connection to Twitter](https://dev.twitter.com/streaming/overview), queues incoming content via a RabbitMQ broker.
* Celery consumer:  consumes messages from RabbitMQ and updates the spreadsheet

## Deployment and installation
* Clone the repo:  `git clone https://github.com/codeforafricalabs/twitterstream`
* Install python dependencies: `pip install -r requirements.txt`
* Create new virtualenv and export env variables in `setup.env`
* Obtain [Twitter dev authentication credentials](https://dev.twitter.com/oauth): consumer key, consumer secret, access token key, and access token secret
* Obtain OAuth2 credentials from Google Developers Console [using the guide here](http://gspread.readthedocs.org/en/latest/oauth2.html)
* Create a spreadsheet on Google Sheets and copy the document ID
![](https://lh3.googleusercontent.com/9GV5nedO27vtnOhlnl4HfWwhf8H0Yt0zU9nG4r2dH42MhmQrQYXm1jIphndBLqtii7UDx9fewG080g=w1518-h74-no)
* Share the spreadsheet with the `client_email` (obtained from the service account on [Google Developrs Console](http://gspread.readthedocs.org/en/latest/oauth2.html)) 
![](https://goo.gl/ZiWpk9)
* Paste the document ID into `twitterstream.config` as the `SHEET_ID`
![](https://goo.gl/93qNKs)
* Start the consumer:  `make consume`
* Start web component: `make testwebserver` for debug mode and `make webserver` for production
* Start streaming component: `make stream`


## Usage

* Access the web app at: https://twitterstream.codeforafrica.tech/
* Select the filter type: 'hashtag' or 'user'
* Enter the hashtag / user to track and hit `Run`
* Open your spreadsheet and watch the magic :raised_hands:


## Obligatory GIF
![](https://media.giphy.com/media/mE5AM0F8bSXMQ/giphy.gif)
