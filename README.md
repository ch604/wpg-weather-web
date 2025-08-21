# wpg-weather-web
This app creates the old-school looking weather channel that was common on Winnipeg cable TV into the 1990s. Instead of being served in a local window, however, this version creates a flask app which serves it to the web, which is better for "broadcasting". Sockets are used to update the weather and news on this site on a regular basis. A radar loop gif is provided too, as well as some astronomical data.

![Example1](/screenshot1.png)
![Example2](/screenshot2.png)
![Example3](/screenshot3.png)
![Example4](/screenshot4.png)

## Usage

For docker, dowload and build the Dockerfile, then run it after exporting variables for your zip code and news feed.

For standalone, just run the python script after installing the requirements listed in the txt file.

### Music

If you choose to enable music, you will need to interact with the page before it can autoplay. _Click on the clock_ in the top right of the page after it loads to begin playback, or see [Chrome Autoplay Policies](https://developer.chrome.com/blog/autoplay/#developer_switches) to launch a browser with autoplay enabled, if you need to do this on a machine without pointer input.

## Attribution

The original application was written by [probnot](https://github.com/probnot/wpg-weatherchan), with modifications by [TechSavvvvy](https://github.com/TechSavvvvy/wpg-weatherchan-USA) to use NOAA weather for the U S and A.

This app uses [NOAA](https://github.com/paulokuong/noaa) to get the weather data and radar images from the National Weather Serivce. [Astral](https://github.com/sffjunkie/astral) is the calculation source for sunrise and sunset times.

It also uses the fonts [VCR OSD Mono](https://www.dafont.com/vcr-osd-mono.font) and [SquareFont](https://www.dafont.com/squarefont.font). Background music is provided by [pixabay](https://pixabay.com/music/) and is AI generated.

## License

This code is available under the terms of the [MIT License]
