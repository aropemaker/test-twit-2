import tweepy
from fastapi import FastAPI
import os

app = FastAPI()

# Twitter API keys (set these as environment variables on Railway)
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

# Custom stream listener
class MyStreamListener(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        # Avoid replying to your own tweets
        if tweet.author_id == client.get_me().data.id:
            return
        
        # Check if the tweet mentions the bot
        bot_username = client.get_me().data.username
        if f"@{bot_username}" in tweet.text:
            reply_text = f"Hello @{tweet.author_id}! Thanks for tagging me!"
            try:
                client.create_tweet(
                    text=reply_text,
                    in_reply_to_tweet_id=tweet.id
                )
                print(f"Replied to @{tweet.author_id}")
            except Exception as e:
                print(f"Error replying: {e}")

    def on_errors(self, errors):
        print(f"Stream error: {errors}")
        return False

# Function to start the Twitter stream
def start_stream():
    listener = MyStreamListener(BEARER_TOKEN)
    
    # Add a rule to listen for mentions of your bot
    bot_username = client.get_me().data.username
    listener.add_rules(tweepy.StreamRule(f"@{bot_username}"))
    
    # Start streaming
    listener.filter()

# Start the stream when the bot starts
start_stream()