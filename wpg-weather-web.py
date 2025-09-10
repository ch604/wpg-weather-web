# Retro Winnipeg Weather Channel
# Original By probnot
# Updated/modified for USA by TechSavvvvy
# Updated for web by ch604

import json, os, random, time
from datetime import datetime
from dateutil import tz
from threading import Thread, Event
from typing import Any, Callable

# for rss feed and generic api access
import feedparser, requests

# for weather data
from noaa_sdk import NOAA

# for location data
import zipcodes

# for almanac data
import astral
from astral.sun import sun
from astral.moon import moonrise, moonset, phase

# for serving sites and making websocket
from flask import Flask, render_template, request
from flask_socketio import SocketIO

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
  def __init__(self, zip: str) -> None:
    z = ZipData(zip)
    self.zip = zip
    self.city = z.city
    self.state = z.state
    self.location = self.city + ", " + self.state
    self.lat = float(z.zipdata['lat'])
    self.long = float(z.zipdata['long'])
    self.timezone = z.zipdata['timezone']
    self.pointProperties = n.points(z.get_latlong_str())['properties']
    self.adjacent_counties = z.get_adj_counties()
    self.fips = str(z.get_fips())

  def get_current_conditions(self):
    # returns a json array of the current observations by the closest station to the stored zip
    if self.zip:
      for i in n.get_observations_by_lat_lon(self.lat, self.long):
        return i
    return None

  def get_daily_forecast(self):
    # returns a json array of 14 day/night forecasts (7 days)
    if self.zip:
      return n.get_forecasts(self.zip, 'US', type='forecast')
    return None

  def get_sevenday_forecast(self) -> list[Any] | None:
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
  def __init__(self, zip: str) -> None:
    if zipcodes.is_real(zip):
      self.zipdata = zipcodes.matching(zip)[0]
      self.state = self.zipdata['state'].upper()
      self.city = self.zipdata['city'].upper()

  def get_latlong_str(self) -> (str | None):
    if self.zipdata:
      return self.zipdata['lat'] + "," + self.zipdata['long']
    return None

  def get_fips(self) -> (str | None):
    """Return FIPS codes for county containing zip"""
    if self.zipdata:
      co = remove_county_suffix(self.zipdata['county'], self.zipdata['state'])
      for i in json.load(open('county_adjacency_by_fips.json')):
        if i['county'] == co and i['state'] == self.zipdata['state']:
          return i['fips']
    return None


  def get_adj_counties(self) -> (list[str] | None):
    """Return FIPS codes for adjacent counties (plus own county)"""
    if self.zipdata:
      co = remove_county_suffix(self.zipdata['county'], self.zipdata['state'])
      for i in json.load(open('county_adjacency_by_fips.json')):
        if i['county'] == co and i['state'] == self.zipdata['state']:
          return i['adj']
    return None


# object to store weather data arrays
class Weather:
  def __init__(self, zip: str) -> None:
    self.city = City(zip)
    self.radarimg = self.city.get_radar_url()

  def get_weather(self) -> None:
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
    self.get_alerts()
    return None

  def get_alerts(self) -> None:
    self.alerts = self.city.get_alerts()

  def get_records(self) -> None:
    self.acis = ACIS(self.city.fips)
    self.acis.get_all_records(datetime.now())

  def update_time(self) -> None:
    self.updated = datetime.now().strftime('%I:%M %p')
    self.forecast_date = datetime.now().strftime('%a, %b %d').upper()


# almanac-type data object
class Almanac:
  def __init__(self, zip: str) -> None:
    self.city = City(zip)
    self.astro = astral.LocationInfo(self.city.city, self.city.state, self.city.timezone, self.city.lat, self.city.long)
    self.tz = tz.gettz(self.astro.timezone)

  def get_almanac_data(self, date: datetime) -> None:
    if self.astro:
      self.get_sun_data(date)
      self.get_moon_data(date)

  def get_sun_data(self, date: datetime) -> None:
    if self.astro:
      s = sun(self.astro.observer, date, tzinfo=self.tz)
      # account for possibility of no sunrise/set in some areas
      try:
        self.sunrise = s['sunrise'].strftime('%I:%M %p')
      except:
        self.sunrise = "N/A"
      try:
        self.sunset = s['sunset'].strftime('%I:%M %p')
      except:
        self.sunset = "N/A"

  def get_moon_data(self, date: datetime) -> None:
    if self.astro:
      # account for possibility of no moonrise/set on some days
      try:
        assert isinstance(moonrise, datetime)
        self.moonrise = moonrise(self.astro.observer, date=date, tzinfo=self.tz).strftime('%I:%M %p')
      except:
        self.moonrise = "N/A"
      try:
        assert isinstance(moonset, datetime)
        self.moonset = moonset(self.astro.observer, date=date, tzinfo=self.tz).strftime('%I:%M %p')
      except:
        self.moonset = "N/A"
      match round(phase(date)):
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


