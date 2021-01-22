'''
This file sets up necessary data directories and loads in API keys
'''
import os
import json
from utils import get_project_root


root = get_project_root()
cred_fp = os.path.join(root, '.env', 'twitter_credentials.json')

def auth():
    """Set-up keys for authentication to twitter API"""
    try:
        creds = json.load(open(cred_fp))
    except Exception as e:
        print('API key file has not been properly set up!')
        return

    os.environ['CONSUMER_KEY'] = creds.get('CONSUMER_KEY')
    os.environ['CONSUMER_SECRET'] = creds.get('CONSUMER_SECRET')
    os.environ['ACCESS_TOKEN'] = creds.get('ACCESS_TOKEN')
    os.environ['ACCESS_TOKEN_SECRET'] = creds.get('ACCESS_TOKEN_SECRET')

    return

def make_datadir():
    """Set-up data directories."""

    data_loc = os.path.join(root, 'data')

    for d in ['raw', 'processed']:
        for d_2 in ['election', 'news']:
            os.makedirs(os.path.join(data_loc, d, d_2), exist_ok=True)

    return
