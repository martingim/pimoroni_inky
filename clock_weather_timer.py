from metno_locationforecast import Forecast, Place
from gpiozero import Button
from RPi import GPIO    
from signal import pause
from threading import Thread
from datetime import datetime, timezone, timedelta
from time import sleep, localtime, strftime, gmtime, time
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
uv_font = ImageFont.truetype(icons_file, int(fontsize*0.5))
rem_time_font = ImageFont.truetype(SEG_file, int(fontsize*0.25))
#weather text
def inky_txt(currtime, temperature, precipitation, icon, uv_symbol, display):
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

        #precipitation
        tmp, tmp, w, h = p_font.getbbox(precipitation)
        y = display.HEIGHT-(h+6)
        x = 160    
        draw.text((x,y), precipitation, display.WHITE, p_font)

        #UV
        tmp, tmp, w, h = uv_font.getbbox(uv_symbol)
        y = 6
        x = 350
        draw.text((x,y), uv_symbol, display.WHITE, uv_font)

        if remaining_time>0:
            msg = strftime("%H:%M", gmtime(remaining_time))
            tmp, tmp, w, h = rem_time_font.getbbox(msg)
            y = 6
            x = 6
            draw.text((x,y), msg, display.WHITE, rem_time_font)
            
        
        display.set_image(img)
        display.show()
        print(currtime)

#timer time
def txtwhat(msg, display, font):
        img = Image.new("P", (display.WIDTH, display.HEIGHT),100)
        img.paste(display.BLACK, (0,0,img.size[0],img.size[1]))
        draw = ImageDraw.Draw(img)

        w, h = font.getsize(msg)
        x = (display.WIDTH / 2) - (w/2)
        y = (display.HEIGHT/2)  - (h/2)
        draw.text((x,y), msg, display.WHITE, font)
        display.set_image(img)
        display.show()
        print(msg)

def ylwtxtwhat(msg, font):
        display = InkyWHAT("yellow")
        display.set_border(display.BLACK)
        img = Image.new("P", (display.WIDTH, display.HEIGHT),100)
        img.paste(display.BLACK, (0,0,img.size[0],img.size[1]))

        draw = ImageDraw.Draw(img)


        w, h = font.getsize(msg)
        x = (display.WIDTH / 2) - (w/2)
        y = (display.HEIGHT/2)  - (h/2)
        draw.text((x,y), msg, display.YELLOW, font)
        display.set_image(img)
        display.show()
        print(msg, " Paused")

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

def weather_report(old_time):
    icon = 0
    temperature = ''

    
    if utc.localize(home_forecast.data.expires)<datetime.now(timezone.utc):
        print("expired, updating forecast")
        home_forecast.update()
    
    interval = home_forecast.data.intervals[0]
    variables = interval.variables
    t = variables["air_temperature"].value
    temperature = f"{t}\u00b0"
    data = json.loads(home_forecast.json_string)
    symbol_code = data['data']['properties']['timeseries'][0]['data']['next_6_hours']['summary']['symbol_code']

    #precipitation and uv next 6 hours
    now = datetime.today()
    now_plus_6_hours = now + timedelta(hours=6)
    precipitation_min = 0
    precipitation_max = 0
    uv_max = 0
    for interval in home_forecast.data.intervals_between(now, now_plus_6_hours):
        precipitation_min += interval.variables["precipitation_amount_min"].value
        precipitation_max += interval.variables["precipitation_amount_max"].value
        uv_max = max(uv_max, interval.variables["ultraviolet_index_clear_sky"].value)    
    if precipitation_max > 0:
        precipitation = f"{precipitation_min:.1f}-{precipitation_max:.1f}"
    else:
        precipitation = ""
        
    if uv_max > 2.9:
        uv_symbol = '1'
    else:
        uv_symbol = ':'
        
    try:
        icon = icon_dict[symbol_code]
    except:
        icon = ':'        
    currtime = strftime("%H:%M", localtime())
    if currtime!=old_time:
        inky_txt(currtime,temperature, precipitation, icon, uv_symbol, inky_display)
    old_time=currtime
    return old_time


################# work timer ###########################
def run_timer():
        global work_time
        global remaining_time
        global endtime
        global Running
        global Paused
        display = InkyWHAT("black")
        display.set_border(display.BLACK)

        font = font_manager.FontProperties(fname="~/usr/share/fonts/truetype/dseg/DSEG7Classic-Bold.ttf")
        file = font_manager.findfont(font)
        font = ImageFont.truetype(file, 110)
        endtime = time() + work_time
        remaining_time = work_time
        while True:
                old_time = ''
                while Paused:
                    old_time = weather_report(old_time)
                    sleep(1)
                
                message = strftime("%H:%M", gmtime(remaining_time))
                while not Paused:
                    if remaining_time>59:
                        txtwhat(message, display, font)
                        #Check if it is time to update the display
                        remaining_time = endtime - time()
                        newtime = strftime("%H:%M", gmtime(remaining_time))
                        tmp_r_t =  remaining_time
                        while newtime == message:
                                tmp_r_t = endtime - time()
                                sleep(1)
                                newtime = strftime("%H:%M", gmtime(tmp_r_t))
                                #check if remaining time has changed while running
                                if message != strftime("%H:%M", gmtime(remaining_time)):
                                        newtime = strftime("%H:%M", gmtime(remaining_time))
                                        remaining_time = endtime - time()
                                        break
                        #update the message
                        message = newtime
                        remaining_time = endtime - time()
                    else:
                        ylwtxtwhat(strftime("%H:%M", gmtime(0)), font)
                        while not Paused:
                            sleep(1)
                        
                                    
                    
                # message = strftime("%H:%M", gmtime(0))
                # #ylwtxtwhat(message, font)
                # Running = False
                # with open('times_worked.txt', 'a') as f:
                #         f.write(strftime("%d.%m.%y: ", localtime()) + str(work_time) + "\n")
                # work_time = 0
                # while work_time == 0:
                #         sleep(10)


def Pause():
        #Pause the timer
        global Paused
        Paused = True
        print("paused\n")

def unPause():
        #unpause the timer
        global Paused
        Paused = False
        print("unpaused\n")

def add_10_min():
        global work_time
        global remaining_time
        global endtime
        work_time += 10*60
        remaining_time += 10*60
        endtime += 10*60
        print("added 10 min")

def sub_10_min():
        global work_time
        global remaining_time
        global endtime
        work_time -= min(10*60, remaining_time)
        endtime -= min(10*60, remaining_time)    
        remaining_time -= min(10*60, remaining_time)
        print("sub 10 min")

def wait_for_input():
        global Paused
        global Running
        while Running:
                user_input = input("type p for pause u for unpause:\n")
                if user_input == "p":
                        print("PAUSED")
                        Paused = True
                elif user_input == "u":
                        print("UNPAUSED")
                        Paused = False
                else:
                        pass

if __name__ == "__main__":

        #Setup buttons
        buttonfront = Button(12)
        buttonrear = Button(16)
        switch = Button(26)
        #Get work time
        try:
                work_time_H = float(sys.argv[1])
        except:
                work_time_H = 0.5 #work time in hours

        work_time = work_time_H*3600 + 59
        remaining_time = work_time
        #Start Running and check if the switch is on or off
        Paused = not GPIO.input(26)
        Running = True


        t1 = Thread(target=run_timer)
        t2 = Thread(target=wait_for_input)
        t2.daemon = True
        t1.start()
        t2.start()

        switch.when_pressed = Pause
        switch.when_released = unPause
        buttonrear.when_pressed = add_10_min
        buttonfront.when_pressed = sub_10_min
        pause()

