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

# Pfad zur Datei, in der das aktuelle Kapitel gespeichert wird
CHAPTER_FILE = "current_chapter.txt"
CHAPTER_DIRECTORY = "."
IMAGES_DIRECTORY = "images"

# Aktuelles Kapitel laden oder mit Kapitel 1 starten
def load_current_chapter():
    print(f"Lade Kapitelnummer aus {CHAPTER_FILE}")
    if os.path.exists(CHAPTER_FILE):
        with open(CHAPTER_FILE, "r") as file:
            content = file.read().strip()
            print(f"Inhalt der geladenen Datei: {content}")
            return int(content)
    print("Datei nicht gefunden. Starte mit Kapitel 1.")
    return 1

# Aktuelles Kapitel speichern
def save_current_chapter(chapter_number):
    print(f"Speichere Kapitelnummer: {chapter_number} in {CHAPTER_FILE}")
    try:
        with open(CHAPTER_FILE, "w") as file:
            file.write(str(chapter_number))
        with open(CHAPTER_FILE, "r") as file:
            content = file.read().strip()
        print(f"Inhalt der Datei nach dem Schreiben: {content}")
    except IOError as e:
        print(f"Fehler beim Schreiben in {CHAPTER_FILE}: {e}")

# Kapitelinhalt aus einer Datei laden
def read_chapter_content(chapter_number):
    chapter_filename = os.path.join(CHAPTER_DIRECTORY, f"Kapitel-{chapter_number}.txt")
    if os.path.exists(chapter_filename):
        with open(chapter_filename, "r", encoding="utf-8") as file:
            return file.read()
    else:
        print(f"Kapitel {chapter_number} wurde nicht gefunden.")
        return None

# Zufälliges Bild aus dem Verzeichnis auswählen
def get_random_image():
    try:
        images = [f for f in os.listdir(IMAGES_DIRECTORY) if f.endswith(('.png', '.jpg', '.jpeg'))]
        if not images:
            print("Keine Bilder im Verzeichnis gefunden.")
            return None
        random_image = random.choice(images)
        print(f"Zufällig ausgewähltes Bild: {random_image}")
        return os.path.join(IMAGES_DIRECTORY, random_image)
    except Exception as e:
        print(f"Fehler beim Auswählen eines Bildes: {e}")
        return None

# Bild hochladen und ID zurückgeben
def upload_image(file_path):
    try:
        media = client.media_upload(filename=file_path)
        print(f"Bild hochgeladen: {media.media_id}")
        return media.media_id
    except Exception as e:
        print(f"Fehler beim Hochladen des Bildes: {e}")
        return None

# GPT-gestütztes Thread-Generieren und Posten
def post_thread(whitepaper_content):
    # Generiere den langen Text basierend auf dem Whitepaper
    prompt = f"""
    You are a creative social media manager for Huntmon. Based on the following content from the whitepaper:
    {whitepaper_content}

    Write a longer, engaging text that can be split into multiple tweets. Each tweet should:
    - Be informative.
    - Spark curiosity among readers.
    - Use varied and engaging language.
    - Include relevant hashtags like #Huntmon, #Matic, #ETH, #P2E, #ARGaming, or others that are currently viral, attract attention, or are niche-specific.

    Make sure each segment is less than 280 characters and forms a logical part of the thread.
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
        print(f"Generated long text: {long_text}")

        # Split the long text into logical sentences and ensure each tweet is <280 characters
        tweets = []
        current_tweet = ""
        for sentence in long_text.split("."):
            sentence = sentence.strip() + "."
            if len(current_tweet) + len(sentence) <= 275:
                current_tweet += " " + sentence
            else:
                tweets.append(current_tweet.strip())
                current_tweet = sentence
        if current_tweet:
            tweets.append(current_tweet.strip())

        # Poste die Tweets als Thread
        previous_tweet_id = None
        posted_tweets = set()
        for i, tweet in enumerate(tweets):
            if tweet in posted_tweets:
                print(f"Tweet {i+1} skipped as it is duplicate: {tweet}")
                continue
            posted_tweets.add(tweet)

            for attempt in range(3):  # Retry logic
                try:
                    # Select a random image and upload it
                    image_path = get_random_image()
                    media_id = upload_image(image_path) if image_path else None

                    if previous_tweet_id:
                        response = client.create_tweet(text=tweet, in_reply_to_tweet_id=previous_tweet_id, media_ids=[media_id] if media_id else None)
                    else:
                        response = client.create_tweet(text=tweet, media_ids=[media_id] if media_id else None)
                    print(f"Tweet {i+1} posted:", response.data)
                    previous_tweet_id = response.data.get("id")
                    break
                except tweepy.errors.Forbidden as e:
                    print(f"Error posting tweet {i+1}: {e}")
                    if attempt < 2:
                        print("Retrying...")
                        time.sleep(2)
                    else:
                        print("Aborting after 3 attempts.")
    except Exception as e:
        print("Error generating or posting the thread:", e)

# Hauptfunktion: Tweet posten
def post_tweet():
    chapter_number = load_current_chapter()
    whitepaper_content = read_chapter_content(chapter_number)

    if not whitepaper_content:
        print(f"Chapter {chapter_number} not found. Resetting to chapter 1.")
        chapter_number = 1
        save_current_chapter(chapter_number)
        whitepaper_content = read_chapter_content(chapter_number)

    if not whitepaper_content:
        print("No content available. Aborting process.")
        return

    # Choose between single tweet or thread
    is_long_tweet = True  # Set to False for single tweets
    if is_long_tweet:
        post_thread(whitepaper_content)
    else:
        tweet = generate_tweet(whitepaper_content)
        try:
            # Select a random image and upload it
            image_path = get_random_image()
            media_id = upload_image(image_path) if image_path else None

            response = client.create_tweet(text=tweet, media_ids=[media_id] if media_id else None)
            print("Tweet successfully posted:", response.data)
            save_current_chapter(chapter_number + 1)
        except tweepy.errors.Forbidden as e:
            print("Error posting tweet:", e)
            print("Details:", e.response.text)
        except Exception as e:
            print("An unexpected error occurred:", e)

# Bot ausführen
if __name__ == "__main__":
    post_tweet()
