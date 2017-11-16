

from itertools import groupby


def isplit(it, keyfunc):
    """Split an iterable on a value. Like str.split().
    """
    return [list(g) for k, g in groupby(it, keyfunc) if not k]
