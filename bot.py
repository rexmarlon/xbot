import openai

openai.api_key = "DEIN_API_KEY"

def generate_tweet(whitepaper_content, discord_link="https://discord.gg/hVjpvDBWBu"):
    prompt = f"""
    Du bist ein kreativer Social-Media-Manager für Huntmon...
    Hier der Whitepaper-Inhalt:
    {whitepaper_content}
    ...
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
