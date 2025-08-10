import tweepy
import time
import datetime
import os
from textblob import TextBlob

# Replace these with your actual credentials
from config import (
    TWITTER_API_KEY, TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET, TWITTER_BEARER_TOKEN
)

# Tweepy client with all credentials for v2 endpoints with write access
client = tweepy.Client(
    bearer_token=TWITTER_BEARER_TOKEN,
    consumer_key=TWITTER_API_KEY,
    consumer_secret=TWITTER_API_SECRET,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_SECRET,
)

# Limits based on Free tier (adjust if needed)
MAX_LIKES_PER_DAY = 300
MAX_REPLIES_PER_DAY = 300

LIKES_LOG_FILE = "likes_log.txt"
REPLIES_LOG_FILE = "replies_log.txt"
PROCESSED_TWEETS_FILE = "processed_tweets.txt"

def read_daily_count(log_file):
    today_str = datetime.date.today().isoformat()
    if not os.path.exists(log_file):
        return 0
    with open(log_file, "r") as f:
        lines = f.readlines()
    return sum(1 for line in lines if line.strip() == today_str)

def log_action(log_file):
    today_str = datetime.date.today().isoformat()
    with open(log_file, "a") as f:
        f.write(today_str + "\n")

def load_processed_ids(filename=PROCESSED_TWEETS_FILE):
    try:
        with open(filename, "r") as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()

def save_processed_id(tweet_id, filename=PROCESSED_TWEETS_FILE):
    with open(filename, "a") as f:
        f.write(str(tweet_id) + "\n")

def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return "positive"
    elif polarity < -0.1:
        return "negative"
    else:
        return "neutral"

def search_tweets_and_engage(query, max_results=10):
    processed_ids = load_processed_ids()
    likes_today = read_daily_count(LIKES_LOG_FILE)
    replies_today = read_daily_count(REPLIES_LOG_FILE)

    while True:
        try:
            tweets = client.search_recent_tweets(query=query, max_results=max_results)
            break
        except tweepy.TooManyRequests:
            print("Rate limit hit. Sleeping for 60 seconds...")
            time.sleep(60)

    if tweets.data:
        for tweet in tweets.data:
            tweet_id = tweet.id
            if str(tweet_id) not in processed_ids:
                print(f"Tweet ID: {tweet_id}")
                print(f"Text: {tweet.text}")

                # Auto-like
                if likes_today < MAX_LIKES_PER_DAY:
                    try:
                        client.like(tweet_id)
                        print(f"❤️ Liked tweet {tweet_id}")
                        log_action(LIKES_LOG_FILE)
                        likes_today += 1
                    except Exception as e:
                        print(f"Error liking tweet {tweet_id}: {e}")
                else:
                    print("Like limit reached for today.")

                # Sentiment analysis before reply
                sentiment = analyze_sentiment(tweet.text)
                print(f"Sentiment: {sentiment}")

                if sentiment != "negative":
                    if replies_today < MAX_REPLIES_PER_DAY:
                        reply_text = "Thanks for the inspiration! 🙌 #SparkNest"
                        try:
                            client.create_tweet(text=reply_text, in_reply_to_tweet_id=tweet_id)
                            print(f"💬 Replied to tweet {tweet_id}")
                            log_action(REPLIES_LOG_FILE)
                            replies_today += 1
                        except Exception as e:
                            print(f"Error replying to tweet {tweet_id}: {e}")
                    else:
                        print("Reply limit reached for today.")
                else:
                    print("Skipping reply due to negative sentiment.")

                print("-" * 40)
                save_processed_id(tweet_id)
    else:
        print("No tweets found.")

if __name__ == "__main__":
    users = ["BJP4India", "narendramodi"]
    hashtags = ["#Motivation", "#Inspiration", "#Quotes"]

    users_part = " OR ".join([f"from:{u}" for u in users])
    hashtags_part = " OR ".join(hashtags)
    query = f"({users_part}) ({hashtags_part}) -is:retweet lang:en"

    print(f"Searching tweets for query: {query}")
    search_tweets_and_engage(query)
