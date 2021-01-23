import os
# import yaml


def get_project_root():
    """Return the root path for the project."""
    curdir = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(curdir, os.pardir))

# def load_config(path):
#     """Load the configuration from config."""
#     return yaml.load(open(path, 'r'), Loader=yaml.Loader)
