

from wordfreq import top_n_list

from .indexes import state_index, city_index


topn = set(top_n_list('en', 100))


class TwitterGeocoder:

    def __init__(self):
        self.cities = {}
        self.states = {}

    def add_ngram(self, ngram):
        """Register state / city for ngram.
        """
        # Skip very frequent words. (in / Indiana, or / Oregon)
        # But, allow all-caps frequent words. (IN, OR)
        if ngram.key in topn and not ngram.text.isupper():
            return

        state = state_index.get(ngram.key)

        if state:
            self.states[state.abbr] = state

        else:

            cities = city_index.get(ngram.key)

            if cities:
                self.cities[ngram.key] = cities

    def max_city_key_len(self):
        """Get size of the longest city index key.
        """
        key_lens = [len(k) for k in self.cities.keys()]

        return max(key_lens) if key_lens else 0

    def max_len_cities(self):
        """Generate cities with longest keys.
        """
        max_len = self.max_city_key_len()

        for key, cities in self.cities.items():
            if len(key) == max_len:
                yield from cities

    def pop_ranked_cities(self):
        """Order city candidates by population.
        """
        return sorted(
            self.max_len_cities(),
            key=lambda c: c.population,
            reverse=True,
        )

    def city_state(self, pop_threshold = 250000):
        """Extract city and/or state.
        """
        res_city, res_state = None, None

        cities = self.pop_ranked_cities()

        # 1+ cities, no state - take highest-pop city.
        if cities and not self.states:
            if cities[0].population > pop_threshold:
                res_city = cities[0]

        # 1 state, 0 cities.
        elif len(self.states) == 1 and len(cities) == 0:
            res_state = list(self.states.values())[0]

        # 2+ cities, 1+ states - look for city / state pair.
        elif cities and self.states:
            for city in cities:
                if city.admin1_code in self.states:
                    res_city = city
                    break

        # Get state for matched city.
        if res_city:
            res_state = state_index[res_city.admin1_code]

        return res_city, res_state
