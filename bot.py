import tweepy
import time

# Twitter API-Schlüssel
API_KEY = "dein_api_key"
API_SECRET = "dein_api_secret"
ACCESS_TOKEN = "dein_access_token"
ACCESS_SECRET = "dein_access_secret"

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
