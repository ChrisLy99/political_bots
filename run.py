import sys
import os

sys.path.insert(0, 'src')

import env_setup
from utils import get_project_root, load_config
from etl import get_troll_data


def main(targets):
    """Runs the main project pipeline project, given targets."""
    root = get_project_root()
    env_setup.make_datadir()
    
    if 'data' in targets:
        get_troll_data()

if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)