import os
import subprocess
import numpy as np
import pandas as pd

from datetime import timedelta, date
from utils import get_project_root


root = get_project_root()


def get_troll_data():
    """Downloads tweets for the days between start and end dates as a
    single file.
    
    Dates range from start_date inclusive to end_date exclusive. Attempts
    downloading data if data file doesn't already exist.
       
    Args:
        start_date (str): start of data range. Format YYYY-MM-DD.
        end_date (str): end of data range. Format YYYY-MM-DD.
        clean (bool): specifies whether to download the cleaned data
          (without retweets) or the raw data.
        p (int): rate of tweets to hydrate.
        
    Returns:
        Path to data file.
        
    """
    # e.g. -> projectdir/data/raw/IRAhandle_tweets_5.csv
    base_fn = 'IRAhandle_tweets_'
    base = os.path.join(root, 'data/raw', base_fn)
    
    tot = []
    save = False
    for i in range(1, 14):
        csv_path = f'{base}{i}.csv'
    
        if not os.path.isfile(csv_path):  # full data doesn't exist
            save = True
            # e.g. -> IRAhandle_tweets_5.csv
            ext = f'{base_fn}{i}.csv'

            url_base = f'https://raw.githubusercontent.com/fivethirtyeight/russian-troll-tweets/master'
            url = os.path.join(url_base, ext)

            curl_cmd = f'curl {url} --output {csv_path}'
            subprocess.run(curl_cmd, shell=True)
            
            tmp = pd.read_csv(csv_path, usecols=['tweet_id']).values
            tot = tot + list(tmp)
    
    if save:
        tot = np.array(tot)
        txt_path = os.path.join(root, 'data/raw', 'troll_ids.txt')
        jsonl_path = os.path.join(root, 'data/processed', 'troll_rts.jsonl')
        np.savetxt(txt_path, tot, fmt='%i')
#         download_retweets(txt_path, jsonl_path)
    
def download_retweets(txt_path, jsonl_path):
    """Retrieves retweets given ID using twarc."""
    if not os.path.isfile(jsonl_path):
        rt_cmd = f'twarc retweets {txt_path} > {jsonl_path}'
        subprocess.run(rt_cmd, shell=True)
