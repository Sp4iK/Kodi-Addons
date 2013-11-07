# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with XBMC; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *


import os, sys
import urllib, re
from xml.dom import minidom
import xml.etree.ElementTree as ET
import xbmcgui, xbmcaddon
from time import strftime, strptime


__addon__      = xbmcaddon.Addon()
__cwd__        = __addon__.getAddonInfo('path')
__scriptname__ = __addon__.getAddonInfo('name')
__version__    = __addon__.getAddonInfo('version')
__author__     = __addon__.getAddonInfo('author')
__language__   = __addon__.getLocalizedString

__profile__    = xbmc.translatePath( __addon__.getAddonInfo('profile') ).decode("utf-8")
__resource__   = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) ).decode("utf-8")

sys.path.append (__resource__)

from utilities import *

NUMBER_OF_DAYS = 7
SEARCH_URL     = "http://www.aemet.es/es/buscador?modo=and&orden=n&tipo=sta&str=%s"
LOCATION_URL   = "http://www.aemet.es/xml/municipios/localidad_%s.xml"

WEATHER_WINDOW = xbmcgui.Window( 12600 )

def set_property(property, value):
  WEATHER_WINDOW.setProperty(property, value)

def clear_properties():
    log("clear_properties")
    set_property("Current.Condition"       , "")
    set_property("Current.Temperature"     , "")
    set_property("Current.Wind"            , "")
    set_property("Current.Humidity"        , "")
    set_property("Current.winddirection"   , "")
    set_property("Current.OutlookIcon"     , "")
    set_property("Current.FanartCode"      , "")
    set_property("Current.FeelsLike"       , "")
    set_property("Current.DewPoint"        , "")
    set_property("Current.UVIndex"         , "")
    
    for i in range(4):
      set_property("Day%i.Title"       % i , "")
      set_property("Day%i.HighTemp"    % i , "")
      set_property("Day%i.LowTemp"     % i , "")
      set_property("Day%i.Outlook"     % i , "")
      set_property("Day%i.OutlookIcon" % i , "")
      set_property("Day%i.FanartCode"  % i , "")

def refresh_locations():
  log("refresh_locations")
  location_set1 = __addon__.getSetting( "Location1" )
  location_set2 = __addon__.getSetting( "Location2" )
  location_set3 = __addon__.getSetting( "Location3" )
  locations = 0
  
  if location_set1 != "":
    locations += 1
    set_property('Location1'   , location_set1) # set location 1, XBMC needs this
  else:
    set_property('Location1'   , "")  
  if location_set2 != "":
    locations += 1 
    set_property('Location2'   , location_set2) # set location 2, XBMC needs this
  else:
    set_property('Location2'   , "")
  if location_set3 != "":
    locations += 1
    set_property('Location3'   , location_set3) # set location 3, XBMC needs this
  else:
    set_property('Location3'   , "")

  set_property('Locations',str(locations))      # set total number of locations, XBMC needs this

def fetch(url):
  log("fetch data from 'aemet.es'")
  socket = urllib.urlopen( url )
  result = socket.read()
  socket.close()
  return result

def get_elements(xml, tag):
   return xml.getElementsByTagName(tag)[0].firstChild.wholeText

def get_fraction():					# Calculates the quarter of day based on actual time
	hour = int(strftime('%H'))
	dayfraction = 0
	
	if hour >= 0 and hour < 6:
		dayfraction = 0
	elif hour >= 6 and hour < 12:
		dayfraction = 1
	elif hour >= 12 and hour < 18:
		dayfraction = 2
	elif hour >= 18 and hour < 24:
		dayfraction = 3
		
	return dayfraction

def location(string):
  log("search for '%s'" % (string,))
  locs = []
  ids = []
  query = fetch( SEARCH_URL % (string))
  locations = re.compile('<a href="/es/eltiempo/prediccion/municipios/([A-Za-z-]+)-id([0-9]+)">',re.DOTALL).findall(query)
  for location, id in locations:
      locs.append(location.replace("-", " ").title())
      ids.append(id)
  return locs, ids

