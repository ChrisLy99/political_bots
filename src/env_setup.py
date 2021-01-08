import os
from utils import get_project_root


root = get_project_root()
cred_fp = os.path.join(root, '.env', 'twarc.yaml')


def make_datadir():
    """Set-up data directories."""

    data_loc = os.path.join(root, 'data')

    for d in ['raw', 'processed']:
        os.makedirs(os.path.join(data_loc, d), exist_ok=True)

    return