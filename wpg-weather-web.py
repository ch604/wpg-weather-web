# Retro Winnipeg Weather Channel
# Original By probnot
# Updated/modified for USA by TechSavvvvy
# Updated for web by ch604

import time, linecache, sys, json
import feedparser, requests # for RSS feed
import random, os # for background music
from datetime import datetime
from dateutil import tz

# for weather data
from noaa_sdk import NOAA

# for location data
import zipcodes

# for almanac data
import astral
from astral.sun import sun
from astral.moon import moonrise, moonset, phase

# for serving sites and making websocket
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from threading import Thread, Event

####################### variables
prog = "wpg-weather-web"
title = "⛅ WPG WEATHER CHANNEL"
ver = "3.1"

## "music" Enables or disables music player, ON to turn it on, and anyhing else to disable it.
music = os.getenv('WPG_MUSIC', default="ON")
## "rss_feed" is the source for local news feeds.
rss_feed = os.getenv('WPG_RSSFEED', default="https://feeds.nbcnews.com/nbcnews/public/news")
## rss_speed is the speed of the news feed ticker (1 is slow, 3 is fast)
rss_speed = os.getenv('WPG_RSSSPEED', default=2)
match rss_speed:
	case 3:
		rss_speed_divisor = 20
	case 1:
		rss_speed_divisor = 10
	case _:
		rss_speed_divisor = 15
## "homezip" is a valid US zip code.
homezip = os.getenv('WPG_HOMEZIP', default="60601")
## "extrazips" is an array of 21 additional zip codes which support extra pages of "nationwide weather"
extrazips = ["48127","42127","10001","98039","60007","47750","43537","77301","43004","36043","27513","95758","32301","20500","27948","96795","90001","89166","29572","27959","14301"]

noaa_user_agent = prog + " (github.com/ch604/wpg-weather-web)"

####################### classes and functions
# store city data for a given zip code, functions to call noaa api and return weather for that city.
class City:
	def __init__(self, zip):
		z = ZipData(zip)
		self.zip = zip
		self.city = z.city
		self.state = z.state
		self.location = self.city + ", " + self.state
		self.lat = float(z.zipdata['lat'])
		self.long = float(z.zipdata['long'])
		self.timezone = z.zipdata['timezone']
		self.pointProperties = n.points(z.get_latlong_str())['properties']
	
	def get_current_conditions(self):
		# returns a json array of the current observations by the closest station to the stored zip
		if self.zip:
			for i in n.get_observations_by_lat_lon(self.lat, self.long):
				return i
				break
		return None

	def get_daily_forecast(self):
		# returns a json array of 14 day/night forecasts (7 days)
		if self.zip:
			return n.get_forecasts(self.zip, 'US', type='forecast')
		return None
	
	def get_sevenday_forecast(self):
		# returns a json array of upcoming day forecasts, excluding today
		if self.zip:
			res = n.get_forecasts(self.zip, 'US', type='forecast')
			out = []
			for i in res:
				if i['isDaytime'] == True and i['name'] != "Today":
					out.append(i)
			return out
		return None

	def get_hourly_forecast(self):
		# returns a json array of 156h of forecasts (about 7 days worth). filter with [0] for current conditions
		if self.zip:
			return n.get_forecasts(self.zip, 'US', type='forecastHourly')
		return None
	
	def get_radar_url(self):
		# populates self.radar with url of 45m historical loop.
		if self.pointProperties:
			return "https://radar.weather.gov/ridge/standard/" + self.pointProperties['radarStation'] + "_loop.gif"
		return None

	def get_alerts(self):
		# returns a json object of alerts for the area. 
		if self.pointProperties:
			return n.active_alerts(zone_id=self.pointProperties['forecastZone'].rsplit('/', 1)[-1])
		return None


# translate location data from a zip code
class ZipData:
	def __init__(self, zip):
		if zipcodes.is_real(zip):
			self.zipdata = zipcodes.matching(zip)[0]
			self.state = self.zipdata['state'].upper()
			self.city = self.zipdata['city'].upper()
		return None
	
	def get_latlong_str(self):
		if self.zipdata:
			return self.zipdata['lat'] + "," + self.zipdata['long']
		return None


# object to store weather data json arrays
class Weather:
	def __init__(self, zip):
		# save self.city to reference City object and functions later
		self.city = City(zip)
		self.radarimg = self.city.get_radar_url()
	
	def get_weather(self):
		debug_msg("pulling weather for %s (%s)" % (self.city.city, self.city.zip))
		self.update_time()
		self.current = self.city.get_current_conditions()
		self.visibility = m_to_mi(int(self.current['visibility']['value']))
		if self.current['dewpoint']['value']:
			self.dewpoint = c_to_f(float(str(self.current['dewpoint']['value'])))
		else:
			self.dewpoint = ""
		if self.current['heatIndex']['value']:
			self.heatindex = c_to_f(float(str(self.current['heatIndex']['value'])))
		else:
			self.heatindex = ""
		if self.current['windChill']['value']:
			self.windchill = c_to_f(float(str(self.current['windChill']['value'])))
		else:
			self.windchill = ""
		self.hourly = self.city.get_hourly_forecast()
		self.forecast = self.city.get_daily_forecast()
		self.outlook = self.city.get_sevenday_forecast()
		self.alerts = self.city.get_alerts()
		return None
	
	def update_time(self):
		self.updated = datetime.now().strftime('%I:%M %p')
		return None


