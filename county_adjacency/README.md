# python-county-adjacency
A simple Python library that wraps US County Adjacency data

By Phill Conrad

# What this library does

This library provides a Python code that processes the data in the file [county_adjacency.txt](https://www2.census.gov/geo/docs/reference/county_adjacency.txt) (a copy of which is cached in this repo) as explained at the [US Census website](https://www.census.gov/geo/reference/county-adjacency.html).  It turns this data into a JSON representation that easily allows a user to determine, for any US county, what counties are adjacent to that county (i.e. share a border with it.)

For the current version of the library, only the data for US states and the District of Columbia  is included, since the intended use case of the library is for mashups with data that corresponds to those counties.  The District of Columbia is treated, for purposes of the library as a 51st state with a single county.   (Future work might extend this to the data in the file for US Territories (Puerto Rico, American Samoa, Guam, Northern Mariana Islands, and the Virgin Islands.)

The library also provides a set convenience functions for doing computations over this data such as computing the first level neighborhood, second level neighborhood, etc.

# The JSON produced

The JSON produced has this form:

```json
{ "AL Autauga" : [
     "AL Autauga",
     "AL Chilton",
     "AL Dallas",
     "AL Elmore",
     "AL Lowndes",
     "AL Montgomery"
     ],
  "AL Baldwin" : [
       "AL Baldwin",
       "AL Clarke",
       "AL Escambia",
       "AL Mobile",
       "AL Monroe",
       "AL Washington",
       "FL Escambia"
     ],
  ...
  "WY Weston" : [
	"SD Custer",
	"SD Lawrence",
	...
	"WY Weston"
  ]
}

We have prefixed each county name with its state abbreviation since there are cases of the same county name occuring in multiple states (e.g. Escambia is both a county in Alabama and a separate, adjacent county in Florida.   

For comparison, here are corresponding lines of the input file.  Note that we have removed the word "county", since it creates an ambiguity (Louisiana uses the word "parish" instead of "county", and the District of Columbia is called simply that, i.e. `"District of Columbia, DC"`.   

```
"Autauga County, AL"	01001	"Autauga County, AL"	01001
		"Chilton County, AL"	01021
		"Dallas County, AL"	01047
		"Elmore County, AL"	01051
		"Lowndes County, AL"	01085
		"Montgomery County, AL"	01101
"Baldwin County, AL"	01003	"Baldwin County, AL"	01003
		"Clarke County, AL"	01025
		"Escambia County, AL"	01053
		"Mobile County, AL"	01097
		"Monroe County, AL"	01099
		"Washington County, AL"	01129
		"Escambia County, FL"	12033
```
# Details

Counties are provided for:
* all 50 US States (accessed by their standard USPS two-letter state abbreviations)
* the District of Columbia ("DC"), treated as a single county equivalent for purposes of this dataset

Note that in Louisiana, the equivalent of a county is called a "parish". 

Counties are also provided for the following US territories.  A flag can be set to include or exclude these territories from the data, since including or excluding them may be approrpriate depending on the use case.  To keep the API simple, when they are included, they are treated as "states" for purposes of the API, even though their legal status is different from that of a US state.   Each of these has its own designator for what a "county equivalent" is called.

| Territory | Code | County Equivalent |
|-----------|----------------------|
|  Puerto Rico | PR | Municipio |
|  American Samoa | AS | Island or District (both appear in the data) |
|  Guam | GU| (treated as a single county)|
|  Northern Mariana Islands | MP | Municipality |
|  Virgin Islands | VI | Island |


# Motiviation

Suppose you are accessing data by US county, for example, [this dataset](https://think.cs.vt.edu/corgis/json/food_access/food_access.html) from the United States Department of Agriculture's Economic Research Service.   That data set contains information about access to sources of healthy and affordable food (and is provided courtesy of the [Corgis project at Virginia Tech](https://think.cs.vt.edu/corgis/).

You might first be interested in data for your own county.  Then, you might be interested in data about your state&mdash;however most states have so many counties that the amount of data you could be overwhelming.  

A more reasonable subset of the data that might be interesting to you is that counties that border on your own&mdash;we can call these "first level neighbors". 

For example, the first level neighbors of Santa Barbara County, California are Santa Barbara county itself, plus the counties of Kern, San Luis Obispo, and Ventura, since they all share a border with Santa Barbara county. (It is convenient to list the neighbors in alphabetical order to avoid any ambiguity, and help us more easily detect any duplicates, and compare lists.)

The second level neighbors include the first level neighbors, and any counties that are first level neighbors of those.   For example, to compute the second level neighbors of Santa Barbara County, we can start with the first level neighbors of the first level neighbors:

* The first level neighbors of Kern are Inyo, Kern, Kings, Los Angeles, San Bernadino, San Luis Obispo, Santa Barbara, Tulare and Ventura.
* The first level neighbors of San Luis Obispo are Kings, Monterey, San Luis Obispo County, and Santa Barbara
* The first level neighbors of Ventura are Kern, Santa Barbara and Los Angeles and Ventura

We then combine these lists together and throw out duplicates (i.e. the "set union" in math terminology), to get the second level neighbors of Santa Barbara county:  Inyo, Kern, Kings, Monterey, Los Angeles, San Bernadino, San Luis Obispo, Santa Barbara, Tulare and Ventura.

Higher level neighbors (third, fourth, etc.) are defined in a similar fashion.  (We're trying to keep this presentation at an level that can be understood by novice programmers, so we are avoiding going into the formal graph theory definitions&mdash;but students of discrete math and linear algebra will see immediately how to apply the concepts of vertex, edge, distance, etc.)


# Format of the file

The first line for a county's data group has the county name, and the first neighbor (if any).  Then there are 0 or more additional indented lines with additional neighbors.

```
"Santa Barbara County, CA"	06083	"Kern County, CA"	06029
		"San Luis Obispo County, CA"	06079
		"Santa Barbara County, CA"	06083
		"Ventura County, CA"	06111
```

Also note in the data file every county also lists itself as a neighbor.  So, a county that is isolated (has only itself for a neighbor&mdash;as in the case of three of Hawaii's counties, and the territory of Guam), has only one line, with itself listed as the single neighbor.  For example, here is the entire listing of counties for the state of Hawaii:

```
"Hawaii County, HI"	15001	"Hawaii County, HI"	15001
"Honolulu County, HI"	15003	"Honolulu County, HI"	15003
"Kalawao County, HI"	15005	"Kalawao County, HI"	15005
		"Maui County, HI"	15009
"Kauai County, HI"	15007	"Kauai County, HI"	15007
"Maui County, HI"	15009	"Kalawao County, HI"	15005
		"Maui County, HI"	15009
```

You might want to bring up data for your own county, and The file https://www2.census.gov/geo/docs/reference/county_adjacency.txt has data for US County adja
