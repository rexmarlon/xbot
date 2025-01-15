import tweepy
import openai
import os
import textwrap
import time
import random
import sys

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
    sys.stdout.flush()
    if os.path.exists(CHAPTER_FILE):
        with open(CHAPTER_FILE, "r") as file:
            content = file.read().strip()
            print(f"Inhalt der geladenen Datei: {content}")
            sys.stdout.flush()
            return int(content)
    print("Datei nicht gefunden. Starte mit Kapitel 1.")
    sys.stdout.flush()
    return 1

# Aktuelles Kapitel speichern
def save_current_chapter(chapter_number):
    print(f"Speichere Kapitelnummer: {chapter_number} in {CHAPTER_FILE}")
    sys.stdout.flush()
    try:
        with open(CHAPTER_FILE, "w") as file:
            file.write(str(chapter_number))
        with open(CHAPTER_FILE, "r") as file:
            content = file.read().strip()
        print(f"Inhalt der Datei nach dem Schreiben: {content}")
        sys.stdout.flush()
    except IOError as e:
        print(f"Fehler beim Schreiben in {CHAPTER_FILE}: {e}")
        sys.stdout.flush()

# Kapitelinhalt aus einer Datei laden
def read_chapter_content(chapter_number):
    chapter_filename = os.path.join(CHAPTER_DIRECTORY, f"Kapitel-{chapter_number}.txt")
    if os.path.exists(chapter_filename):
        with open(chapter_filename, "r", encoding="utf-8") as file:
            return file.read()
    else:
        print(f"Kapitel {chapter_number} wurde nicht gefunden.")
        sys.stdout.flush()
        return None

# Zufälligen Bild-Link aus dem GitHub-Repository auswählen
def get_random_image_url():
    base_url = "https://raw.githubusercontent.com/rexmarlon/xbot/main/images/"
    try:
        images = [f for f in os.listdir(IMAGES_DIRECTORY) if f.endswith(('.png', '.jpg', '.jpeg'))]
        if not images:
            print("Keine Bilder im Verzeichnis gefunden.")
            sys.stdout.flush()
            return None
        random_image = random.choice(images)
        print(f"Zufällig ausgewähltes Bild: {random_image}")
        sys.stdout.flush()
        return base_url + random_image
    except Exception as e:
        print(f"Fehler beim Auswählen eines Bildes: {e}")
        sys.stdout.flush()
        return None

# Rate-Limit-Status überprüfen
def check_rate_limit():
    try:
        print("Überprüfe Rate-Limit-Status...")
        sys.stdout.flush()
        # Fallback-Logik: Falls get_rate_limit_status nicht unterstützt wird
        print("Rate-Limit-Überprüfung nicht implementiert; Standard fort.")
        sys.stdout.flush()
    except Exception as e:
        print(f"Fehler beim Überprüfen des Rate-Limits: {e}")
        sys.stdout.flush()

# GPT-gestütztes Tweet-Generieren
def generate_tweet(whitepaper_content):
    print("Starte Generierung des Tweets...")
    sys.stdout.flush()
    prompt = f"""
    You are a creative social media manager for Huntmon. Based on the following content from the whitepaper:
    {whitepaper_content}

    Write a short, engaging tweet on this topic. The tweet should:
    - Be concise (less than 280 characters).
    - Spark curiosity among readers.
    - Include relevant hashtags like #Huntmon, #Matic, #ETH, #P2E, #ARGaming, or others that are currently viral, attract attention, or are niche-specific.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative social media assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.7,
        )
        tweet = response["choices"][0]["message"]["content"].strip()
        print(f"Generated tweet: {tweet}")
        sys.stdout.flush()
        return tweet
    except Exception as e:
        print("Error generating tweet with GPT:", e)
        sys.stdout.flush()
        return "Explore the innovative world of Huntmon! Join the adventure today. #Huntmon #Gaming"

# Hauptfunktion: Tweet posten
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

    # Check rate limit before posting
    check_rate_limit()

    tweet = generate_tweet(whitepaper_content)
    try:
        print("Versuche, den Tweet zu posten...")
        sys.stdout.flush()
        # Select a random image URL
        image_url = get_random_image_url()
        tweet_with_image = f"{tweet}\n\n{image_url}" if image_url else tweet

        response = client.create_tweet(text=tweet_with_image)
        print("Tweet erfolgreich gepostet:", response.data)
        sys.stdout.flush()
        save_current_chapter(chapter_number + 1)
    except tweepy.errors.TooManyRequests:
        print("Rate limit reached. Sleeping for 15 minutes.")
        sys.stdout.flush()
        for i in range(15):
            print(f"Sleeping... {15 - i} minutes remaining.")
            sys.stdout.flush()
            time.sleep(60)  # Sleep for 1 minute (total: 15 minutes)
        print("Waking up and retrying now.")
        sys.stdout.flush()
        post_tweet()
    except tweepy.errors.Forbidden as e:
        print("Error posting tweet:", e)
        sys.stdout.flush()
        print("Details:", e.response.text)
        sys.stdout.flush()
    except Exception as e:
        print("An unexpected error occurred:", e)
        sys.stdout.flush()

# Bot ausführen
if __name__ == "__main__":
    post_tweet()
