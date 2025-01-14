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

        # Poste die Tweets als Thread
        previous_tweet_id = None
        for i, tweet in enumerate(tweets):
            for attempt in range(3):  # Retry logic
                try:
                    if i == 0:  # Post URL of the image with the first tweet
                        image_url = "https://your-public-image-link.com/example.jpg"  # Replace with your actual URL
                        response = client.create_tweet(text=f"{tweet} {image_url} ({i+1}/{len(tweets)})")
                    else:
                        response = client.create_tweet(text=f"{tweet} ({i+1}/{len(tweets)})", in_reply_to_tweet_id=previous_tweet_id)

                    print(f"Tweet {i+1} posted:", response.data)
                    previous_tweet_id = response.data.get("id")
                    break
                except tweepy.errors.Forbidden as e:
                    print(f"Error posting tweet {i+1}: {e}")
                    if attempt < 2:
                        print("Retrying...")
                        time.sleep(2)
                    else:
                        print("Aborting after 3 attempts.")
    except Exception as e:
        print("Error generating or posting the thread:", e)
