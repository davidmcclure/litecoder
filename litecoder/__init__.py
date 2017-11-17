

from .queries import TwitterUSACityStateQuery
from .parsers import LocationField


def twitter_usa_city_state(text):
    """Given a Twitter location text, match to a city and/or state.
    """
    field = LocationField.from_text(text)

    query = TwitterUSACityStateQuery()

    for ngram in field.candidate_toponyms():
        query.add_ngram(ngram)

    return query.city_state()
