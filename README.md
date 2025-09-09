# wpg-weather-web
This app creates the old-school looking weather channel that was common on Winnipeg cable TV into the 1990s. Instead of being served in a local window, however, this version creates a flask app which serves it to the web, which is better for "broadcasting". Sockets are used to update the weather and news on this site on a regular basis. A radar loop gif is provided too, as well as some astronomical data.

![Example1](/screenshot1.png)
![Example2](/screenshot2.png)
![Example3](/screenshot3.png)
![Example4](/screenshot4.png)

## Usage

For docker, dowload and build the Dockerfile, then run it after exporting variables for your zip code and news feed.

For standalone, just run the python script after installing the requirements listed in the txt file.

You can load up the 'static/img' directory with random loading screens (or just one) and the 'static/audio' directory with your fav weather muzak in mp3 format.

### Music

If you choose to enable music, you will need to interact with the page before it can autoplay. _Click on the clock_ in the top right of the page after it loads to begin playback, or see [Chrome Autoplay Policies](https://developer.chrome.com/blog/autoplay/#developer_switches) to launch a browser with autoplay enabled, if you need to do this on a machine without pointer input.

## Attribution

### Code
The original application was written by [probnot](https://github.com/probnot/wpg-weatherchan), with modifications by [TechSavvvvy](https://github.com/TechSavvvvy/wpg-weatherchan-USA) to use NOAA weather for the U S and A.

### Libraries
This app uses [NOAA-SDK](https://github.com/paulokuong/noaa) to get weather data and radar images from the National Weather Serivce. [Astral](https://github.com/sffjunkie/astral) is the calculation source for sunrise and sunset times. Historical weather records are pulled from [ACIS](https://www.rcc-acis.org/docs_webservices).

County adjacency comes from [pconrad](https://github.com/pconrad/python-county-adjacency), with data via US Census Bureau. FIPS county code translation sourced from [nokane](https://github.com/nokane/FIPS_state_county_codes), and I slammed these together to make a static adjacency JSON file with FIPS codes.

### Media
It also uses the fonts [VCR OSD Mono](https://www.dafont.com/vcr-osd-mono.font) and [SquareFont](https://www.dafont.com/squarefont.font). Included background music is provided by [pixabay](https://pixabay.com/music/) and is AI generated. Included loading screens are also AI generated, posited by me to Gemini 2.5 Flash.

## License

This code is available under the terms of the [MIT License]

This was a pet project to help me learn python, but I also ended up learning about sockets, flask/jinja, and css in the meantime. As a pet project, upkeep is not guaranteed, but forking is welcome.