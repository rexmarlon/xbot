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

# Zufälligen Bild-Link aus dem GitHub-Repository auswählen
def get_random_image_url():
    base_url = "https://raw.githubusercontent.com/rexmarlon/xbot/main/images/"
    try:
        images = [f for f in os.listdir(IMAGES_DIRECTORY) if f.endswith(('.png', '.jpg', '.jpeg'))]
        if not images:
            print("Keine Bilder im Verzeichnis gefunden.")
            return None
        random_image = random.choice(images)
        print(f"Zufällig ausgewähltes Bild: {random_image}")
        return base_url + random_image
    except Exception as e:
        print(f"Fehler beim Auswählen eines Bildes: {e}")
        return None

# Rate-Limit-Status überprüfen
def check_rate_limit():
    try:
        print("Überprüfe Rate-Limit-Status...")
        # Fallback-Logik: Falls get_rate_limit_status nicht unterstützt wird
        # Alternativ können hier statische Wartezeiten eingebaut werden
        print("Rate-Limit-Überprüfung nicht implementiert; Standard fort.")
        print('Rate einstellungen bleiben als fallback festgelegt")