# almanac-type data object
class Almanac:
	def __init__(self, zip):
		self.city = City(zip)
		self.astro = astral.LocationInfo(self.city.city, self.city.state, self.city.timezone, self.city.lat, self.city.long)
	
	def get_almanac_data(self, date):
		if self.astro:
			self.get_sun_data(date)
			self.get_moon_data(date)
		#TODO get historical averages? meteostat downloads are dead
		return None

	def get_sun_data(self, date):
		if self.astro:
			s = sun(self.astro.observer, date=date, tzinfo=tz.gettz(self.astro.timezone))
			self.sunrise = s['sunrise'].strftime('%I:%M %p')
			self.sunset = s['sunset'].strftime('%I:%M %p')
		return None

	def get_moon_data(self, date):
		if self.astro:
			self.moonrise = moonrise(self.astro.observer, date=date, tzinfo=tz.gettz(self.astro.timezone)).strftime('%I:%M %p')
			self.moonset = moonset(self.astro.observer, date=date, tzinfo=tz.gettz(self.astro.timezone)).strftime('%I:%M %p')
			match round(phase(date=date)):
				case 0:
					self.phase = "New"
				case num if num < 7:
					self.phase = "Waxing Crescent"
				case 7:
					self.phase = "First Quarter"
				case num if num < 14:
					self.phase = "Waxing Gibbous"
				case 14:
					self.phase = "Full"
				case num if num < 21:
					self.phase = "Waning Gibbous"
				case 21:
					self.phase = "Third Quarter"
				case num if num < 28:
					self.phase = "Waning Crescent"
				case 28:
					self.phase = "New"
				case _:
					pass
		return None


class News:
	def __init__(self, url):
		self.url = url
		self.ticker = ""
		self.speed = "300s"

	def build_ticker(self):
		self.feed = feedparser.parse(self.url) 
		if len(self.feed.entries) > 0:
			stories = [ entry.description for entry in self.feed.entries ]
			self.ticker = self.feed.feed.title + ' updated ' + self.feed.feed.updated
			for story in stories:
				self.ticker = self.ticker + ' ... ' + story
			self.speed = str(round(len(self.ticker)/rss_speed_divisor)) + 's'
		return None


def c_to_f(i):
	return round((i * 1.8) + 32)

def m_to_mi(i):
	return round(i / 1609)

def debug_msg(message):
	timestr = time.strftime("%Y%m%d-%H:%M.")
	print(timestr + '.' + prog + "." + ver + "." + message)


####################### initialize
# open a NOAA class to interact with weather data, define the user_agent
n = NOAA(user_agent=noaa_user_agent)

# init classes for homezip data
weather_data = Weather(homezip)
almanac_data = Almanac(homezip)
news_data = News(rss_feed)

# make a playlist
music_files = [f for f in os.listdir('static/audio') if f.endswith('.mp3')]


####################### flask app and routes
# open a flask class for the app
app = Flask(__name__)
app.secret_key = os.urandom(12).hex()
socketio = SocketIO(app)

# set up a thread for regular socket communication
thread = Thread()
thread_stop_event = Event()

def local_weather_updater():
	while not thread_stop_event.is_set():
		# sleep for 15 minutes before updating
		socketio.sleep(900)
		weather_data.get_weather()
		almanac_data.get_almanac_data(datetime.now())
		# re-render the slides and emit that html to clients
		with app.app_context():
			new_slides = render_template('local.j2', **locals())
			socketio.emit('update_slides', {'html': new_slides})

def local_news_updater():
	while not thread_stop_event.is_set():
		socketio.sleep(news_data.speed)
		news_data.build_ticker()
		with app.app_context():
			socketio.emit('update_ticker', {'news': news_data.ticker})

# add the sixhour_time_format function to jinja2 template
@app.template_filter("sixhour_time_format")
def sixhour_time_format(input):
	noaatime_fmt = '%Y-%m-%dT%H:%M:%S%z'
	sixhourtime_fmt = '%^a, %^b %d, %l %p'
	return datetime.strptime(input, noaatime_fmt).strftime(sixhourtime_fmt)

# export global variables to jinja2
@app.context_processor
def variable_adder():
	return {
		'title': title,
		'prog': prog,
		'weather_data': weather_data,
		'almanac_data': almanac_data,
		'news_data': news_data,
		'music': music,
		'music_files': music_files
	}

@app.route('/')
def index():
	random.shuffle(music_files)
	weather_data.get_weather()
	almanac_data.get_almanac_data(datetime.now())
	news_data.build_ticker()

	# create objects with current conditions for all of the extra zips
	#TODO async nationwide weather
	#nationwide_weather_objects = [City(zipcode).get_hourly_forecast()[0] for zipcode in extrazips]

	return render_template('index.j2', **locals())

@socketio.on('connect')
def connect():
	global thread
	print('client connected')
	if not thread.is_alive():
		print('starting thread')
		thread = socketio.start_background_task(local_weather_updater)

@socketio.on('disconnect')
def disconnect():
    print('Client disconnected')

####################### start the webserver
socketio.run(app, debug=True)