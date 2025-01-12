import sys
from gpiozero import Button
from RPi import GPIO    
from signal import pause
from threading import Thread
from time import sleep, localtime, strftime, gmtime, time
from inky import InkyWHAT
from PIL import Image, ImageFont, ImageDraw
from matplotlib import font_manager
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


def run_timer():
        global work_time
        global remaining_time
        global endtime
        global Running
        global Paused
        while True:
                message = strftime("%H:%M", gmtime(work_time))
                display = InkyWHAT("black")
                display.set_border(display.BLACK)

                font = font_manager.FontProperties(fname="/home/pi/.fonts/digital7.ttf")
                file = font_manager.findfont(font)
                font = ImageFont.truetype(file, 195)

                endtime = time() + work_time
                remaining_time = work_time
                while remaining_time>0:
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
                                        break
                                if Paused:
                                        ylwtxtwhat(message, font)
                                        while Paused:
                                                sleep(1)
                                                #if time is added while paused
                                                if message != strftime("%H:%M", gmtime(remaining_time)):
                                                        newtime = strftime("%H:%M", gmtime(remaining_time))
                                                        break
                                        endtime = remaining_time + time()
                        #update the message
                        message = newtime
                        remaining_time = endtime - time()
                message = strftime("%H:%M", gmtime(0))
                ylwtxtwhat(message, font)
                Running = False
                with open('times_worked.txt', 'a') as f:
                        f.write(strftime("%d.%m.%y: ", localtime()) + str(work_time) + "\n")
                work_time = 0
                while work_time == 0:
                        sleep(10)


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
        work_time -= 10*60
        remaining_time -= 10*60
        endtime -= 10*60
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


