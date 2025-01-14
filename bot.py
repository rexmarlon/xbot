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

# GPT-gestütztes Thread-Generieren und Posten
def post_thread(whitepaper_content):
    # Generiere den langen Text basierend auf dem Whitepaper
    prompt = f"""
    You are a creative social media manager for Huntmon. Based on the following content from the whitepaper:
    {whitepaper_content}

    Write a longer, engaging text that can be split into multiple tweets. Each tweet should:
    - Be informative.
    - Spark curiosity among readers.
    - Use varied and engaging language.
    - Include relevant hashtags like #Huntmon, #Matic, #ETH, #P2E, #ARGaming, or others that are currently viral, attract attention, or are niche-specific.

    Ensure tweets flow logically, allowing sentences to continue in the next tweet if necessary, and keep each segment under 280 characters.
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

        # Split the text into segments of <=275 characters, allowing sentence continuation
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

        # Wähle ein Bild für den ersten Tweet aus
        image_url = get_random_image_url()

        # Poste die Tweets als Thread
        previous_tweet_id = None
        for i, tweet in enumerate(tweets):
            for attempt in range(3):  # Retry logic
                try:
                    if i == 0:  # Post image link only with the first tweet
                        tweet_with_image = f"{tweet}\n\n{image_url}" if image_url else tweet
                        response = client.create_tweet(text=f"{tweet_with_image} ({i+1}/{len(tweets)})")
                    else:
                        response = client.create_tweet(text=f"{tweet} ({i+1}/{len(tweets)})", in_reply_to_tweet_id=previous_tweet_id)

                    print(f"Tweet {i+1} posted:", response.data)
                    previous_tweet_id = response.data.get("id")
                    time.sleep(5)  # Add a delay between tweets to avoid rate limits
                    break
                except tweepy.errors.TooManyRequests:
                    print("Rate limit reached.")
                    time.sleep(900)  # Sleep for 15 minutes
                except Exception as e:
                    print(f"Error posting tweet {i+1}: {e}")
                    if attempt < 2:
                        print("Retrying...")
                        time.sleep(2)
                    else:
                        print("Aborting after 3 attempts.")
    except Exception as e:
        print("Error generating or posting the thread:", e)

# Hauptfunktion: Tweet posten
def post_tweet():
    chapter_number = load_current_chapter()
    whitepaper_content = read_chapter_content(chapter_number)

    if not whitepaper_content:
        print(f"Chapter {chapter_number} not found. Resetting to chapter 1.")
        chapter_number = 1
        save_current_chapter(chapter_number)
        whitepaper_content = read_chapter_content(chapter_number)

    if not whitepaper_content:
        print("No content available. Aborting process.")
        return

    # Choose between single tweet or thread
    is_long_tweet = True  # Set to False for single tweets
    if is_long_tweet:
        post_thread(whitepaper_content)
    else:
        tweet = generate_tweet(whitepaper_content)
        try:
            # Select a random image URL
            image_url = get_random_image_url()
            tweet_with_image = f"{tweet}\n\n{image_url}" if image_url else tweet

            response = client.create_tweet(text=tweet_with_image)
            print("Tweet successfully posted:", response.data)
            save_current_chapter(chapter_number + 1)
        except tweepy.errors.TooManyRequests:
            print("Rate limit reached.")
            time.sleep(900)  # Sleep for 15 minutes
        except tweepy.errors.Forbidden as e:
            print("Error posting tweet:", e)
            print("Details:", e.response.text)
        except Exception as e:
            print("An unexpected error occurred:", e)

# Bot ausführen
if __name__ == "__main__":
    post_tweet()
