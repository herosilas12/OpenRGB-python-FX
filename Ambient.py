import time, os
from PIL import ImageGrab #pip3 install Pillow
from openrgb import OpenRGBClient #pip3 install openrgb-python
from openrgb.utils import RGBColor
 
#//////////////////////////////////////////////////////////////////////////////////////////////////////////
# GLOBAL DEFINES
#//////////////////////////////////////////////////////////////////////////////////////////////////////////
#HEIGHT         = 1920   #now using image.size[1] dynamically
#WIDTH          = 1200   #now using image.size[0] dynamically
LOOP_INTERVAL  = 0.05    # how often we calculate screen colour (in seconds)
DURATION       = 3    # how long it takes bulb to switch colours (in seconds)
DECIMATE       = 10   # skip every DECIMATE number of pixels to speed up calculation

XSCREENCAPTURE  = True # Set to true if on X11, else false
X_RES           = 2560 # Screen pixel in x direction
Y_RES           = 1440 # screen pixel in y direction


client = OpenRGBClient() #will only work if you use default ip/port for OpenRGB server. This is an easy fix, read the documentation if need be https://openrgb-python.readthedocs.io/en/latest/

Dlist = client.devices

if XSCREENCAPTURE:
    # Use X11 display manager for screen capture
    import ctypes
    from PIL import Image
    LibName = 'prtscn.so' # has to be compiled previously from prtscrn.c
    AbsLibPath = os.getcwd() + os.path.sep + LibName # assuming prtscrn.so lives in the same dir
    grab = ctypes.CDLL(AbsLibPath)

    def grab_screen(x1,y1,x2,y2):
        w, h = x2-x1, y2-y1
        size = w * h
        objlength = size * 3

        grab.getScreen.argtypes = []
        result = (ctypes.c_ubyte*objlength)()

        grab.getScreen(x1,y1, w, h, result)
        return Image.frombuffer('RGB', (w, h), result, 'raw', 'RGB', 0, 1)

def SetStatic():
    for Device in Dlist:
        time.sleep(0.1)
        try:
            Device.set_mode('direct')
            print('Set %s successfully'%Device.name)
        except:
            try:
                Device.set_mode('static')
                print('error setting %s\nfalling back to static'%Device.name)
            except:
                print("Critical error! couldn't set %s to static or direct"%Device.name)
SetStatic()

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
 
# run loop
while True:
    #init counters/accumulators
    red   = 0
    green = 0
    blue  = 0
 
    time.sleep(LOOP_INTERVAL) #wake up ever so often and perform this ...
    
    #//////////////////////////////////////////////////////////////////////////////////////////////////////////
    # CALCULATE AVERAGE SCREEN COLOUR
    #//////////////////////////////////////////////////////////////////////////////////////////////////////////
    if XSCREENCAPTURE:
      image = grab_screen(0,0,X_RES,Y_RES)  # take a screenshot usign X
    else:
        image = ImageGrab.grab()    # take a screenshot using PIL
    #print image.size
 
    
    for y in range(0, image.size[1], DECIMATE):  #loop over the height
        for x in range(0, image.size[0], DECIMATE):  #loop over the width
            color = image.getpixel((x, y))  #grab a pixel
            red += color[0]
            green += color[1]
            blue += color[2]
 
 
    red = (( red / ( (image.size[1]/DECIMATE) * (image.size[0]/DECIMATE) ) ) )
    green = ((green / ( (image.size[1]/DECIMATE) * (image.size[0]/DECIMATE) ) ) )
    blue = ((blue / ( (image.size[1]/DECIMATE) * (image.size[0]/DECIMATE) ) ) )
    #print(red, green, blue)
    for Device in Dlist:
        Device.set_color(RGBColor(int(red), int(green), int(blue)))
    time.sleep(0.1)
