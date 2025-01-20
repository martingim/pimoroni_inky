from metno_locationforecast import Forecast, Place
from datetime import datetime, timezone
from time import sleep, localtime, strftime
from inky.auto import auto, InkyWHAT
from PIL import Image, ImageFont, ImageDraw
from matplotlib import font_manager
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

ICONS_font = ImageFont.truetype(icons_file, int(fontsize*0.75))
SEG_font = ImageFont.truetype(SEG_file, fontsize)


def inky_txt(currtime, temperature, icon, display, text_font, icon_font):
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
temperature = '-10.0'
while True:
    if home_forecast.data.expires<datetime.now(timezone.utc):
        print("expired, updating forecast")
        home_forecast.update()
    currtime = strftime("%H:%M", localtime())
    if currtime!=old_time:
        inky_txt(currtime,temperature, str(icon), inky_display, SEG_font, ICONS_font)
    sleep(10)
    old_time=currtime
    icon += 1