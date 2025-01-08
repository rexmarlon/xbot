import tweepy
import openai
import os
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

# Themen aus Inhaltsverzeichnis laden
def extract_topics(file_path="Huntmon-Whitepaper.txt"):
    topics = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().lower().startswith("chapter") or line.strip().lower().startswith("faq"):
                topics.append(line.strip())
    return topics

# Zufälliges Thema auswählen
def choose_random_topic(topics):
    return random.choice(topics)

# Tweet generieren
def generate_tweet(topic, discord_link="https://discord.gg/hVjpvDBWBu"):
    prompt = f"""
    Schreibe einen kurzen, interessanten Tweet basierend auf folgendem Thema:
    {topic}

    Füge relevante Hashtags wie #Huntmon, #Blockchain, #Gaming hinzu und lade die Leser ein, mehr auf dem Discord-Server zu erfahren.
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100,
        temperature=0.7,
    )
    tweet = response.choices[0].text.strip()
    return f"{tweet}\n\n🌟 Erfahre mehr auf unserem Discord: {discord_link}"

# Hauptfunktion: Tweet posten
def post_tweet():
    try:
        topics = extract_topics()
        random_topic = choose_random_topic(topics)
        tweet = generate_tweet(random_topic)
        
        # Tweet posten
        response = client.create_tweet(text=tweet)
        print("Tweet erfolgreich gepostet:", response)
    except Exception as e:
        print("Ein Fehler ist aufgetreten:", e)

# Bot ausführen
if __name__ == "__main__":
    post_tweet()
