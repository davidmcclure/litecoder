
# Litecoder [WIP]

> US city + state geocoding, without a heavy webservice. With [Who's On First](https://www.whosonfirst.org/) and SQLite.

It's not uncommon to have free-text "location" fields - for example, from Twitter user profiles - that contain a mix of cities, states, and countries. Eg, things like:

- `Los Angeles, CA`
- `Boston`
- `bellingham washington`
- `NYC`
- `big apple`
- `tuscaloosa al`
- `VT`

To make use of these, they generally need to be linked against some kind of canonical set of geographic entities. One approach is to throw them at a commercial geocoder like [Google](https://developers.google.com/places/web-service/search) or [Mapbox](https://www.mapbox.com/geocoding/), but this is slow and expensive, and there are often onerous terms-of-service restrictions on the results. And, really, a full-blown geocoder is overkill here, since these kinds of location fields almost never contain street addresses, just references to a smaller set of high-level locations.

Litecoder is a small library (~500 SLOC) resolves location strings to records in the [Who's On First](https://www.whosonfirst.org/) (WOF) gazetteer from Mapzen, which aggregates geographic metadata as well as IDs for corresponding records in a number of other gazetteers and knowledge databases (Wikipedia, Wikidata, DBpedia, Geonames, etc). Mapzen sadly doesn't exist anymore, but the WOF data is [CC-0](https://github.com/whosonfirst-data/whosonfirst-data/blob/master/LICENSE.md).

For now, Litecoder only supports US cities and states.

## Goals
- Be fast. Lookups take ~3ms.
- Work anywhere without hassle. The underlying data sits in SQLite and ships with the package - just `pip install`. Since everything is totally embedded, it can be used in ETL and big data workflows involving billions of inputs.
- Favor precision over recall. Litecoder will miss some things, but when it returns a result, it should be trustworthy.
- Support non-standard names that clearly refer to a city or state. Eg, `NYC` always means New York City.
- Some heuristics are unavoidable - eg, `Boston` should map to `Boston, MA`, not `Boston, GA` (which exists!). In these cases, do something simple and easy to reason about.

## Non-Goals
- No support yet for extracting locations that are embedded inside of surrounding text. The assumption is that you've got a snippet of text that represents a location, and the goal is to figure out which one.
- Nothing more granular than the city / town. (With the exception of NYC boroughs, which map to NYC.)

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
