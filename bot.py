import tweepy
import openai
import os
import textwrap
import time
import random
import requests
import sys
from telegram import Bot

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

# Telegram-Bot-Token und Chat-ID laden
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
telegram_bot = Bot(token=TELEGRAM_TOKEN)

# Pfad zur Datei, in der das aktuelle Kapitel gespeichert wird
CHAPTER_FILE = "current_chapter.txt"
CHAPTER_DIRECTORY = "."
IMAGES_DIRECTORY = "images"
GITHUB_BASE_URL = "https://raw.githubusercontent.com/rexmarlon/xbot/main/images/"

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
    try:
        images = [f for f in os.listdir(IMAGES_DIRECTORY) if f.endswith((".png", ".jpg", ".jpeg"))]
        if not images:
            print("Keine Bilder im Verzeichnis gefunden.")
            sys.stdout.flush()
            return None
        random_image = random.choice(images)
        image_url = GITHUB_BASE_URL + random_image
        print(f"Zufällig ausgewähltes Bild: {image_url}")
        sys.stdout.flush()
        return image_url
    except Exception as e:
        print(f"Fehler beim Abrufen des Bildes: {e}")
        sys.stdout.flush()
        return None

# Bild von GitHub herunterladen und als Datei speichern
def download_image(image_url):
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            image_path = os.path.join("temp_image", os.path.basename(image_url))
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            with open(image_path, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(f"Bild heruntergeladen: {image_path}")
            sys.stdout.flush()
            return image_path
        else:
            print(f"Fehler beim Herunterladen des Bildes. Statuscode: {response.status_code}")
            sys.stdout.flush()
            return None
    except Exception as e:
        print(f"Fehler beim Herunterladen des Bildes: {e}")
        sys.stdout.flush()
        return None

# GPT-gestütztes Thread-Generieren und Senden an Telegram
def send_thread_to_telegram(whitepaper_content):
    print("Starte Generierung des Threads...")
    sys.stdout.flush()
    prompt = f"""
    You are a creative social media manager for Huntmon. Based on the following content from the whitepaper:
    {whitepaper_content}

    Write a longer, engaging text that can be split into multiple tweets. 
    - Include relevant hashtags at the end like #Huntmon, #Matic, #ETH, #P2E, #ARGaming, or others that are viral or niche-specific.
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
        sys.stdout.flush()

        # Split the text into segments of <=275 characters, ensuring continuation
        tweets = textwrap.wrap(long_text, width=275, break_long_words=False)

        # Sende die Tweets als Nachrichten an Telegram
        image_url = get_random_image_url()  # GitHub-Bild-URL abrufen
        if image_url:
            image_path = download_image(image_url)
            if image_path:
                with open(image_path, "rb") as img_file:
                    telegram_bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=img_file)
                os.remove(image_path)

        for i, tweet in enumerate(tweets):
            try:
                telegram_bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"{tweet} ({i+1}/{len(tweets)})")
                print(f"Nachricht {i+1} an Telegram gesendet.")
                sys.stdout.flush()
                time.sleep(2)  # Verzögerung zwischen den Nachrichten
            except Exception as e:
                print(f"Fehler beim Senden der Nachricht {i+1}: {e}")
                sys.stdout.flush()
    except Exception as e:
        print("Error generating or sending the thread to Telegram:", e)
        sys.stdout.flush()

# Hauptfunktion: Nachricht senden
def post_to_telegram():
    print("Start: Senden an Telegram-Prozess")
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

    send_thread_to_telegram(whitepaper_content)

    # Aktualisiere das Kapitel
    save_current_chapter(chapter_number + 1)
    print(f"Kapitel aktualisiert auf: {chapter_number + 1}")
    sys.stdout.flush()


# Bot ausführen
if __name__ == "__main__":
    post_to_telegram()
