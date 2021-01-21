import os
import subprocess
import numpy as np
import pandas as pd
import requests
import gzip
import shutil
import json

from twarc import Twarc
from datetime import datetime, date, timedelta
from utils import get_project_root


root = get_project_root()
raw_data_path = os.path.join(root, 'data', 'raw', 'news')
json_data_path = os.path.join(root, 'data', 'processed', 'news')

def configure_twarc():
    """Passes api credentials into Twarc"""
    t = Twarc(
        os.getenv('CONSUMER_KEY'),
        os.getenv('CONSUMER_SECRET'),
        os.getenv('ACCESS_TOKEN'),
        os.getenv('ACCESS_TOKEN_SECRET')
    )
    return t

def test():
    t = configure_twarc()

    # for tweet in t.timeline(screen_name='nytimes'):
    #     print(tweet)
    # for tweet in t.retweets(['1352357900551860226']):
    #     print(tweet)
    # get_user_timeline('nytimes')
    timeline_to_retweets('nytimes')

def get_news_rts():
    """Downloads retweets for the networks specified in config file.
    
    Attempts downloading data if data file doesn't already exist.
        
    """
    news_path = os.path.join(root, 'config', 'news_stations.txt')
    with open(news_path) as f:
        for line in f:
            screen_name = str.strip(line)
            timeline_to_retweets(screen_name)
            
def timeline_to_retweets(screen_name):
    """Downloads retweets given the user screen name."""
    jsonl_path = get_user_timeline(screen_name)
    txt_path = os.path.splitext(jsonl_path)[0] + '.txt'
    jsonl_path_rts = os.path.join(json_data_path, f'{screen_name}_rts.jsonl')
    
    if not os.path.isfile(txt_path):
        twts = []
        for line in open(jsonl_path):
            twt = json.loads(line)
            twts.append(twt['id_str'])
        pre_rts = np.array(twts, dtype=np.int64)

        np.savetxt(txt_path, pre_rts, fmt='%i')
    
    download_retweets(txt_path, jsonl_path_rts)
        
def get_user_timeline(screen_name):
    """Retrieves user timeline data given retweet using twarc."""
    t = configure_twarc()
    jsonl_path = os.path.join(raw_data_path, f'{screen_name}_tweets.jsonl')
    if not os.path.isfile(jsonl_path):
 
        # e.g. twarc timeline realDonaldTrump > realDonaldTrump.jsonl
        with open(jsonl_path, 'w') as outfile:
            for tweet in t.timeline(screen_name=screen_name):
                outfile.write(json.dumps(tweet) + '\n')
    
    return jsonl_path
    
def download_retweets(txt_path, jsonl_path):
    """Retrieves retweets given ID using twarc."""
    t = configure_twarc()
    if not os.path.isfile(jsonl_path):

        with open(jsonl_path, 'w') as outfile:
            with open(txt_path, 'r') as infile:
                for tweet in infile.read().split('\n'):
                    print(tweet)
                    for retweet in t.retweets(list(tweet)):
                        outfile.write(json.dumps(retweet) + '\n')
