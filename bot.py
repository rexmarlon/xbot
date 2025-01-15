import os
import random
import time
import openai
import tweepy
import sys

# ENV-Variablen aus GitHub Secrets
CONSUMER_KEY = os.getenv("API_KEY")
CONSUMER_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Auth v1.1 (klassisch)
auth = tweepy.OAuth1UserHandler(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET,
)

api = tweepy.API(auth)  # <-- v1.1-API
openai.api_key = OPENAI_API_KEY

CHAPTER_FILE = "current_chapter.txt"
CHAPTER_DIRECTORY = "."
IMAGES_DIRECTORY = "images"

def load_current_chapter():
    print(f"Lade Kapitelnummer aus {CHAPTER_FILE}")
    sys.stdout.flush()
    if os.path.exists(CHAPTER_FILE):
        with open(CHAPTER_FILE, "r", encoding="utf-8") as file:
            content = file.read().strip()
            print(f"Inhalt der geladenen Datei: {content}")
            sys.stdout.flush()
            return int(content)
    print("Datei nicht gefunden. Starte mit Kapitel 1.")
    sys.stdout.flush()
    return 1

def save_current_chapter(chapter_number):
    print(f"Speichere Kapitelnummer: {chapter_number} in {CHAPTER_FILE}")
    sys.stdout.flush()
    try:
        with open(CHAPTER_FILE, "w", encoding="utf-8") as file:
            file.write(str(chapter_number))
        with open(CHAPTER_FILE, "r", encoding="utf-8") as file:
            content = file.read().strip()
        print(f"Inhalt der Datei nach dem Schreiben: {content}")
        sys.stdout.flush()
    except IOError as e:
        print(f"Fehler beim Schreiben in {CHAPTER_FILE}: {e}")
        sys.stdout.flush()

def read_chapter_content(chapter_number):
    chapter_filename = os.path.join(CHAPTER_DIRECTORY, f"Kapitel-{chapter_number}.txt")
    if os.path.exists(chapter_filename):
        with open(chapter_filename, "r", encoding="utf-8") as file:
            return file.read()
    else:
        print(f"Kapitel {chapter_number} wurde nicht gefunden.")
        sys.stdout.flush()
        return None

def get_random_image_path():
    try:
        images = [f for f in os.listdir(IMAGES_DIRECTORY) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        if not images:
            print("Keine Bilder im Verzeichnis gefunden.")
            sys.stdout.flush()
            return None
        random_image = random.choice(images)
        image_path = os.path.join(IMAGES_DIRECTORY, random_image)
        print(f"Zufällig ausgewähltes lokales Bild: {image_path}")
        sys.stdout.flush()
        return image_path
    except Exception as e:
        print(f"Fehler beim Abrufen des Bildes: {e}")
        sys.stdout.flush()
        return None

def post_thread(whitepaper_content):
    print("Starte Generierung des Threads...")
    sys.stdout.flush()

    prompt = f"""
    You are a creative social media manager for Huntmon. Based on the following content from the whitepaper:
    {whitepaper_content}

    Write a longer, engaging text (max ~270 characters).
    Include relevant hashtags: #Huntmon, #Matic, #ETH, #P2E, #ARGaming, etc.
    """

    try:
        # GPT-Aufruf
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
        sys.stdout.flush()

        # In 275-Char-Tweets aufteilen
        tweets = []
        words = long_text.split()
        current_tweet = ""
        for word in words:
            if len(current_tweet) + len(word) + 1 <= 275:
                current_tweet += (" " if current_tweet else "") + word
            else:
                tweets.append(current_tweet)
                current_tweet = word
        if current_tweet:
            tweets.append(current_tweet)

        # Bild hochladen (v1.1)
        image_path = get_random_image_path()
        if image_path:
            try:
                media = api.media_upload(image_path)
            except Exception as e:
                print(f"Fehler beim Hochladen des lokalen Bildes: {e}")
                sys.stdout.flush()
                media = None
        else:
            media = None

        # Tweets posten (v1.1)
        # Thread -> jeder Tweet "reply" auf den vorherigen
        reply_to = None
        for i, tweet in enumerate(tweets):
            for attempt in range(3):  # Retry logic
                try:
                    if i == 0:
                        # Beim ersten Tweet ggf. mit Bild
                        if media:
                            status = api.update_status(
                                status=f"{tweet} ({i+1}/{len(tweets)})",
                                media_ids=[media.media_id_string]
                            )
                        else:
                            status = api.update_status(
                                status=f"{tweet} ({i+1}/{len(tweets)})"
                            )
                        reply_to = status.id
                    else:
                        status = api.update_status(
                            status=f"{tweet} ({i+1}/{len(tweets)})",
                            in_reply_to_status_id=reply_to,
                            auto_populate_reply_metadata=True
                        )
                        reply_to = status.id

                    print(f"Tweet {i+1} posted: {status.id}")
                    sys.stdout.flush()
                    time.sleep(10)
                    break
                except tweepy.TweepyException as ex:
                    print(f"Error posting tweet {i+1}: {ex}")
                    sys.stdout.flush()
                    if "429" in str(ex):
                        # Rate limit -> 15 Minuten Pause
                        print("Rate limit reached. Retrying in 15 minutes.")
                        for _ in range(15):
                            print("Sleeping 1 minute...")
                            sys.stdout.flush()
                            time.sleep(60)
                    else:
                        if attempt < 2:
                            print("Retrying in 10s...")
                            sys.stdout.flush()
                            time.sleep(10)
                        else:
                            print("Aborting after 3 attempts.")
                            sys.stdout.flush()
                            return
    except Exception as e:
        print("Error generating or posting the thread:", e)
        sys.stdout.flush()

def post_tweet():
    print("Start: Post-Tweet-Prozess")
    sys.stdout.flush()

    chapter_number = load_current_chapter()
    whitepaper_content = read_chapter_content(chapter_number)

    if not whitepaper_content:
        print(f"Chapter {chapter_number} not found. Resetting to chapter 1.")
        sys.stdout.flush()
        chapter_number = 1
        save_current_chapter(chapter_number)
        whitepaper_content = read_chapter_content(chapter_number)

    if not whitepaper_content:
        print("No content available. Aborting process.")
        sys.stdout.flush()
        return

    post_thread(whitepaper_content)
    # Wenn alles geklappt hat, Kapitelnummer hochzählen
    new_chapter = chapter_number + 1
    save_current_chapter(new_chapter)

if __name__ == "__main__":
    post_tweet()
