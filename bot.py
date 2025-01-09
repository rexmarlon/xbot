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

# Den Inhalt des Whitepapers laden
def load_whitepaper(file_path="Huntmon-Whitepaper.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print("Fehler: Whitepaper-Datei nicht gefunden.")
        return None
    except Exception as e:
        print(f"Fehler beim Laden der Whitepaper-Datei: {e}")
        return None

# GPT-gestütztes Tweet-Generieren
def generate_tweet(whitepaper_content, discord_link="https://discord.gg/hVjpvDBWBu"):
    prompt = f"""
    Du bist ein kreativer Social-Media-Manager für Huntmon. Wähle ein spannendes Thema aus dem folgenden Text über Huntmon:
    
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
        return f"{tweet}\n\n🌟 Join our Discord: {discord_link}"
    except Exception as e:
        print("Fehler bei der Generierung des Tweets mit GPT:", e)
        return "Explore the world of Huntmon! 🌟 Join our Discord: https://discord.gg/hVjpvDBWBu"

# Hauptfunktion: Tweet posten
def post_tweet():
    try:
        whitepaper_content = load_whitepaper()
        if not whitepaper_content:
            print("Kein Whitepaper-Inhalt verfügbar. Standard-Tweet wird verwendet.")
            tweet = "Explore the world of Huntmon! 🌟 Join our Discord: https://discord.gg/hVjpvDBWBu"
        else:
            tweet = generate_tweet(whitepaper_content)
        
        # Tweet posten
        response = client.create_tweet(text=tweet)
        print("Tweet erfolgreich gepostet:", response.data)
    except tweepy.errors.Forbidden as e:
        if "duplicate" in str(e).lower():
            print("Tweet wurde nicht gepostet, da er bereits existiert.")
        else:
            print("Ein Fehler ist aufgetreten beim Posten des Tweets:", e)
    except Exception as e:
        print("Ein Fehler ist aufgetreten beim Posten des Tweets:", e)

# Bot ausführen
if __name__ == "__main__":
    print(f"OpenAI-Bibliothek Version: {openai.__version__}")
    post_tweet()
