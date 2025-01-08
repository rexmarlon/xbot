import tweepy
import os

# Debug: Zeige die Umgebungsvariablen
print("BEARER_TOKEN:", os.getenv("BEARER_TOKEN"))
print("API_KEY:", os.getenv("API_KEY"))
print("API_SECRET:", os.getenv("API_SECRET"))
print("ACCESS_TOKEN:", os.getenv("ACCESS_TOKEN"))
print("ACCESS_SECRET:", os.getenv("ACCESS_SECRET"))

# Twitter API-Schlüssel aus Umgebungsvariablen laden
client = tweepy.Client(
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_SECRET"),
)

# Versuche, einen Tweet zu posten
try:
    response = client.create_tweet(text="Hallo von der v2 API!")
    print("Tweet erfolgreich:", response)
except tweepy.errors.Unauthorized as e:
    print("Fehler: Unauthorized (401). Bitte überprüfe die API-Schlüssel und Berechtigungen.")
except Exception as e:
    print("Ein anderer Fehler ist aufgetreten:", e)
