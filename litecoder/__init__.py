

from .parsers import LocationField
from .geocoders import TwitterGeocoder


def geocode_twitter(text):
    """Given a Twitter location text, match to a city and/or state.
    """
    field = LocationField.from_text(text)

    geocoder = TwitterGeocoder()

    for ngram in field.candidate_toponyms():
        geocoder.add_ngram(ngram)

    return geocoder.city_state()
