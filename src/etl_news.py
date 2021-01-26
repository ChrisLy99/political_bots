import os
import numpy as np
import json

from twarc import Twarc
from utils import get_project_root


root = get_project_root()
raw_data_path = os.path.join(root, 'data', 'raw', 'news')
proc_data_path = os.path.join(root, 'data', 'processed', 'news')

def configure_twarc():
    """Passes api credentials into Twarc."""
    t = Twarc(
        os.getenv('CONSUMER_KEY'),
        os.getenv('CONSUMER_SECRET'),
        os.getenv('ACCESS_TOKEN'),
        os.getenv('ACCESS_TOKEN_SECRET')
    )
    return t

def test():
    t = configure_twarc()

    get_users(screen_name='FoxNews')

def get_news_rts():
    """Downloads retweets for the networks specified in config file.

    Attempts downloading data if data file doesn't already exist.

    """
    news_path = os.path.join(root, 'config', 'news_stations.txt')
    with open(news_path) as fh:
        for line in fh:
            screen_name = str.strip(line)
            timeline_to_retweets(screen_name=screen_name)
            
def get_timeline_retweeters():
    """Downloads timelines of users retweeting the networks specified
    in config file.

    Attempts downloading data if data file doesn't already exist.

    """
    news_path = os.path.join(root, 'config', 'news_stations.txt')
    with open(news_path) as fh:
        for line in fh:
            screen_name = str.strip(line)
            get_users(screen_name)

def timeline_to_retweets(screen_name):
    """Downloads retweets given the user screen name."""
    jsonl_path = get_user_timeline(screen_name)
    txt_path = os.path.splitext(jsonl_path)[0] + '.txt'
    jsonl_path_rts = os.path.join(proc_data_path, f'{screen_name}_rts.jsonl')

    if not os.path.isfile(txt_path):
        twts = []
        with open(jsonl_path) as fh:
            for line in fh:
                twt = json.loads(line)
                twts.append(twt['id_str'])
        pre_rts = np.array(twts, dtype=np.int64)
        np.savetxt(txt_path, pre_rts, fmt='%i')

    download_retweets(txt_path, jsonl_path_rts)
    
def get_users(screen_name):
    """Retrieve user ids given retweets of a user."""
    path_rts = os.path.join(proc_data_path, f'{screen_name}_rts.jsonl')
    user_data_path = os.path.join(raw_data_path, f'{screen_name}_users')
    path_users = os.path.join(user_data_path, f'{screen_name}_users.txt')
    os.makedirs(user_data_path, exist_ok=True)
    
    if not os.path.isfile(path_users):
        users = set()
        with open(path_rts) as fh:
            for line in fh:
                rt = json.loads(line)
                users.add(rt['user']['id_str'])
        ids = np.sort(np.array(list(users), dtype=np.int64))
        np.savetxt(path_users, ids, fmt='%i')
        
    compile_users(screen_name)
    
def compile_users(screen_name):
    user_data_path = os.path.join(raw_data_path, f'{screen_name}_users')
    path_users = os.path.join(user_data_path, f'{screen_name}_users.txt')
    
    with open(path_users) as fh:
        for line in fh:
            user_id = str.strip(line)
            txt_path = os.path.join(user_data_path, f'{user_id}.txt')
            if not os.path.isfile(txt_path):
                get_user_timeline(user_id=user_id, fp=user_data_path)
            

def get_user_timeline(user_id=None, screen_name=None, fp=raw_data_path):
    """Retrieves user timeline data given retweet using twarc.
    
    Requires either user_id or screen_name, not both.
    
    Parameters:
        user_id: A user's unique id
        screen_name: A user's Twitter handle
        fp: file path for the timeline file
        
    """
    t = configure_twarc()
    fn = screen_name if screen_name else user_id
    jsonl_path = os.path.join(fp, f'{fn}_tweets.jsonl')
    
    if not os.path.isfile(jsonl_path):
        with open(jsonl_path, 'w') as outfile:
            for tweet in t.timeline(user_id=user_id, screen_name=screen_name):
                outfile.write(json.dumps(tweet) + '\n')

    return jsonl_path

def download_retweets(txt_path, jsonl_path):
    """Retrieves retweets given ID using twarc."""
    t = configure_twarc()
    
    if not os.path.isfile(jsonl_path):
        with open(jsonl_path, 'w') as outfile, open(txt_path, 'r') as infile:
            for tweet in infile.read().split('\n'):
                for retweet in t.retweets(list(tweet)):
                    outfile.write(json.dumps(retweet) + '\n')
