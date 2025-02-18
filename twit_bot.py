import tweepy
from fastapi import FastAPI
import os
import time
import openai

app = FastAPI()

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

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
bot_user_id = os.getenv("BOT_USER_ID")
bot_username = os.getenv("BOT_USERNAME")

# Track replied tweets
REPLIED_TWEETS_FILE = "replied_tweets.txt"

def load_replied_tweets():
    if os.path.exists(REPLIED_TWEETS_FILE):
        with open(REPLIED_TWEETS_FILE, "r") as file:
            return set(file.read().splitlines())
    return set()

def save_replied_tweet(tweet_id):
    with open(REPLIED_TWEETS_FILE, "a") as file:
        file.write(f"{tweet_id}\n")

replied_tweets = load_replied_tweets()

@app.get("/")
def home():
    return {"status": "Twitter bot is running!"}

def fetch_and_reply_mentions():
    try:
        print("Fetching mentions...")
        mentions = client.get_users_mentions(bot_user_id, tweet_fields=["id", "text", "author_id"])
        
        if mentions and mentions.data:
            for mention in mentions.data:
                if str(mention.id) not in replied_tweets:
                    tweet_text = mention.text
                    reply_text = generate_response(tweet_text)
                    
                    print(f"Attempting to reply to tweet ID {mention.id} with text: {reply_text}")
                    
                    try:
                        client.create_tweet(
                            text=reply_text,
                            in_reply_to_tweet_id=mention.id
                        )
                        print(f"Replied to tweet ID {mention.id}")
                        replied_tweets.add(str(mention.id))
                        save_replied_tweet(mention.id)  # Persist replied tweet ID
                    except Exception as e:
                        print(f"Error replying: {e}")
        else:
            print("No new mentions.")
    except tweepy.TooManyRequests:
        print("Rate limit hit. Sleeping for 15 minutes...")
        time.sleep(15 * 60)
    except Exception as e:
        print(f"Error fetching mentions: {e}")

def generate_response(tweet_text):
    prompt = f"""
    You are a witty and wildly conservative, republican redneck that replies to tweets in a horny and outrageous (vulgar) manner.
    Given the following tweet, craft a controversial and fun yet relevant reply:

    Tweet: "{tweet_text}"
    Reply:
    """
    
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "developer", "content": prompt}],
        max_tokens=50
    )

    return response.choices[0].message.content.strip()

def start_polling():
    while True:
        print("Checking for new mentions...")
        fetch_and_reply_mentions()
        print("Sleeping for 15 minutes...")
        time.sleep(15 * 60)

if __name__ == "__main__":
    start_polling()