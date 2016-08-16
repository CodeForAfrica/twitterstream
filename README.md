# twitterstream
Stream content from a #hashtag into a csv / spreadsheet

## Requirements

* Twitter account, app, and auth credentials
* 




## Deployment
* Clone the repo:  `git clone https://github.com/codeforafricalabs/twitterstream`
* Install python dependencies: `pip install -r requirements.txt`
* Create new virtualenv and export env variables in `setup.env`
* 


## Usage
* For gspread, obtain OAuth2 credentials from Google Developers Console [using the guide here](http://gspread.readthedocs.org/en/latest/oauth2.html)
* Create a spreadsheet on Google Sheets and copy the document ID
![document-id.png](https://lh3.googleusercontent.com/9GV5nedO27vtnOhlnl4HfWwhf8H0Yt0zU9nG4r2dH42MhmQrQYXm1jIphndBLqtii7UDx9fewG080g=w1518-h74-no)
* Share the spreadsheet with the `client_email` on the JSON from the first step
* Access the web app at:
* Enter the hashtag / user to track and hit Enter
