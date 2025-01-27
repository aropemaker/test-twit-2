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
auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

@app.get("/")
def home():
    return {"status": "Twitter bot is running!"}

class MyStreamListener(tweepy.StreamingClient):
    def on_status(self, status):
        # Avoid replying to your own tweets
        if status.user.screen_name == api.me().screen_name:
            return
        
        # Check if the tweet mentions the bot
        if api.me().screen_name in status.text:
            reply_text = f"Hello @{status.user.screen_name}! Thanks for tagging me!"
            try:
                api.update_status(
                    status=reply_text, 
                    in_reply_to_status_id=status.id
                )
                print(f"Replied to @{status.user.screen_name}")
            except Exception as e:
                print(f"Error replying: {e}")

    def on_error(self, status_code):
        if status_code == 420:
            # Disconnect on rate limiting
            return False

# Function to start the Twitter stream
def start_stream():
    listener = MyStreamListener(BEARER_TOKEN)
    stream = tweepy.Stream(auth=api.auth, listener=listener)
    stream.filter(track=[f"@{api.me().screen_name}"], is_async=True)

# Start the stream when the bot starts
start_stream()