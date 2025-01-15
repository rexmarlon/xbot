import tweepy
import openai
import os
import textwrap
import time
import random
import requests
import sys
from telegram import Bot
from telegram.constants import ParseMode
from telegram.ext import Application

# OpenAI API-Key laden
openai.api_key = os.getenv("OPENAI_API_KEY")

# Telegram-Bot-Token und Chat-ID laden
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
telegram_bot = Application.builder().token(TELEGRAM_TOKEN).build()

# GPT-gestütztes Thread-Generieren und Senden an Telegram
async def send_thread_to_telegram(whitepaper_content):
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

        # Sende die Nachrichten an Telegram
        image_url = "📷 " + get_random_image_url() if get_random_image_url() else ""
        if image_url:
            await telegram_bot.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=image_url)

        for i, tweet in enumerate(tweets):
            try:
                await telegram_bot.bot.send_message(
                    chat_id=TELEGRAM_CHAT_ID,
                    text=f"{tweet} ({i+1}/{len(tweets)})",
                    parse_mode=ParseMode.HTML
                )
                print(f"Nachricht {i+1} an Telegram gesendet.")
                sys.stdout.flush()
                await asyncio.sleep(2)  # Verzögerung zwischen den Nachrichten
            except Exception as e:
                print(f"Fehler beim Senden der Nachricht {i+1}: {e}")
                sys.stdout.flush()
    except Exception as e:
        print("Error generating or sending the thread to Telegram:", e)
        sys.stdout.flush()

# Hauptfunktion: Nachricht senden
async def post_to_telegram():
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

    await send_thread_to_telegram(whitepaper_content)

# Bot ausführen
if __name__ == "__main__":
    import asyncio
    asyncio.run(post_to_telegram())
