import os
import subprocess
import numpy as np
import pandas as pd
import json

from datetime import timedelta, date
from utils import get_project_root


root = get_project_root()


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
    jsonl_path_rts = os.path.join(root, 'data/processed', f'{screen_name}_rts.jsonl')
    
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
    jsonl_path = os.path.join(root, 'data/raw', f'{screen_name}.jsonl')
    if not os.path.isfile(jsonl_path):
        # e.g. twarc timeline realDonaldTrump > realDonaldTrump.jsonl
        cmd = f'twarc timeline {screen_name} > {jsonl_path}'
        subprocess.run(cmd, shell=True)
    
    return jsonl_path
    
def download_retweets(txt_path, jsonl_path):
    """Retrieves retweets given ID using twarc."""
    if not os.path.isfile(jsonl_path):
        rt_cmd = f'twarc retweets {txt_path} > {jsonl_path}'
        subprocess.run(rt_cmd, shell=True)
        