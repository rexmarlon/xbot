import tweepy
import openai
import os
import textwrap

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
import fcntl

def save_current_chapter(chapter_number):
    print(f"Speichere Kapitelnummer: {chapter_number} in {CHAPTER_FILE}")
    try:
        with open(CHAPTER_FILE, "w") as file:
            fcntl.flock(file, fcntl.LOCK_EX)  # Sperre die Datei exklusiv
            file.write(str(chapter_number))
            fcntl.flock(file, fcntl.LOCK_UN)  # Aufheben der Sperre
        # Überprüfen, ob der Inhalt korrekt geschrieben wurde
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

# GPT-gestütztes Tweet-Generieren
def generate_tweet(whitepaper_content):
    prompt = f"""
Du bist ein kreativer Social-Media-Manager für Huntmon. Basierend auf folgendem Inhalt aus dem Whitepaper:
{whitepaper_content}

Schreibe einen kurzen, interessanten Tweet auf Englisch. Der Tweet sollte:
- Informativ sein.
- Leser neugierig machen.
- Abwechslungsreiche Formulierungen verwenden.
- Relevante Hashtags wie #Huntmon, #BlockchainGaming, #NFTGaming, #CryptoGaming, #PlayToEarn, #ARGaming enthalten oder andere die zum Inhalt des Textes gerade passen und hype sind und leute anzieht und interessante Nischen.

Verwende frische und originelle Ansätze, um das Interesse der Zielgruppe zu wecken. Beginne den Tweet mit einer fesselnden Frage, einem starken Call-to-Action oder einer ungewöhnlichen Aussage. Wichtig: Achte darauf den Tweet weniger als 280 Zeichen lang ist und in ein Tweet passt von der länge.
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
        # Entferne umgebende Anführungszeichen, falls vorhanden
        if tweet.startswith('"') and tweet.endswith('"'):
            tweet = tweet[1:-1]
        print(f"Generierter Tweet (vor Kürzung): {tweet} (Länge: {len(tweet)})")
        # Kürze den Tweet auf maximal 280 Zeichen
        tweet = textwrap.shorten(tweet, width=280, placeholder="...")
        print(f"Tweet nach Kürzung: {tweet} (Länge: {len(tweet)})")
        return tweet
    except Exception as e:
        print("Fehler bei der Generierung des Tweets mit GPT:", e)
        return "Explore the world of Huntmon! 🌟 Dive into #Huntmon #BlockchainGaming #NFTGaming #PlayToEarn."

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

    tweet = generate_tweet(whitepaper_content)
    try:
        response = client.create_tweet(text=tweet)
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
