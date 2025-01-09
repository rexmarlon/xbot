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


# GPT-gestütztes Tweet-Generieren
def generate_tweet(whitepaper_content, discord_link="https://discord.gg/hVjpvDBWBu"):
    prompt = f"""
    Du bist ein kreativer Social-Media-Manager für Huntmon. Wähle ein spannendes Thema aus dem whitepaper über Huntmon.
    
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
        tweet = generate_tweet(generate_tweet)
        
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
