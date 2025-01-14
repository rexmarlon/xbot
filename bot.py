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
    Du bist ein kreativer Social-Media-Manager für Huntmon. Basierend auf folgendem Inhalt aus dem Whitepaper:
    {whitepaper_content}

    Schreibe einen längeren, interessanten Text, der auf mehrere Tweets aufgeteilt werden kann. Jeder Tweet sollte:
    - Informativ sein.
    - Leser neugierig machen.
    - Abwechslungsreiche Formulierungen verwenden.
    - Relevante Hashtags wie #Huntmon, #Matic, #ETH, #P2E, #ARGaming enthalten oder andere, die zum Inhalt des Textes gerade passen, aktuell hype sind, viele Nutzer anziehen oder in Nischen viel Aufmerksamkeit erhalten.

    Wichtig: Stelle sicher, dass jeder Abschnitt weniger als 280 Zeichen lang ist und als Teil eines Threads logisch fortgesetzt werden kann.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative social media assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7,
        )
        long_text = response["choices"][0]["message"]["content"].strip()
        print(f"Generierter langer Text: {long_text}")

        # Splitte den langen Text in Abschnitte von maximal 275 Zeichen
        tweets = textwrap.wrap(long_text, width=275, break_long_words=False, placeholder="...")

        # Poste die Tweets als Thread
        previous_tweet_id = None
        posted_tweets = set()
        for i, tweet in enumerate(tweets):
            if tweet in posted_tweets:
                print(f"Tweet {i+1} wurde übersprungen, da er doppelt ist: {tweet}")
                continue
            posted_tweets.add(tweet)

            for attempt in range(3):  # Bis zu 3 Versuche pro Tweet
                try:
                    # Wähle ein zufälliges Bild und lade es hoch
                    image_path = get_random_image()
                    media_id = upload_image(image_path) if image_path else None

                    if previous_tweet_id:
                        response = client.create_tweet(text=tweet, in_reply_to_tweet_id=previous_tweet_id, media_ids=[media_id] if media_id else None)
                    else:
                        response = client.create_tweet(text=tweet, media_ids=[media_id] if media_id else None)
                    print(f"Tweet {i+1} gepostet:", response.data)
                    previous_tweet_id = response.data.get("id")
                    break
                except tweepy.errors.Forbidden as e:
                    print(f"Fehler beim Posten von Tweet {i+1}: {e}")
                    if attempt < 2:
                        print("Versuche erneut...")
                        time.sleep(2)
                    else:
                        print("Abbruch nach 3 Versuchen.")
    except Exception as e:
        print("Fehler beim Generieren oder Posten des Threads:", e)

# Hauptfunktion: Tweet posten
def post_tweet():
    chapter_number = load_current_chapter()
    whitepaper_content = read_chapter_content(chapter_number)

    if not whitepaper_content:
        print(f"Kapitel {chapter_number} nicht gefunden. Zurücksetzen auf Kapitel 1.")
        chapter_number = 1
        save_current_chapter(chapter_number)
        whitepaper_content = read_chapter_content(chapter_number)

    if not whitepaper_content:
        print("Kein Inhalt verfügbar. Der Prozess wird abgebrochen.")
        return

    # Wähle zwischen Einzel-Tweet oder Thread
    is_long_tweet = True  # Setze auf False, um normale Tweets zu posten
    if is_long_tweet:
        post_thread(whitepaper_content)
    else:
        tweet = generate_tweet(whitepaper_content)
        try:
            # Wähle ein zufälliges Bild und lade es hoch
            image_path = get_random_image()
            media_id = upload_image(image_path) if image_path else None

            response = client.create_tweet(text=tweet, media_ids=[media_id] if media_id else None)
            print("Tweet erfolgreich gepostet:", response.data)
            save_current_chapter(chapter_number + 1)
        except tweepy.errors.Forbidden as e:
            print("Ein Fehler ist aufgetreten beim Posten des Tweets:", e)
            print("Fehlerdetails:", e.response.text)
        except Exception as e:
            print("Ein unerwarteter Fehler ist aufgetreten:", e)

# Bot ausführen
if __name__ == "__main__":
    post_tweet()
