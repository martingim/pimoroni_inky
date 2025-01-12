from metno_locationforecast import Forecast, Place
from datetime import datetime, timezone
from time import sleep
from inky import InkyWHAT
from PIL import Image, ImageFont, ImageDraw
from matplotlib import font_manager

display = InkyWHAT("black")
display.set_border(display.BLACK)

#font = font_manager.FontProperties(fname="/home/pi/.fonts/digital7.ttf")
font = font_manager.FontProperties(family="monospace")
file = font_manager.findfont(font)
font = ImageFont.truetype(file, 22)
#print(font_manager.get_fontconfig_fonts())
def draw_forecast(home_forecast):
        img =  Image.new("P", (display.WIDTH, display.HEIGHT), 100)
        img.paste(display.BLACK, (0,0,img.size[0],img.size[1]))
        draw = ImageDraw.Draw(img)
        n_hours = 24
        t = []
        for i in range(n_hours):
                if i<12:
                        x = 10
                        y = 10+24*i
                else:
                        x = 210
                        y = 10+24*(i-12)
                interval = home_forecast.data.intervals[i]
                variables = interval.variables
                t = variables["air_temperature"].value
                msg = f"{utc_to_local(interval.start_time).hour:02}:{round(t)}\u00b0"
                if variables['precipitation_amount_max']>0.001:
                        msg = f"{msg} {variables['precipitation_amount_min'].value}-{variables['precipitation_amount_max'].va>

                draw.text((x, y), msg, display.WHITE, font)
        display.set_image(img)
        display.show()


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

home = Place("Heggedal", 59.78, 10.44, 112)
ua = "rpi_inky_weather_app https://github.com/martingim/pimoroni_inky"
home_forecast = Forecast(home, ua, forecast_type="complete")
try:
        home_forecast.load()
except:
        home_forecast.update()
draw_forecast(home_forecast)
#print(home_forecast.data.intervals[0].variables["air_temperature"].value)
#print(utc_to_local(home_forecast.data.expires))


while True:
        if home_forecast.data.expires<datetime.utcnow():
                print("expired, updating forecast")
                home_forecast.update()
                draw_forecast(home_forecast)
        else:
                print("not expired")
                print(home_forecast.data.expires)
                print(datetime.utcnow())
        sleep(60*5)


