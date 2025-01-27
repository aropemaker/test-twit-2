import tweepy
from fastapi import FastAPI
import os
import time

app = FastAPI()

# Twitter API keys
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

# Cache bot details
bot_user_id = client.get_me().data.id
bot_username = client.get_me().data.username

# Track replied tweets
replied_tweets = set()

@app.get("/")
def home():
    return {"status": "Twitter bot is running!"}

def fetch_and_reply_mentions():
    try:
        # Fetch mentions
        mentions = client.get_users_mentions(bot_user_id, tweet_fields=["id", "text", "author_id"])
        if mentions and mentions.data:
            for mention in mentions.data:
                if mention.id not in replied_tweets:
                    reply_text = f"Hello @{mention.author_id}! Thanks for tagging me!"
                    try:
                        client.create_tweet(
                            text=reply_text,
                            in_reply_to_tweet_id=mention.id
                        )
                        print(f"Replied to tweet ID {mention.id}")
                        replied_tweets.add(mention.id)  # Mark tweet as replied
                    except Exception as e:
                        print(f"Error replying: {e}")
        else:
            print("No new mentions.")
    except tweepy.TooManyRequests:
        print("Rate limit hit. Sleeping for 15 minutes...")
        time.sleep(15 * 60)  # Wait for 15 minutes before retrying
    except Exception as e:
        print(f"Error fetching mentions: {e}")

def start_polling():
    while True:
        print("Checking for new mentions...")
        fetch_and_reply_mentions()
        print("Sleeping for 15 minutes...")
        time.sleep(15 * 60)  # Wait 15 minutes

if __name__ == "__main__":
    start_polling()
