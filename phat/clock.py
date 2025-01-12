from time import sleep, localtime, strftime
from inky.auto import auto
from PIL import Image, ImageFont, ImageDraw
from matplotlib import font_manager

def inky_txt(msg, display, font):
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


# Set up the Inky display
try:
    inky_display = auto(ask_user=True, verbose=True)
except TypeError:
    raise TypeError("You need to update the Inky library to >= v1.1.0")

try:
    inky_display.set_border(inky_display.BLACK)
except NotImplementedError:
    pass

font = font_manager.FontProperties(fname="~/usr/share/fonts/truetype/dseg/DSEG7Classic-Bold.ttf")
file = font_manager.findfont(font)
font = ImageFont.truetype(file, 40)

while True:
    msg = strftime("%H:%M", localtime())
    inky_txt(msg, inky_display, font)
    sleep(10)


