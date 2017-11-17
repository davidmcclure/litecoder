

import yaml
import os


def read_yaml(root, *path_parts):
    """Parse a YAML file relative to the passed path.

    Args:
        root (str)
        path_parts (list of str)

    Returns: dict
    """
    path = os.path.join(os.path.dirname(root), *path_parts)

    with open(path, 'r') as fh:
        return yaml.load(fh)
