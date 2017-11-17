

from wordfreq import top_n_list

from .db import state_index, city_index


topn = set(top_n_list('en', 100))


class TwitterUSACityStateQuery:

    def __init__(self):
        self.cities = []
        self.states = []

    def add_ngram(self, ngram):
        """Register state / city for ngram.
        """
        key = ngram.key()
        text = ngram.text()

        # Skip very frequent words. (in / Indiana, or / Oregon)
        # But, allow all-caps frequent words. (IN, OR)
        if not text.isupper() and key in topn:
            return

        state = state_index.get(ngram.key())

        if state:
            self.states.append(state)

        # Skip cities with same names as states.
        else:
            for city in city_index[ngram.key()]:
                self.cities.append(city)

    def max_city_key_len(self):
        """Get size of the longest city index key.
        """
        key_lens = [len(c.key()) for c in self.cities]

        return max(key_lens) if key_lens else 0

    def max_len_cities(self):
        """Generate cities with longest keys.
        """
        max_len = self.max_city_key_len()

        for city in self.cities:
            if len(city.key()) == max_len:
                yield city

    def pop_ranked_cities(self):
        """Order city candidates by population.
        """
        return sorted(
            self.max_len_cities(),
            key=lambda c: c.population,
            reverse=True,
        )

    def state_abbrs(self):
        return set([s.abbr for s in self.states])

    def city_state(self, pop_threshold = 250000):
        """Extract city and/or state.
        """
        res_city, res_state = None, None

        cities = self.pop_ranked_cities()

        # 1+ cities, no state - take highest-pop city, if the population is
        # above a reasonable threshold.
        if cities and not self.states:
            if cities[0].population > pop_threshold:
                res_city = cities[0]

        # 1 state, 0 cities.
        elif len(self.states) == 1 and len(cities) == 0:
            res_state = self.states[0]

        # 2+ cities, 1+ states - look for city / state pair.
        elif cities and self.states:

            state_abbrs = self.state_abbrs()

            for city in cities:
                if city.admin1_code in state_abbrs:
                    res_city = city
                    break

        # Get state for matched city.
        if res_city:
            res_state = state_index[res_city.admin1_code]

        return res_city, res_state
