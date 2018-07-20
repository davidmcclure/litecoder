
# litecoder

> US city + state geocoding, without a heavy webservice. With [Who's On First](https://www.whosonfirst.org/) and SQLite.

It's not uncommon to have free-text "location" fields - for example, from Twitter user profiles - that contain a mix of cities, states, and countries. Eg, things like `Los Angeles, CA`, `Boston`, `DC`, `tuscaloosa al`, `VT` etc. To make use of these, they generally need to be liked against some kind of canonical set of geographic entities. One approach is to throw them at a commercial geocoder like Google Places or Mapbox, but this is slow and expensive, and there are often onerous TOS restrictions on the results. And, really, a full-blown geocoder is overkill here, since these kinds of location fields almost never contain street addresses, just references to a more limited set of cities, regions, and countries. Though, annoyingly, with endless variations in formatting.

This library resolves location strings to entities in the open-source Who's On First gazetteer, which includes really rich geographic metadata as well as IDs for corresponding records in a range of other gazetteers and knowledge databases (Wikipedia, Wikidata, DBpedia, Geonames, Freebase, etc).

For now, Litecoder only supports US cities and states.

## Goals
- Be very fast. Lookups take ~3ms.
- Work anywhere without hassle. The underlying data sits in SQLite and ships with the package - just `pip install`. Since Litecoder is totally embedded, it can be used in ETL and big data workflows involving billions of inputs.
- Be unsurprising. When in doubt, favor precision over recall. Litecoder will miss some things, but when it returns a result, it should almost always be correct.
- Support non-standard names that unambiguously refer to a city or state. Eg, `NYC` always means New York City.
- Some heuristics are unavoidable - eg, `Boston` should map to `Boston, MA`, not `Boston, GA` (which exists!). In these cases, use rules that are simple and interpretable.

## Non-Goals
- No support yet for extracting locations that are embedded inside of surrounding text. The assumption is that you've got a snippet of text that represents a location, and the goal is to figure out which one.
- No support for entities more granular than the city / town. (With the exception of NYC boroughs, which map to NYC.)

## Examples

```python
from litecoder.us_cities import USCityIndex

# Load the pre-built index. You can also build your own (see below), but this
# is only useful if you want to implement custom indexing logic, provide custom
# alternate-name lists, etc.
idx = USCityIndex.load()

# Basic city, state, country.
idx.query('Boston, Massachusetts')
idx.query('Boston, MA')
idx.query('Boston, MA, USA')
>> [City<85950361, Boston, Massachusetts, United States>]

# Normalize differences in capitalization, spacing, commas.
idx.query('boston, ma')
idx.query('boston ma')
idx.query('BOSTON MA')
>> [City<85950361, Boston, Massachusetts, United States>]

# For major cities, match the "bare" city name.
idx.query('Boston')
>> [City<85950361, Boston, Massachusetts, United States>]

# Since "Boston" alone almost certainly doesn't refer to Boston, GA!
idx.query('Boston, GA')
>> [City<85936819, Boston, Georgia, United States>]

# But don't guess when there isn't a clear "major" city.
idx.query('Springfield')
>> []

# Match major abbreviations, alternate names, nicknames.
idx.query('NYC')
idx.query('New York City')
idx.query('Big Apple')
idx.query('Nueva York')
>> [City<85977539, New York, New York, United States>]

# For small cities with names that are unique among all ~350k international
# cities, match the bare name.
idx.query('Tuscaloosa')
>> [City<85914453, Tuscaloosa, Alabama, United States>]
```