class ACIS:
  """pull data from ACIS api"""
  def __init__(self, fips: str) -> None:
    self.url = "https://data.rcc-acis.org/"
    self.headers = {'Content-Type': 'application/json'}
    self.fips = fips

  def call_api(self, date: datetime, stat: str, best: bool) -> None:
    """Get the daily record 'stat' for the last 50 years from 'date' from all stations in the county 'self.fips'"""
    # stat is the endpoint to hit, like pcpn or maxt
    # best is the reduce target, true being max and false being min
    # eg: j.call_api("01101", datetime.now(), "snow", True)
    #     will set j.daily_snow and j.daily_snow_date
    operator: Callable[[float, float], bool] = lambda x, y: x > y  # Use greater than for max
    reduce = "max"
    if not best:
      operator = lambda x, y: x < y  # Use less than for min
      reduce = "min"
    yday_idx = date.timetuple().tm_yday - 1
    body = '{"county": "' + self.fips + '", "sdate": "' + str(date.year - 50) + '-01-01", "edate": "' + str(date.year) + '-12-31", "elems": [{"name": "' + stat + '", "interval": "dly", "duration": 1, "smry": {"add": "date", "reduce": "' + reduce + '"}, "smry_only": "1", "groupby": "year"}]}'
    try:
      f = requests.post(self.url + "MultiStnData", headers=self.headers, data=body)
      if not f.ok or "error" in json.loads(f.content):
        return None
      for d in json.loads(f.content)['data']:
        if not getattr(self, "daily_" + stat, False) or operator(float(d['smry'][0][yday_idx][0]), getattr(self, "daily_" + stat)):
          setattr(self, "daily_" + stat, float(d['smry'][0][yday_idx][0]))
          setattr(self, "daily_" + stat + "_date", d['smry'][0][yday_idx][1].split('-')[0])
      if not getattr(self, "daily_" + stat, False):
        # we didnt get any values from the data, set N/A
        setattr(self, "daily_" + stat, "N/A")
        setattr(self, "daily_" + stat + "_date", "N/A")
        return None
    except:
      return None

  def get_all_records(self, date: datetime) -> None:
    self.get_daily_maxt(date)
    self.get_daily_mint(date)
    self.get_daily_pcpn(date)
    self.get_daily_snow(date)
    return None

  def get_daily_maxt(self, date: datetime) -> None:
    """Record High Temp"""
    self.call_api(date, "maxt", True)
    if getattr(self, "daily_maxt", False) and type(self.daily_maxt) == float:
      self.daily_maxt = int(round(self.daily_maxt))
    return None

  def get_daily_mint(self, date: datetime) -> None:
    """Record Low Temp"""
    self.call_api(date, "mint", False)
    if getattr(self, "daily_mint", False) and type(self.daily_mint) == float:
      self.daily_mint = int(round(self.daily_mint))
    return None

  def get_daily_pcpn(self, date: datetime) -> None:
    """Record Rainfall"""
    self.call_api(date, "pcpn", True)
    return None

  def get_daily_snow(self, date: datetime) -> None:
    """Record Snowfall"""
    self.call_api(date, "snow", True)
    return None


class News:
  def __init__(self, url: str) -> None:
    self.url = url
    self.ticker = ""
    self.speed = 300

  def build_ticker(self) -> None:
    self.feed = feedparser.parse(self.url)
    if len(self.feed.entries) > 0:
      stories = [ entry.description for entry in self.feed.entries ]
      self.ticker = self.feed.feed.title + ' updated ' + self.feed.feed.updated
      for story in stories:
        self.ticker = self.ticker + ' ... ' + story
      self.speed = round(len(self.ticker)/rss_speed_divisor)
    return None


def c_to_f(i: float) -> str:
  return str(round((i * 1.8) + 32))

def m_to_mi(i: float) -> str:
  return str(round(i / 1609))

