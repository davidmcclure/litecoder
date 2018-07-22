

import os
import yaml


def read_yaml(from_path, file_name):
    """Open a YAML file relative to the passed path.

    Args:
        from_path (str)
        file_name (str)

    Returns: dict
    """
    path = os.path.join(os.path.dirname(from_path), file_name)

    with open(path, 'r') as fh:
        return yaml.load(fh)
