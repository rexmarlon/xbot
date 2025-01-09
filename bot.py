import tweepy
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

client = tweepy.Client(
    bearer_token=os.getenv("BEARER_TOKEN"),
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_SECRET"),
)

def generate_tweet(...):
    # ... GPT-Logik ...
    return tweet_text

def post_tweet():
    tweet_text = generate_tweet(...)
    response = client.create_tweet(text=tweet_text)
    print("Tweet erfolgreich gepostet:", response.data)

if __name__ == "__main__":
    post_tweet()
