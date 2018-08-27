
# Litecoder

> US city + state geocoding, without a heavy webservice. With [Who's On First](https://www.whosonfirst.org/) and SQLite.

Sometimes you've got "location" fields that contain a weird mix of cities and states. Stuff like:

- `SF`
- `Los Angeles, CA`
- `Boston`
- `California`
- `bellingham washington`
- `NYC`
- `tuscaloosa AL`
- `big apple`

To make use of these, they generally need to be linked against some kind of canonical set of geographic entities. One approach is to throw them at a commercial geocoder like [Google](https://developers.google.com/places/web-service/search) or [Mapbox](https://www.mapbox.com/geocoding/), but this is slow and expensive, and there are often [onerous terms-of-service restrictions](https://www.mapbox.com/tos/#[YmouYmoq]) on the results. And, really, a full-blown geocoder is overkill here, since these kinds of location fields almost never contain street addresses, just references to a smaller set of high-level locations.

Litecoder is a small library that links these kinds of free-text location strings to records in the [Who's On First](https://www.whosonfirst.org/) (WOF) gazetteer from Mapzen, which includes both high-quality geographic metadata as well as IDs for corresponding records in a number of other gazetteers and knowledge databases (Wikipedia, Wikidata, DBpedia, Geonames, etc). Mapzen sadly doesn't exist anymore, but the WOF data is [CC-0](https://github.com/whosonfirst-data/whosonfirst-data/blob/master/LICENSE.md).

For now, Litecoder only supports US cities and states.

## Now
- Be fast. Lookups take ~20µs.
- Work anywhere without hassle. The underlying data ships with the package and is small enough to fit in memory (~100m). Since everything sits in RAM, the library can be used in ETL and big data workflows involving billions of inputs.
- Comprehensive support for [nicknames and abbreviations](litecoder/data/city-alt-names.yml). Eg, `Windy City` always means Chicago.
- Some heuristics are unavoidable - eg, `Boston` should map to `Boston, MA`, not `Boston, GA` (which exists!). In these cases, do something simple and easy to reason about.

## Future
- Match locations embedded inside of surrounding text. For now, the assumption is that you've got a snippet of text that represents a location, and the goal is to figure out which one.
- Locations more granular than cities / towns - major parks, venues, etc.
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
idx['   boston   ma   ']
idx['BOSTON MA']
>> [CityMatch<Boston, Massachusetts, United States, wof:85950361>]

# For major cities, match the "bare" city name.
idx['Boston']
>> [CityMatch<Boston, Massachusetts, United States, wof:85950361>]

# Since "Boston" alone (almost) never refers to Boston, GA!
idx['Boston, GA']
>> [CityMatch<Boston, Georgia, United States, wof:85936819>]

# But don't guess when there isn't a clear "major" city...
idx['Springfield']
>> []

# ... Until more detail is provided.
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

## Metadata

The city and state indexes return "match" objects that act as proxies for the underlying data in SQLite. These objects store all metadata associated with the location, as well as denormalized copies of parent entities.

### US cities

```python
idx = USCityIndex.load()

sf = idx['San Francisco'][0]

sf.data.name
>> 'San Francisco'

sf.data.population
>> 805235

sf.data.latitude
>> 37.759715

sf.data.longitude
>> -122.693976

sf.data.region.name_abbr
>> 'CA'

sf.data.to_dict()
>>
{'area_m2': 600307527.980684,
 'country_iso': 'US',
 'dbp_id': 'San_Francisco',
 'duplicate': False,
 'elevation': 16,
 'fb_id': 'en.san_francisco',
 'fct_id': '08cb9cb0-8f76-11e1-848f-cfd5bf3ef515',
 'fips_code': '667000',
 'gn_id': 5391959,
 'gp_id': 2487956,
 'latitude': 37.759715,
 'loc_id': 'n79018452',
 'longitude': -122.693976,
 'name': 'San Francisco',
 'name_a0': 'United States',
 'name_a1': 'California',
 'nyt_id': '9223372036854775807',
 'population': 805235,
 'qs_id': 240388,
 'qs_pg_id': 240388,
 'region': {'area_m2': 423822167986.13293,
  'country_iso': 'US',
  'fips_code': 'US06',
  'gn_id': 5332921,
  'gp_id': 2347563,
  'hasc_id': 'US.CA',
  'iso_id': 'US-CA',
  'latitude': 37.215297,
  'longitude': -119.663837,
  'name': 'California',
  'name_a0': 'United States',
  'name_abbr': 'CA',
  'population': 37253956,
  'unlc_id': 'US-CA',
  'wd_id': 'Q99',
  'wof_continent_id': 102191575,
  'wof_country_id': 85633793,
  'wof_id': 85688637},
 'wd_id': 'Q62',
 'wikipedia_wordcount': None,
 'wk_page': 'San Francisco',
 'wof_continent_id': 102191575,
 'wof_country_id': 85633793,
 'wof_id': 85922583,
 'wof_region_id': 85688637}
```

Or, use the `db_row` attribute, which (lazily) queries the underlying SQLite database.

```python
sf.db_row
>> WOFLocality<San Francisco, California, United States, wof:85922583>
```

This usually shouldn't be needed, since a copy of the metadata is stored under `data`. This means that Litecoder can be used in parallelized / distributed environments where highly concurrent SQLite queries would be problematic. For example, in a Spark job, a Litecoder index can be serialized and shipped to workers just like any other variable.

### US states

```python
idx = USStateIndex.load()

ca = idx['California'][0]

ca.data.name
>> 'California'

ca.data.population
>> 37253956

ca.data.area_m2
>> 423822167986.13293

ca.data.to_dict()
>>
{'area_m2': 423822167986.13293,
 'country_iso': 'US',
 'fips_code': 'US06',
 'gn_id': 5332921,
 'gp_id': 2347563,
 'hasc_id': 'US.CA',
 'iso_id': 'US-CA',
 'latitude': 37.215297,
 'longitude': -119.663837,
 'name': 'California',
 'name_a0': 'United States',
 'name_abbr': 'CA',
 'population': 37253956,
 'unlc_id': 'US-CA',
 'wd_id': 'Q99',
 'wof_continent_id': 102191575,
 'wof_country_id': 85633793,
 'wof_id': 85688637}

# Generates SQLite query.
ca.db_row
>> WOFRegion<California, United States, wof:85688637>
```
