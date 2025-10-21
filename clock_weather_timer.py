from metno_locationforecast import Forecast, Place
from datetime import datetime, timezone, timedelta
from time import sleep, localtime, strftime
from inky.auto import auto, InkyWHAT
from PIL import Image, ImageFont, ImageDraw
from matplotlib import font_manager
import pytz
import json
utc=pytz.UTC

what_font_size = 110
phat_font_size = 40

## Inky display setup
try:
    inky_display = auto(ask_user=True, verbose=True)
except TypeError:
    raise TypeError("You need to update the Inky library to >= v1.1.0")

#check for what and set to black mode and larger fontsize
if inky_display.height == 300:
    inky_display = InkyWHAT("black")
    fontsize = what_font_size
else:
     fontsize = phat_font_size

try:
    inky_display.set_border(inky_display.BLACK)
except NotImplementedError:
    pass


## FONT SETUP
font = font_manager.FontProperties(fname="~/usr/share/fonts/truetype/dseg/DSEG7Classic-Bold.ttf")
SEG_file = font_manager.findfont(font)

weather_icons = font_manager.FontProperties(fname="~/usr/share/fonts/truetype/dseg/DSEGWeather.ttf")
icons_file = font_manager.findfont(weather_icons)
icon_dict = {'clearsky':'1', 'cloudy':'2', 'fair':'9', 'fog':'2', 'heavyrain':'4','heavyrainandthunder':'7', 
             'heavyrainshowers':'4', 'heavysleet':'5','heavysleetandthunder':'0', 'heavysleetshowers':'0',
             'heavysnow':'5', 'heavysnowshowers':'5', 'lightrain':'3', 'lightrainandthunder':'6',
             'lightrainshowers':'3', 'lightsleet':'5', 'lightsnow':'5', 'partlycloudy':'9', 'rain':'3',
             'rainandthunder':'6', 'rainshowers':'3', 'sleet':'5', 'snow':'5', 'snowshowers':'5'}

icon_font = ImageFont.truetype(icons_file, int(fontsize*0.75))
text_font = ImageFont.truetype(SEG_file, fontsize)
temp_font = ImageFont.truetype(SEG_file, int(fontsize*0.5))
p_font = ImageFont.truetype(SEG_file, int(fontsize*0.25))

def inky_txt(currtime, temperature, p_min, p_max, icon, display):
        img = Image.new("P", (display.WIDTH, display.HEIGHT),100)
        img.paste(display.BLACK, (0,0,img.size[0],img.size[1]))
        draw = ImageDraw.Draw(img)

        #set the time
        tmp, tmp, w, h = text_font.getbbox(currtime)
        x = (display.WIDTH / 2) - (w/2)
        y = (display.HEIGHT/2)  - (h/2)
        draw.text((x,y), currtime, display.WHITE, text_font)
        
        #set the weather icon
        tmp, tmp, w, h = icon_font.getbbox(icon)
        x = display.WIDTH - (w+15)
        y = display.HEIGHT -(h+6)
        draw.text((x,y), icon, display.WHITE, icon_font)

        #Print the temperature
        tmp, tmp, w, h = temp_font.getbbox(temperature)
        x = 0 + 10
        y = display.HEIGHT-(h+6)
        draw.text((x,y), temperature, display.WHITE, temp_font)
        
        precipitation = f"{p_min:.1f}-{p_max:.1f}"
        tmp, tmp, w, h = p_font.getbbox(precipitation)
        y = display.HEIGHT-(h+6)
        x = 180    
        draw.text((x,y), precipitation, display.WHITE, p_font)
        
        
        display.set_image(img)
        display.show()
        print(currtime)

## WEATHER ##
def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

home = Place("Heggedal", 59.78, 10.44, 112)
ua = "rpi_inky_weather_app https://github.com/martingim/pimoroni_inky"
home_forecast = Forecast(home, ua, forecast_type="complete")

try:
    home_forecast.load()
except:
    home_forecast.update()


icon = 0
old_time = ''
temperature = ''
while True:
    if utc.localize(home_forecast.data.expires)<datetime.now(timezone.utc):
        print("expired, updating forecast")
        home_forecast.update()
    
    interval = home_forecast.data.intervals[0]
    variables = interval.variables
    t = variables["air_temperature"].value
    temperature = f"{t}\u00b0"
    data = json.loads(home_forecast.json_string)
    symbol_code = data['data']['properties']['timeseries'][0]['data']['next_6_hours']['summary']['symbol_code']

    #precipitation next 6 hours
    now = datetime.today()
    now_plus_6_hours = now + timedelta(hours=6)
    precipitation_min = 0
    precipitation_max = 0
    for interval in home_forecast.data.intervals_between(now, now_plus_6_hours):
        precipitation_min += interval.variables["precipitation_amount_min"].value
        precipitation_max += interval.variables["precipitation_amount_max"].value

    
    try:
        icon = icon_dict[symbol_code]
    except:
        icon = ':'        
    currtime = strftime("%H:%M", localtime())
    if currtime!=old_time:
        inky_txt(currtime,temperature, precipitation_min, precipitation_max, icon, inky_display)
    sleep(10)
    old_time=currtime
