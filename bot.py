import tweepy
import openai
import os

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
    else:
        print(f"Kapitel {chapter_number} wurde nicht gefunden.")
        return None

# GPT-gestütztes Tweet-Generieren
def generate_tweet(whitepaper_content, discord_link="https://discord.gg/hVjpvDBWBu"):
    prompt = f"""
    Du bist ein kreativer Social-Media-Manager für Huntmon. Basierend auf folgendem Inhalt aus dem Whitepaper:
    {whitepaper_content}

    Schreibe einen kurzen, interessanten Tweet auf Englisch. Der Tweet sollte neugierig machen, Leser dazu einladen, dem Discord-Server beizutreten, und relevante Hashtags wie #Huntmon, #Blockchain, #Gaming enthalten.
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
        return f"{tweet}\n\n\ud83c\udf1f Join our Discord: {discord_link}"
    except Exception as e:
        print("Fehler bei der Generierung des Tweets mit GPT:", e)
        return "Explore the world of Huntmon! \ud83c\udf1f Join our Discord: https://discord.gg/hVjpvDBWBu"

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
        if "duplicate" in str(e).lower():
            print("Tweet wurde nicht gepostet, da er bereits existiert.")
        else:
            print("Ein Fehler ist aufgetreten beim Posten des Tweets:", e)
    except Exception as e:
        print("Ein unerwarteter Fehler ist aufgetreten:", e)

# Bot ausführen
if __name__ == "__main__":
    post_tweet()