def debug_msg(message: str) -> None:
  timestr = time.strftime("%Y%m%d-%H:%M.")
  print(timestr + '.' + prog + "." + ver + "." + message)
  return None

def remove_county_suffix(full_name: str, state: str) -> str:
  """Turn 'Name County/Municipality/Borough' to 'Name'"""
  # dont remove 'city' from VA independent cities
  match state:
    case "AK":
      return ( full_name.replace(" City and Borough","")
       .replace(" Census Area","")
       .replace(" Municipality","")
       .replace(" Borough","")
      )
    case "LA":
      return full_name.replace(" Parish","")
    case "PR":
      return full_name.replace(" Municipio","")
    case "AS":
      return full_name.replace(" District","")
    case "MP":
      return full_name.replace(" Municipality","")
    case "VI":
      return full_name.replace(" Island","")
    case _:
      return full_name.replace(" County","")


####################### initialize
# open a NOAA class to interact with weather data, define the user_agent
n = NOAA(user_agent=noaa_user_agent)

# init classes for homezip data
weather_data = Weather(homezip)
almanac_data = Almanac(homezip)
news_data = News(rss_feed)

# make a playlist
music_files = [f for f in os.listdir('static/audio') if f.endswith('.mp3')]
# enum loading screens
loading_screens = [f for f in os.listdir('static/img') if f.endswith(('.png', '.jpg', '.gif'))]


####################### flask app setup
# open a flask class for the app
app = Flask(__name__)
app.secret_key = os.urandom(12).hex()
socketio = SocketIO(app)

# set up a thread for regular socket communication
thread_weather = Thread()
thread_news = Thread()
thread_stop_event = Event()

# track client connections
clients = set()

####################### threaded functions
def local_weather_updater():
  while not thread_stop_event.is_set():
    # sleep for 15 minutes before updating
    socketio.sleep(900)
    weather_data.get_weather()
    weather_data.get_records()
    almanac_data.get_almanac_data(datetime.now())
    # re-render the slides and emit that html to clients
    with app.app_context():
      new_slides = render_template('local.j2', **locals())
      socketio.emit('update_slides', {'html': new_slides})

def local_news_updater():
  while not thread_stop_event.is_set():
    # sleep until the news ticker should have completely moved across the screen
    socketio.sleep(news_data.speed)
    news_data.build_ticker()
    with app.app_context():
      socketio.emit('update_ticker', {'news': news_data.ticker})

####################### routes
# add the sixhour_time_format function to jinja2 template
@app.template_filter("sixhour_time_format")
def sixhour_time_format(input: str) -> str:
  noaatime_fmt = '%Y-%m-%dT%H:%M:%S%z'
  sixhourtime_fmt = '%^a, %^b %d, %l %p'
  return datetime.strptime(input, noaatime_fmt).strftime(sixhourtime_fmt)

# export global variables to jinja2
@app.context_processor
def variable_adder() -> dict[str, Any] :
  return {
   'title': title,
   'prog': prog,
   'weather_data': weather_data,
   'almanac_data': almanac_data,
   'news_data': news_data,
   'music': music,
   'music_files': music_files,
   'loading_screens': loading_screens
  }

# main page
@app.route('/')
def loading() -> str:
  return render_template('loading.j2', **locals())

@app.route('/weather')
def weather() -> str:
  random.shuffle(music_files)
  weather_data.get_weather()
  weather_data.get_records()
  almanac_data.get_almanac_data(datetime.now())
  news_data.build_ticker()

  # create objects with current conditions for all of the extra zips
  #TODO async nationwide weather
  #nationwide_weather_objects = [City(zipcode).get_hourly_forecast()[0] for zipcode in extrazips]

  return render_template('weather.j2', **locals())

# socket listeners
@socketio.on('connect')
def connect() -> None:
  global thread_weather
  global thread_news
  debug_msg(f"client {request.sid} connected")
  clients.add(request.sid)
  if not thread_weather.is_alive():
    debug_msg('starting weather thread')
    thread_weather = socketio.start_background_task(local_weather_updater)
  if not thread_news.is_alive():
    debug_msg('starting news thread')
    thread_news = socketio.start_background_task(local_news_updater)

@socketio.on('disconnect')
def disconnect() -> None:
  debug_msg(f"Client {request.sid} disconnected")
  clients.discard(request.sid)
  if not clients:
    debug_msg('No clients remaining, stopping threads')
    thread_stop_event.set()

####################### start the webserver
socketio.run(app, debug=True)
