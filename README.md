
# litecoder

US city + state geocoding, without a heavy webservice. With [Who's On First](https://www.whosonfirst.org/) and SQLite.

It's not uncommon to have free-text "location" fields - for example, from Twitter user profiles - that contain a mix of cities, states, and countries. Eg, things like `Los Angeles, CA`, `Boston`, `DC`, `tuscaloosa al`, `VT` etc. To make use of these, they generally need to be liked against some kind of canonical set of geographic entities. One approach is to throw them at a commercial geocoder like Google Places or Mapbox, but this is slow and expensive, and there are often onerous TOS restrictions on the results. And, really, a full-blown geocoder is overkill here, since these kinds of location fields almost never contain street addresses, just references to a more limited set of cities, regions, and countries. Though, annoyingly, with endless variations in formatting.

This library resolves location strings to entities in the open-source Who's On First gazetteer, which includes really rich geographic metadata (including polygon geometries) as well as IDs for corresponding records in a range of other gazetteers and knowledge databases (Wikipedia, Wikidata, DBpedia, Geonames, Quattroshapes, Freebase, etc). Right now it just supports US cities and states, though in the future

## Goals
- Be very fast. Lookups take ~1ms.
- Work anywhere. The underlying data sits in SQLite and ships with the package. Just `pip install`.
- When in doubt, favor precision over recall. Litecoder will miss some things, but when it returns a result, it will almost certainly be correct.

## Non-Goals
- No support for extracting locations that are embedded inside of surrounding text.
