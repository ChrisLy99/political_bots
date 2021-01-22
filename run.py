import sys
import os

sys.path.insert(0, 'src')

import env_setup
from utils import get_project_root, load_config
from etl import get_news_rts


def main(targets):
    """Runs the main project pipeline project, given targets."""
    root = get_project_root()
    env_setup.make_datadir()
    
    if 'data' in targets:
        get_news_rts()

if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)