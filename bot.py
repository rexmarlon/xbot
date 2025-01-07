import tweepy
import time

# Twitter API-Schlüssel
API_KEY = "vsi6YMdcMXbsaBLvBs3qQTnIE"
API_SECRET = "cXEUjBboAJrLWmNMzwZeaihcAdXeA9nZOg4CP2Ps0ETrQnlgQG"
ACCESS_TOKEN = "1863572815405887488-pvQDFDfEsmdmwqxzvMgQfgfYz594eN"
ACCESS_SECRET = "U9eszFrb5hF2mvBv8552ige3GFKqJDAnIak2XkcQhNneZ"

# Twitter API authentifizieren
auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

# Funktion, um Tweets zu posten
def post_tweet():
    try:
        tweet = "Hallo Welt! Das ist ein automatischer Tweet! 🌍"
        api.update_status(tweet)
        print("Tweet gepostet!")
    except Exception as e:
        print("Fehler:", e)

# Bot ausführen (alle 10 Minuten ein Tweet posten)
while True:
    post_tweet()
    time.sleep(600)  # 600 Sekunden = 10 Minuten
