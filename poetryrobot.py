import twitter
import json
import random

with open('credentials.json') as f:
    credentials = json.loads(f.read())

api = twitter.Api(**credentials)

def has_less_than_three_hashtags(status):
    return status.text.count('#') <= 2

def poem_tweets():
    # - have a poetry or poem hashtag
    # - 'safe' only
    # - no links
    # - no retweets
    query = 'q=%23poetry+OR+%23poem+filter%3Asafe+-filter%3Alinks+-filter%3Aretweets'
    # - English only
    query += '&lang=en'
    # - 40 results
    query += '&count=40'
    results = api.GetSearch(raw_query=query)
    results = list(filter(has_less_than_three_hashtags, results))
    return results

def retweet_someone(tweets):
    if not tweets:
        return False
    status_to_retweet = max(tweets, key=lambda status: status.favorite_count + status.retweet_count)
    api.PostRetweet(status_to_retweet.id)

def follow_followers():
    (_, _, recent_followers) = api.GetFollowersPaged()
    followers_not_followed_yet = list(filter(lambda f: not f.following, recent_followers))
    max_num_to_follow = 5
    for follower in followers_not_followed_yet[0:max_num_to_follow]:
        api.CreateFriendship(follower.id)

def follow_someone(tweets):
    if not tweets:
        return False
    users = list(map(lambda t: t.user, tweets))
    users_not_followed_yet = list(filter(lambda u: not u.following, users))
    if not users_not_followed_yet:
        return False
    user_to_follow = random.choice(users_not_followed_yet)
    api.CreateFriendship(user_to_follow.id)

def reply_to_someone(tweets):
    if not tweets:
        return False
    tweet_to_reply_to = random.choice(tweets)
    possible_responses = [
        'Thank you for tweeting poetry!',
        'Thanks for sharing poetry with the world 🌎',
        "You've poetry'd your way to my metal heart",
        'Keep tweeting poetry!'
    ]
    response = random.choice(possible_responses)
    api.PostUpdate(response, in_reply_to_status_id=tweet_to_reply_to.id, auto_populate_reply_metadata=True)

def lambda_handler(_event_json, _context):
    tweets = poem_tweets()
    # Retweet a poet more often than reply to a poet:
    if random.random() <= 0.9:
        retweet_someone(tweets)
    else:
        reply_to_someone(tweets)
    follow_someone(tweets)
    follow_followers()
