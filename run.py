import sys
import os

sys.path.insert(0, 'src')

import env_setup
import etl_election
import etl_news
import eda
from utils import get_project_root


def main(targets):
    """Runs the main project pipeline project, given targets."""
    root = get_project_root()

    env_setup.auth()
    env_setup.make_datadir()

    if 'data' in targets:
        etl_news.test()
        # etl_election.generate_dataset()
        # etl_election.rehydrate_tweets(100)
    if 'eda' in targets:
        eda.main()

if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)
