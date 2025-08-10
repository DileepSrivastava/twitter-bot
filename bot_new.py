import tweepy
import time

from config import (
    TWITTER_API_KEY, TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
)

# Authenticate
auth = tweepy.OAuth1UserHandler(
    TWITTER_API_KEY, TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
)
api = tweepy.API(auth, wait_on_rate_limit=True)

# Define hashtags to track
TRACK_HASHTAGS = ["#Motivation", "#Inspiration", "#Quotes"]

def like_and_retweet():
    for hashtag in TRACK_HASHTAGS:
        print(f"Searching for tweets with {hashtag}")
        try:
            for tweet in tweepy.Cursor(api.search_tweets, q=hashtag, lang="en", result_type="recent").items(10):
                tweet_id = tweet.id
                username = tweet.user.screen_name
                print(f"Processing tweet {tweet_id} by @{username}")

                # Like tweet
                try:
                    api.create_favorite(tweet_id)
                    print(f"Liked tweet {tweet_id}")
                except tweepy.TweepError as e:
                    print(f"Error liking tweet: {e}")

                # Retweet
                try:
                    api.retweet(tweet_id)
                    print(f"Retweeted tweet {tweet_id}")
                except tweepy.TweepError as e:
                    print(f"Error retweeting: {e}")

            time.sleep(60)  # Wait a minute before next hashtag to avoid rate limits

        except Exception as e:
            print(f"Error searching tweets: {e}")

if __name__ == "__main__":
    like_and_retweet()
