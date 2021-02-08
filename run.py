import sys
import os

sys.path.insert(0, 'src')

import env_setup
import etl_election
import etl_news
# import eda
import similarity
import hashtags
from utils import get_project_root, load_config



def main(targets):
    """Runs the main project pipeline project, given targets."""
    root = get_project_root()

    env_setup.auth()
    env_setup.make_datadir()

    if 'all' in targets:
        targets = ['data', 'eda']

    if 'data' in targets:
        config = load_config('config/news_params.json')
        etl_news.get_news_data(**config)
        # etl_election.generate_dataset()
        # etl_election.rehydrate_tweets(100)

    if 'eda' in targets:
        eda.main(test=True)

    if 'test' in targets:
        # config = load_config('config/test_params.json')
        # etl_news.get_news_data(**config)


        temp = hashtags.count_features([os.path.join(root, 'test', 'testdata', 'test_election.jsonl')])
        news_vectors = similarity.compile_vectors(os.path.join(root, 'test', 'testdata'), temp)
        # TODO: calculate pairwise similarity among news vectors

if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)
