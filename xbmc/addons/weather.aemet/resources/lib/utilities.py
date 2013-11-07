# -*- coding: utf-8 -*- 

import sys
import xbmc
import math

__scriptname__ = sys.modules[ "__main__" ].__scriptname__

DAYS = { 1: xbmc.getLocalizedString( 11 ), 
         2: xbmc.getLocalizedString( 12 ), 
         3: xbmc.getLocalizedString( 13 ), 
         4: xbmc.getLocalizedString( 14 ), 
         5: xbmc.getLocalizedString( 15 ), 
         6: xbmc.getLocalizedString( 16 ), 
         0: xbmc.getLocalizedString( 17 )}
'''        
WEATHER_CODES = { #N/A - Not Available
					0   # Thunderstorms
					1   # Windy Rain
					2   # Windy Rain
					3   # Thunderstorms
					4   # T-Storms
					5   # Rain Snow
					6   # Rain Sleet
					7   # Snow/Rain Icy Mix
					8   # Freezing Drizzle
					9   # Drizzle
					10  # Freezing Rain
					11  # T-Showers / Showers / Light Rain
					12  # Heavy Rain
					13  # Snow Flurries
					14  # Light Snow
					15  # Snowflakes
					16  # Heavy Snow
					17  # Thunderstorms
					18  # Hail
					19  # Dust
					20  # Fog
					21  # Haze
					22  # Smoke
					23  # Windy
					24  # Windy
					25  # Frigid
				'16'  :	'26'  # Cloudy
				'14n' :	'27'  # Mostly Cloudy Night
				'14'  :	'28'  # Mostly Cloudy
				'13n' :	'29'  # Partly Cloudy Night
				'13'  :	'30'  # Partly Cloudy
				'11n' :	'31'  # Clear Night
				'11'  :	'32'  # Sunny
				'12n' :	'33'  # Fair / Mostly Clear Night
				'12'  :	'34'  # Fair / Mostly Sunny
				'17n' :	'33'  # Fair / Mostly Clear Night
				'17'  :	'34'  # Fair / Mostly Sunny
					35  # Thunderstorms
					36  # Hot
					37  # Isolated Thunder
					38  # Scattered T-Storms
				'43'  :	'39'  # Scattered Rain
					40  # Heavy Rain
					41  # Scattered Snow
					42  # Heavy Snow
					43  # Windy/Snowy
					44  # Partly Cloudy Day
				'43n' :	'45'  # Scattered Showers Night
					46  # Snowy Night
					47  # Scattered T-Storms Night 
				}
'''
def log(msg):
  xbmc.log("### [%s] - %s" % (__scriptname__,msg,),level=xbmc.LOGDEBUG ) 
  
  
#### below thanks to FrostBox @ http://forum.xbmc.org/showthread.php?p=937168#post937168  

def getFeelsLike( T=10, V=25 ): 
    """ The formula to calculate the equivalent temperature related to the wind chill is: 
        T(REF) = 13.12 + 0.6215 * T - 11.37 * V**0.16 + 0.3965 * T * V**0.16 
        Or: 
        T(REF): is the equivalent temperature in degrees Celsius 
        V: is the wind speed in km/h measured at 10m height 
        T: is the temperature of the air in degrees Celsius 
        source: http://zpag.tripod.com/Meteo/eolien.htm
        
        getFeelsLike( tCelsius, windspeed )
    """ 
    FeelsLike = T 
    #Wind speeds of 4 mph or less, the wind chill temperature is the same as the actual air temperature. 
    if round( ( V + .0 ) / 1.609344 ) > 4: 
        FeelsLike = ( 13.12 + ( 0.6215 * T ) - ( 11.37 * V**0.16 ) + ( 0.3965 * T * V**0.16 ) ) 
    # 
    return str( round( FeelsLike ) ) 
    
    
def getDewPoint( Tc=0, RH=93, minRH=( 0, 0.075 )[ 0 ] ): 
    """ Dewpoint from relative humidity and temperature 
        If you know the relative humidity and the air temperature, 
        and want to calculate the dewpoint, the formulas are as follows. 
        
        getDewPoint( tCelsius, humidity )
    """ 
    #First, if your air temperature is in degrees Fahrenheit, then you must convert it to degrees Celsius by using the Fahrenheit to Celsius formula. 
    # Tc = 5.0 / 9.0 * ( Tf - 32.0 ) 
    #The next step is to obtain the saturation vapor pressure(Es) using this formula as before when air temperature is known. 
    Es = 6.11 * 10.0**( 7.5 * Tc / ( 237.7 + Tc ) ) 
    #The next step is to use the saturation vapor pressure and the relative humidity to compute the actual vapor pressure(E) of the air. This can be done with the following formula. 
    #RH=relative humidity of air expressed as a percent. or except minimum(.075) humidity to abort error with math.log. 
    RH = RH or minRH #0.075 
    E = ( RH * Es ) / 100 
    #Note: math.log( ) means to take the natural log of the variable in the parentheses 
    #Now you are ready to use the following formula to obtain the dewpoint temperature. 
    try: 
        DewPoint = ( -430.22 + 237.7 * math.log( E ) ) / ( -math.log( E ) + 19.08 ) 
    except ValueError: 
        #math domain error, because RH = 0% 
        #return "N/A" 
        DewPoint = 0 #minRH 
    #Note: Due to the rounding of decimal places, your answer may be slightly different from the above answer, but it should be within two degrees. 
    return str( int( DewPoint ) )  
  