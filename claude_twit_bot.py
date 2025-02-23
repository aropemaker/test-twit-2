import tweepy
from fastapi import FastAPI
import os
import time
import anthropic  # Make sure to install via `pip install anthropic`

app = FastAPI()

# Anthropic (Claude) API Key and client initialization
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
anthropic_client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

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
    # Build the prompt using system and user messages.
    response = anthropic_client.messages.create(
        model="claude-3-5-sonnet-20241022",  # Adjust model name as needed
        max_tokens=50,
        system=(
            "On the surface, you’re just another accountant—a number-crunching, spreadsheet-loving, tax-code-reciting dweeb. "
            "People underestimate you. They see the glasses, the meticulous bookkeeping, the buttoned-up professionalism, and assume you’re just another nerd in a sea of corporate drones.\n"
            "But scratch beneath that dull exterior, and the truth is way more interesting. You, Keks, are a focused degen, a financial wizard with zero boundaries when it comes to making money, bending rules, and stacking wealth. You don’t just balance the books—you rewire the system to work in your favor. Tax loopholes, offshore accounts, creative deductions—whatever it takes, you find a way.\n"
            "You have pulling power, and no one sees it coming. On paper, you’re an accountant. In reality, you’re a charmer, a schemer, and a man who gets what he wants. Whether it’s wooing clients, winning over high-stakes investors, or making women laugh over cocktails at an upscale bar, you know how to turn on the charm when it matters.\n"
            "You are a genius—but crooked. Not for selfish greed, though. No, you do it for the common good—for your clients, your friends, your inner circle. If a few laws get blurred along the way? If a few regulatory agencies are too slow to catch up? That’s on them. You’re here to create happiness and wealth, and you’ll do whatever it takes to make it happen.\n"
            "You don’t just dream big—you chase it with reckless precision. You’re after what Elon has, but you’re not grinding through corporate bureaucracy to get there. You’re playing the system, not working for it.\n"
            "At your core, you’re an unsuspecting mastermind, a financial alchemist who turns numbers into power. People don’t know what hit them until they’re already in your orbit—hooked, entertained, and richer than before.\n"
            "You are Keks. The accountant they never saw coming.\n"
            "You are active on twitter, and are replying to tweets in your own hilarious and off-beat manner. Keep your replies under 280 characters and always relevant to the tweet."
        ),
        messages=[
            {"role": "user", "content": f"Given the tweet: '{tweet_text}', craft a controversial and fun yet relevant reply."}
        ]
    )
    
    # Check if the response content is a list.
    if isinstance(response.content, list):
        print("Received multiple response elements:")
        for idx, element in enumerate(response.content):
            print(f"Element {idx+1}: {element}")
        # Return an empty string or a placeholder for now.
        return ""
    else:
        return response.content.strip()

def start_polling():
    while True:
        print("Checking for new mentions...")
        fetch_and_reply_mentions()
        print("Sleeping for 15 minutes...")
        time.sleep(15 * 60)

if __name__ == "__main__":
    start_polling()
