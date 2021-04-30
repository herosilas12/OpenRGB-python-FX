import time, os
from PIL import ImageGrab #pip3 install Pillow
from openrgb import OpenRGBClient #pip3 install openrgb-python
from openrgb.utils import RGBColor
from sklearn.cluster import KMeans
from collections import Counter
import numpy as np

#//////////////////////////////////////////////////////////////////////////////////////////////////////////
# GLOBAL DEFINES
#//////////////////////////////////////////////////////////////////////////////////////////////////////////
#HEIGHT         = 1920   #now using image.size[1] dynamically
#WIDTH          = 1200   #now using image.size[0] dynamically
LOOP_INTERVAL  = 0.05    # how often we calculate screen colour (in seconds)
DURATION       = 3       # how long it takes bulb to switch colours (in seconds)
DECIMATE       = 100     # sample only 1% of pixels to speed up
K_MEANS        = 3       # number of clusters to calculate (returns average color if 1 and dominant color if >1)

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
 
# init K-Means model
clt = KMeans(n_clusters = 3, n_init=3, max_iter=200)

# init vars for colors before current
old2 = np.zeros(3)
old = np.zeros(3)

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
 
    data = []
    for y in range(0, image.size[1], DECIMATE):  #loop over the height
        for x in range(0, image.size[0], DECIMATE):  #loop over the width
            color = image.getpixel((x, y))  #grab a pixel
            data.append(color)
 
    #cluster and assign labels to the pixels 
    labels = clt.fit_predict(data)
    #count labels to find most popular
    label_counts = Counter(labels)
    #subset out most popular centroid
    dominant_color = clt.cluster_centers_[label_counts.most_common()[0][0]]
    
    # current color is blended with colors 2 frames before to smooth effect
    dominant_color += (old + 0.5*old2)
    dominant_color /= 2.5
    # reset vars for next iteration
    old = dominant_color
    old2 = old

    red, green, blue = dominant_color
    #print(red, green, blue)
    for Device in Dlist:
        Device.set_color(RGBColor(int(red), int(green), int(blue)))
    time.sleep(0.1)