def forecast(city):
  log("get forecast for '%s'" % (city,))
  data = fetch(LOCATION_URL % (city))
  root = ET.fromstring(data)
  current = root.find("./prediccion/dia")
  fraction = get_fraction()
  iconpath = xbmc.translatePath(os.path.join( __cwd__, 'resources', 'images', 'new' )).decode("utf-8")
  
  ## Get current weather info from xml
  temp = current.findall("./temperatura/dato")[fraction].text
  humidity = current.findall("./humedad_relativa/dato")[fraction].text
  wind = current.findall("./viento/velocidad")[fraction+3].text
  if current.findall("./viento/direccion")[fraction+3].text == "C":
	winddir = "-"
  else:
	winddir = current.findall("./viento/direccion")[fraction+3].text
  precip = current.findall("./prob_precipitacion")[fraction+3].text
  code = current.findall("./estado_cielo")[fraction+3].text
  desc = str(current.findall("./estado_cielo")[fraction+3].attrib.get("descripcion"))
  uv = current.find("./uv_max").text
  
  set_property("Current.Location"        , root.find("nombre").text)
  set_property("Forecast.State"          , root.find("provincia").text)
  set_property("Current.Condition"       , desc)                                    # current condition in words
  set_property("Current.Temperature"     , temp)                                 	# temp in C, no need to set F, XBMC will convert it
  set_property("Current.Wind"            , wind)                                    # wind speed in Km/h, no need for mph as XBMC will do the conversion
  set_property("Current.Humidity"        , humidity)                                # Humidity in %
  set_property("Current.winddirection"   , winddir)  								# wind direction
  set_property("Current.FeelsLike"       , getFeelsLike(int(temp), int(wind)))   	# Feels like
  set_property("Current.DewPoint"        , getDewPoint(int(temp), int(humidity)))	# Dew Point
  set_property("Current.UVIndex"         , uv)										# UV index
  set_property("Current.Precipitation"	 , precip)									# Precipitation probability in %
  set_property("Current.OutlookIcon"	 , iconpath + "/%s.png" % code)
# set_property("Current.OutlookIcon"     , "%s.png" % WEATHER_CODES[code])          # condition icon, utilities.py has more on this
# set_property("Current.FanartCode"      , WEATHER_CODES[code])                     # fanart icon, utilities.py has more on this

  ## Get forecast info
  weather = root.findall("./prediccion/dia")
  weather.pop(0)
  i = 0
  for day in weather:
    code = day.find("./estado_cielo").text
    date = strptime(day.attrib.get("fecha"), '%Y-%m-%d')
    set_property("Day%i.Title"       % i , DAYS[int(strftime('%w', date))])       # Day of the week
    set_property("Day%i.HighTemp"    % i , day.find("./temperatura/maxima").text)   # Max Temp for that day, C only XBMC will do the conversion
    set_property("Day%i.LowTemp"     % i , day.find("./temperatura/minima").text)   # Min temperature for that day, C only XBMC will do the conversion
    set_property("Day%i.Outlook"     % i , str(day.find("./estado_cielo").get("descripcion")))  # days condition in words 
    set_property("Daily.%i.ChancePrecipitation"	% i , day.find("./prob_precipitacion").text)	# Precipitation probability in %
    set_property("Day%i.OutlookIcon" % i , iconpath + "/%s.png" % code)
    #set_property("Day%i.OutlookIcon" % i , "%s.png" % WEATHER_CODES[code])          # condition icon, utilities.py has more on this
    #set_property("Day%i.FanartCode"  % i , WEATHER_CODES[code])                     # fanart icon, utilities.py has more on this
    i += 1
 
if sys.argv[1].startswith("Location"):                                              # call from addon settings to set the location                                       
  kb = xbmc.Keyboard("", xbmc.getLocalizedString(14024), False)                     #           (Location1, Location2 or Location3)
  kb.doModal()
  if (kb.isConfirmed() and kb.getText() != ""):
    text = kb.getText()
    locations, ids = location(text)
    dialog = xbmcgui.Dialog()
    ret = dialog.select(xbmc.getLocalizedString(396), locations)
    if ret > -1:
      __addon__.setSetting( sys.argv[1], locations[ret] )
      __addon__.setSetting( sys.argv[1] + 'id', ids[ret] )
      log("addon setting - [%s] set to value [%s]" % (sys.argv[1], locations[ret],))
    
elif sys.argv[1] == "1" or sys.argv[1] == "2" or sys.argv[1] == "3":               # call from XBMC to collect data
                                                                                   #         for location 1, 2 or 3 
  location = __addon__.getSetting( "Location%s" % sys.argv[1])
  id = __addon__.getSetting( "Location%sid" % sys.argv[1])
  if location != "":
    log("addon called by XBMC for location '%s'" % (location,))
    forecast(id)
  else:
    clear_properties()   

refresh_locations()
set_property("WeatherProvider", "aemet.es")                          # set name of the provider, this will be visible in the Weather page



