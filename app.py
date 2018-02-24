import feedparser
from flask import Flask
import os
import random
import requests
import time


app = Flask(__name__)

BASE_URL = "https://slack.com/api/chat.postMessage"
TOKEN = os.environ["TOKEN"]
CHANNEL = os.environ["CHANNEL"] 
THTS = os.environ["THTS"]
NAME = "Geek bot"
ICON_URL = os.environ["ICON_URL"]

RSS_FEEDS = [
    {"name": u"Gizmodo", "url": "http://feeds.gizmodo.jp/rss/gizmodo/index.xml"},
    {"name": u"GIGAZINE", "url": "http://feed.rssad.jp/rss/gigazine/rss_2.0"}
]
RSS_MAX = 1


def post_slack(payload):
    try:
        requests.post(BASE_URL, payload)
    except Exception as e:
        return "err"
    return ""

def get_article():
    data = []
    for i in range(RSS_MAX):
        kind = random.randint(0, len(RSS_FEEDS) - 1)
        feed = feedparser.parse(RSS_FEEDS[kind]["url"])
        choice = random.randint(0, len(feed.entries) - 1)
        
        try:
            article = feed.entries[choice]
            data.append({
                "link": article.link,
                "title": article.title,
                "source": RSS_FEEDS[kind]["name"]
            })
        except Exception as e:
            print(str(e))
            return None
        finally:
            time.sleep(1)
    return data

def create_msg(data):
    if data is None:
        return None

    msg = "記事だよ～\n"
    for d in data:
        msg += "『<{}|{}>』({}から)\n".format(d["link"], d["title"], d["source"])
    return msg
    

@app.route("/")
def index():
    return "hello"

@app.route("/incoming", methods=["GET"])
def bot_incoming():
    article = get_article()
    msg = create_msg(article)

    if msg is None:
        return "err"

    payload = {
        "token": TOKEN,
        "channel": CHANNEL,
        "username": NAME,
        "icon_url": ICON_URL,
        "text": msg,
        "thread_ts": THTS
    }
    return post_slack(payload)

@app.errorhandler(404)
def page_not_found(e):
    return ";-("

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.debug = True
    app.run(port=port)

