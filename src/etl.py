import os
import subprocess
import numpy as np

from datetime import timedelta, date
from utils import get_project_root


root = get_project_root()


def get_troll_data():
    # e.g. -> projectdir/data/raw/2020-03-27_ids.txt
    base_fn = 'IRAhandle_tweets_'
    base = os.path.join(root, 'data/raw/troll', base_fn)
    for i in range(1, 14):
        csv_path = f'{base}{i}.csv'
    
        if not os.path.isfile(csv_path):  # full data doesn't exist
            # e.g. -> 2020-03-27-dataset.tsv.gz
            ext = f'{base_fn}{i}.csv'

            url_base = f'https://raw.githubusercontent.com/fivethirtyeight/russian-troll-tweets/master'
            url = os.path.join(url_base, ext)

            # e.g. -> projectdir/data/raw/2020-03-27-dataset.tsv.gz
            gz_path = os.path.join(root, 'data/raw', ext)

            curl_cmd = f'curl {url} --output {gz_path}'
            subprocess.run(curl_cmd, shell=True)

#             try:
#                 # np.genfromtxt decompresses .gz by default
#                 tids = np.genfromtxt(gz_path, dtype=np.int64, skip_header=1, usecols=(0,))
#                 np.savetxt(csv_path, tids, fmt='%i')
#             except:
#                 pass
#             os.remove(gz_path)
        
#     return np.genfromtxt(csv_path, dtype=np.int64)
    
def get_data_range(start_date, end_date, clean=False, p=360):
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
    # e.g. -> projectdir/data/processed/2020-03-27_2020-03-30_ids.txt
    base = os.path.join(root, 'data/processed', start_date) + f'_{end_date}'
    txt_path = f'{base}_clean_ids.txt' if clean else f'{base}_ids.txt'
    jsonl_path = os.path.splitext(txt_path)[0] + '.jsonl'
    
    if not os.path.isfile(jsonl_path):
        download_data_range_day(start_date, end_date, clean, p)
        hydrate_ids(txt_path, jsonl_path)
    return jsonl_path

def download_data_range_day(start_date, end_date, clean=False, p=360):
    """Downloads tweets for the days between start and end dates.
    
    Dates range from start_date inclusive to end_date exclusive. Attempts
    downloading data if data file doesn't already exist.
       
    Args:
        start_date (str): start of data range. Format YYYY-MM-DD.
        end_date (str): end of data range. Format YYYY-MM-DD.
        clean (bool): specifies whether to download the cleaned data
          (without retweets) or the raw data.
        p (int): rate of tweets to hydrate.
        
    """
    # e.g. -> projectdir/data/processed/2020-03-27_2020-03-30_ids.txt
    base = os.path.join(root, 'data/processed', start_date) + f'_{end_date}'
    txt_path = f'{base}_clean_ids.txt' if clean else f'{base}_ids.txt'
    
    if not os.path.isfile(txt_path):
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
        sample = []  # running list of every p tweet IDs
        for day in daterange(start, end):
            daily = day.isoformat()
            try:
                tmp = get_data_day(daily, clean)
                sample = sample + list(tmp[::p].copy())
            except:
                pass
        sample = np.array(sample)

        np.savetxt(txt_path, sample, fmt='%i')
    return

def get_data_day(daily, clean=False):
    """Downloads tweets for the given day.
    
    First checks if tweets have already been downloaded. If they haven't,
    then download them and save the tweet IDs to a txt file.
       
    Args:
        daily (str): date of data. Format YYYY-MM-DD.
        clean (bool): specifies whether to download the cleaned data
          (without retweets) or the raw data.
    
    Returns:
        All tweet ids from daily.
        
    """
    # e.g. -> projectdir/data/raw/2020-03-27_ids.txt
    base = os.path.join(root, 'data/raw', daily)
    txt_path = f'{base}_clean_ids.txt' if clean else f'{base}_ids.txt'
    
    if not os.path.isfile(txt_path):  # full data doesn't exist
        # e.g. -> 2020-03-27-dataset.tsv.gz
        ext = f'{daily}_clean-dataset.tsv.gz' if clean else f'{daily}-dataset.tsv.gz'
        
        url_base = f'https://raw.githubusercontent.com/thepanacealab/covid19_twitter/master/dailies/{daily}'
        url = os.path.join(url_base, ext)
        
        # e.g. -> projectdir/data/raw/2020-03-27-dataset.tsv.gz
        gz_path = os.path.join(root, 'data/raw', ext)
        
        curl_cmd = f'curl {url} --output {gz_path}'
        subprocess.run(curl_cmd, shell=True)
        
        try:
            # np.genfromtxt decompresses .gz by default
            tids = np.genfromtxt(gz_path, dtype=np.int64, skip_header=1, usecols=(0,))
            np.savetxt(txt_path, tids, fmt='%i')
        except:
            pass
        os.remove(gz_path)
        
    return np.genfromtxt(txt_path, dtype=np.int64)
                
def hydrate_ids(txt_path, jsonl_path):
    """Retrieves tweets given IDs in txt_path using twarc."""
    hydrate_cmd = f'twarc hydrate {txt_path} > {jsonl_path}'
    subprocess.run(hydrate_cmd, shell=True)
    
def download_retweets(tid, jsonl_path):
    """Retrieves retweets given ID using twarc."""
    if not os.path.isfile(jsonl_path):
        rt_cmd = f'twarc retweets {tid} > {jsonl_path}'
        subprocess.run(rt_cmd, shell=True)

def daterange(start, end):
    """Generator for dates between start and end dates.
    
    ref: https://stackoverflow.com/questions/1060279/iterating-through-a-range-of-dates-in-python
    
    Args:
        start (date): start of range inclusive.
        end (date): end of range exclusive.
    
    Yields:
        Next date in range.
        
    """
    for n in range(int((end - start).days)):
        yield start + timedelta(n)
