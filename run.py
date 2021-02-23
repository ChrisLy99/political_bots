import sys
import os
sys.path.insert(0, 'src')
import env_setup
import etl_election
import etl_news
import eda
import similarity
import hashtags
import pandas as pd
from utils import get_project_root, load_config



def main(targets):
    """Runs the main project pipeline project, given targets."""
    root = get_project_root()

    if 'setup-dsmlp' in targets:
        env = load_config("config/env_dsmlp.json")
        for root, _, files in os.walk(env['src']):
            base_dir = os.path.basename(os.path.normpath(root))
            for name in files:
                file_src = os.path.join(root, name)
                file_dst = os.path.join(env['dst'], base_dir, name)
                if not os.path.exists(file_dst):
                    os.symlink(file_src, file_dst)

    if 'test' not in targets:
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
        eda.main()

    if 'test' in targets:
        config = load_config('config/test_params.json')
        etl_news.get_news_data(**config)

        eda.main(test=True)

        # hashtag vector from the election dataset
        temp = hashtags.count_features([os.path.join(root, 'test', 'testdata', 'test_election.jsonl')])
        # hashtag vector for each news stations
        news_vectors = similarity.compile_vectors(os.path.join(root, 'test', 'testdata'), temp)
        result_path = os.path.join(root, 'test', 'testreport')
        pd.Series(news_vectors).to_json(os.path.join(result_path, 'news_vector.json'))
        temp.to_json(os.path.join(result_path, 'election_vector.json'))
        # TODO: calculate pairwise similarity among news vectors

if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)
