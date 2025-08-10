import tweepy
import requests
import time

# Twitter API v2 credentials
BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAKfrPwEAAAAAskVBvLjTms3AoTxcUUFLc1HfIWg%3D1yJuD5aReKZVVEbgikXpiAVvCMDDHAdbGw1vVJLvUZA4mqZIcG'
API_KEY = 'smffFE1TaRWzP7k8AHOl4DVBK'
API_SECRET = '10ewH6dewmI3TqXxNaQtKjccyvy1nmBg6NBGtvlcD4SqZJzk2q'
ACCESS_TOKEN = '459915333-cxwrUBMVuZ4vvTyhz7kzH1DXSrled9llicyTGbiY'
ACCESS_TOKEN_SECRET = 'jrsxoCh6gVUx93G8PEN1ig8MKipr22rHfgOqzZ04Un9SC'

# Initialize Tweepy Client with user auth
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
    wait_on_rate_limit=True
)

LAST_SEEN_FILE = 'last_seen_id.txt'

def retrieve_last_seen_id(file_name):
    try:
        with open(file_name, 'r') as f:
            return int(f.read().strip())
    except:
        return None

def store_last_seen_id(last_seen_id, file_name):
    with open(file_name, 'w') as f:
        f.write(str(last_seen_id))

def get_response_from_api(message):
    url = 'http://localhost:5000/api/chat'  # Change to your deployed API URL
    data = {'message': message}
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return response.json().get('reply', "Sorry, no reply.")
        else:
            return "Error: Bad response from API."
    except Exception as e:
        return f"Error connecting to API: {str(e)}"

def reply_to_mentions():
    print("Checking mentions with Twitter API v2...")
    last_seen_id = retrieve_last_seen_id(LAST_SEEN_FILE)
    
    # Get your bot user id
    me = client.get_me()
    bot_user_id = me.data.id
    bot_username = me.data.username

    # Fetch mentions since last seen id (max 10 for demo)
    mentions = client.get_users_mentions(id=bot_user_id, since_id=last_seen_id, max_results=10, tweet_fields=["author_id","created_at"])

    if mentions.data:
        for mention in reversed(mentions.data):
            print(f"Replying to tweet {mention.id} from user {mention.author_id}")
            last_seen_id = int(mention.id)
            store_last_seen_id(last_seen_id, LAST_SEEN_FILE)

            # Remove bot username from tweet text
            text = mention.text.replace(f"@{bot_username}", "").strip()

            # Get reply from backend API
            reply_text = get_response_from_api(text)

            # Reply to mention
            try:
                client.create_tweet(
                    text=f"@{mention.author_id} {reply_text}",
                    in_reply_to_tweet_id=mention.id
                )
                print(f"Replied to {mention.id}")
            except Exception as e:
                print(f"Error replying to tweet {mention.id}: {e}")

if __name__ == "__main__":
    while True:
        reply_to_mentions()
        time.sleep(60)