# wpg-weather-web
This app creates the old-school looking weather channel that was common on Winnipeg cable TV into the 1990s. Insteqad of being served on the local browser, this version creates a flask app which serves it to the web, which is better for "broadcasting".

![Example1](/wpg-1.jpg)
![Example2](/wpg-2.jpg)

## Usage

For docker, dowload and build the Dockerfile, then run it after exporting variables for your city and news feed.

For standalone, just run the python script after installing the requirements listed in the txt file.

## Attribution

The original application was written by [probnot](https://github.com/probnot/wpg-weatherchan), with modifications by [TechSavvvvy](https://github.com/TechSavvvvy/wpg-weatherchan-USA) to use NOAA weather for the U S and A.

This app uses [NOAA](https://github.com/paulokuong/noaa) to get the weather data from the National Weather Serivce. It also uses the fonts [VCR OSD Mono](https://www.dafont.com/vcr-osd-mono.font) and [SquareFont](https://www.dafont.com/squarefont.font).

## License

This code is available under the terms of the [MIT License]
