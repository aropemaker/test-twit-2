import tweepy
from fastapi import FastAPI
import os
import time

app = FastAPI()

# Twitter API keys (set these as environment variables on Railway or replace with your own keys for testing)
API_KEY = os.getenv("API_KEY") 
API_SECRET = os.getenv("API_SECRET") 
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN") 
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.getenv("BEARER_TOKEN") 

# Tweepy Authentication
client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
    bearer_token=BEARER_TOKEN
)

# FastAPI root endpoint
@app.get("/")
def home():
    return {"status": "Twitter bot is running!"}

def fetch_and_reply_mentions():
    """
    Fetch mentions of the bot and reply to them. This function is run periodically.
    """
    try:
        bot_username = client.get_me().data.username
        bot_user_id = client.get_me().data.id

        # Fetch mentions of the bot
        mentions = client.get_users_mentions(bot_user_id, tweet_fields=["id", "text", "author_id"])

        if mentions.data:
            for mention in mentions.data:
                if f"@{bot_username}" in mention.text:
                    reply_text = f"Hello @{mention.author_id}! Thanks for tagging me!"
                    try:
                        client.create_tweet(
                            text=reply_text,
                            in_reply_to_tweet_id=mention.id
                        )
                        print(f"Replied to tweet ID {mention.id} by user ID {mention.author_id}")
                    except Exception as e:
                        print(f"Error replying: {e}")
        else:
            print("No new mentions to reply to.")
    except Exception as e:
        print(f"Error fetching mentions: {e}")

# Periodically check for mentions and reply
def start_polling():
    while True:
        print("Checking for new mentions...")
        fetch_and_reply_mentions()
        print("Sleeping for 15 minutes...")
        time.sleep(15 * 60)  # 15 minutes

# Start the polling process when the script is run
if __name__ == "__main__":
    start_polling()
