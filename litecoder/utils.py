

import ujson


class safe_property:

    @classmethod
    def cached(cls, func):
        return cls(func, True)

    def __init__(self, func, cached=False):
        self.cached = cached
        self.__doc__ = getattr(func, "__doc__")
        self.func = func

    def __get__(self, obj, cls):
        """Try to set a cached property. Catch and record errors.
        """
        if obj is None:
            return self

        try:
            value = self.func(obj)
        except Exception as e:
            value = None

        # Replace attribute with computed value.
        if self.cached:
            obj.__dict__[self.func.__name__] = value

        return value


def first(*seq):
    return next((x for x in seq if x is not None), None)


def read_json(path):
    with open(path) as fh:
        return ujson.load(fh)
