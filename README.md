
# Litecoder

> US city + state geocoding, without a heavy webservice. With [Who's On First](https://www.whosonfirst.org/) and SQLite.

It's not uncommon to have free-text "location" fields - for example, from Twitter user profiles - that contain a mix of cities, states, and countries. Eg, things like:

- `Los Angeles, CA`
- `Boston`
- `bellingham washington`
- `NYC`
- `tuscaloosa al`
- `big apple`

To make use of these, they generally need to be linked against some kind of canonical set of geographic entities. One approach is to throw them at a commercial geocoder like [Google](https://developers.google.com/places/web-service/search) or [Mapbox](https://www.mapbox.com/geocoding/), but this is slow and expensive, and there are often [onerous terms-of-service restrictions](https://www.mapbox.com/tos/#[YmouYmoq]) on the results. And, really, a full-blown geocoder is overkill here, since these kinds of location fields almost never contain street addresses, just references to a smaller set of high-level locations.

Litecoder is a small library that resolves location strings to records in the [Who's On First](https://www.whosonfirst.org/) (WOF) gazetteer from Mapzen, which aggregates geographic metadata as well as IDs for corresponding records in a number of other gazetteers and knowledge databases (Wikipedia, Wikidata, DBpedia, Geonames, etc). Mapzen sadly doesn't exist anymore, but the WOF data is [CC-0](https://github.com/whosonfirst-data/whosonfirst-data/blob/master/LICENSE.md).

For now, Litecoder only supports US cities and states.

## Goals
- Be fast. Lookups take ~20µs.
- Work anywhere without hassle. The underlying data ships with the package, and gets pulled into memory when an index is loaded (~100m). Since everything sits in RAM, the library can be used in ETL and big data workflows involving billions of inputs. (And if you want, it's easy to access the underlying relational data in SQLite.)
- First-class support for nicknames and abbreviations. Eg, `NYC` always means New York City, `Windy City` means Chicago.
- Favor precision over recall. Litecoder will miss some things, but when it returns a result, it should be trustworthy.
- Some heuristics are unavoidable - eg, `Boston` should map to `Boston, MA`, not `Boston, GA` (which exists!). In these cases, do something simple and easy to reason about.

## Future / TBD
- No support (yet) for extracting locations that are embedded inside of surrounding text. The assumption is that you've got a snippet of text that represents a location, and the goal is to figure out which one.
- Nothing more granular than the city / town. (With the exception of NYC boroughs, which map to NYC.)
- International cities + countries.

## Examples

### US cities

```python
from litecoder.usa import USCityIndex

# Load the pre-built index.
idx = USCityIndex.load()
>> USCityIndex<630774 keys, 53219 entities>

# Basic city, state, country.
idx['Boston, Massachusetts']
idx['Boston, MA']
idx['Boston, MA, USA']
>> [CityMatch<Boston, Massachusetts, United States, wof:85950361>]

# Normalize differences in capitalization, spacing, commas.
idx['boston, ma']
idx['boston ma']
idx['BOSTON MA']
>> [CityMatch<Boston, Massachusetts, United States, wof:85950361>]

# For major cities, match the "bare" city name.
idx['Boston']
>> [CityMatch<Boston, Massachusetts, United States, wof:85950361>]

# Since "Boston" alone almost certainly doesn't refer to Boston, GA!
idx['Boston, GA']
>> [CityMatch<Boston, Georgia, United States, wof:85936819>]

# But don't guess when there isn't a clear "major" city.
idx['Springfield']
>> []
idx['Springfield, IL']
>> [CityMatch<Springfield, Illinois, United States, wof:85940429>]

# Match major abbreviations, alternate names, nicknames.
idx['NYC']
idx['New York City']
idx['Big Apple']
idx['Nueva York']
>> [CityMatch<New York, New York, United States, wof:85977539>]
```

### US states

```python
from litecoder.usa import USStateIndex

# Load the pre-built index.
idx = USStateIndex.load()
>> USStateIndex<561 keys, 51 entities>

# Basic state, country.
idx['Massachusetts']
idx['Massachusetts, USA']
>> [StateMatch<Massachusetts, United States, wof:85688645>]
```
