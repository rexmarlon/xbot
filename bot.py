import tweepy
import openai
import os
import textwrap
import time
import random

# OpenAI API-Key laden
openai.api_key = os.getenv("OPENAI_API_KEY")

# Twitter API-Schlüssel aus Umgebungsvariablen laden
client = tweepy.Client(
    bearer_token=os.getenv("BEARER_TOKEN"),
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_SECRET"),
)

# API für Media-Uploads initialisieren
auth = tweepy.OAuth1UserHandler(
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_SECRET"),
)
api = tweepy.API(auth)

# Pfad zur Datei, in der das aktuelle Kapitel gespeichert wird
CHAPTER_FILE = "current_chapter.txt"
CHAPTER_DIRECTORY = "."
IMAGES_DIRECTORY = "images"

# Aktuelles Kapitel laden oder mit Kapitel 1 starten
def load_current_chapter():
    if os.path.exists(CHAPTER_FILE):
        with open(CHAPTER_FILE, "r") as file:
            return int(file.read().strip())
    return 1

# Aktuelles Kapitel speichern
def save_current_chapter(chapter_number):
    with open(CHAPTER_FILE, "w") as file:
        file.write(str(chapter_number))

# Kapitelinhalt aus einer Datei laden
def read_chapter_content(chapter_number):
    chapter_filename = os.path.join(CHAPTER_DIRECTORY, f"Kapitel-{chapter_number}.txt")
    if os.path.exists(chapter_filename):
        with open(chapter_filename, "r", encoding="utf-8") as file:
            return file.read()
    return None

# Zufälliges Bild aus dem Verzeichnis auswählen
def get_random_image():
    images = [f for f in os.listdir(IMAGES_DIRECTORY) if f.endswith(('.png', '.jpg', '.jpeg'))]
    return os.path.join(IMAGES_DIRECTORY, random.choice(images)) if images else None

# Bild hochladen und ID zurückgeben
def upload_image(file_path):
    try:
        media = api.media_upload(filename=file_path)
        return media.media_id
    except Exception as e:
        print(f"Fehler beim Hochladen des Bildes: {e}")
        return None

# GPT-gestütztes Thread-Generieren und Posten
def post_thread(whitepaper_content):
    prompt = f"""
    You are a creative social media manager for Huntmon. Based on the following content from the whitepaper:
    {whitepaper_content}
    Write a longer, engaging text that can be split into multiple tweets. Each tweet should:
    - Be informative.
    - Spark curiosity among readers.
    - Use varied and engaging language.
    - Include relevant hashtags.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative social media assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7,
        )
        long_text = response["choices"][0]["message"]["content"].strip()

        tweets = textwrap.wrap(long_text, width=275, break_long_words=False)
        previous_tweet_id = None

        for i, tweet in enumerate(tweets):
            for attempt in range(3):
                try:
                    if i == 0:
                        image_path = get_random_image()
                        media_id = upload_image(image_path) if image_path else None
                        response = client.create_tweet(text=f"{tweet} (1/{len(tweets)})", media_ids=[media_id] if media_id else None)
                    else:
                        response = client.create_tweet(text=f"{tweet} ({i+1}/{len(tweets)})", in_reply_to_tweet_id=previous_tweet_id)
                    previous_tweet_id = response.data["id"]
                    break
                except tweepy.errors.TooManyRequests:
                    print("Rate limit reached. Sleeping for 15 minutes.")
                    time.sleep(900)
                except Exception as e:
                    print(f"Error posting tweet {i+1}: {e}")
    except Exception as e:
        print(f"Error generating thread: {e}")

# Hauptfunktion
def post_tweet():
    chapter_number = load_current_chapter()
    whitepaper_content = read_chapter_content(chapter_number)

    if whitepaper_content:
        post_thread(whitepaper_content)
        save_current_chapter(chapter_number + 1)
    else:
        print("No content available.")

if __name__ == "__main__":
    post_tweet()
