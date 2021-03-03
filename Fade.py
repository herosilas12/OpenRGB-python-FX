import openrgb, time, sys, threading
from statistics import mean
from openrgb.utils import RGBColor, ModeData, DeviceType, ZoneType

client = openrgb.OpenRGBClient()

Dlist = client.devices

DEBUG = False

def UserInput():
    Color1 = Color2 = Colors = OnlySet = Zones = LEDs = None
    Speed = 40
    Delay = 3
    for arg in sys.argv:
        if arg == '--C1':
            Pos = sys.argv.index(arg) + 1
            R, G, B = sys.argv[Pos:(Pos + 3)]
            Color1 = RGBColor(int(R),int(G),int(B))
        elif arg == '--C2':
            Pos = sys.argv.index(arg) + 1
            R, G, B = sys.argv[Pos:(Pos + 3)]
            Color2 = RGBColor(int(R),int(G),int(B))
        elif arg == '--colors':
            Colors = []
            ColorsSelected = (sys.argv.index(arg) + 1)
            if ',' in sys.argv[ColorsSelected]:
                for i in sys.argv[ColorsSelected].split(','):
                    RGB = i.split()
                    Colors += [RGBColor(int(RGB[0]), int(RGB[1]), int(RGB[2]))]
            else:
                print("You must specify more than one color.")
                quit()
        elif arg == '--only-set':
            OnlySet = []
            AllowedDevices = (sys.argv.index(arg) + 1)
            if ' , ' in sys.argv[AllowedDevices]:
                for i in sys.argv[AllowedDevices].split(' , '):
                    for D in client.devices:
                        if D.name.strip().casefold() == i.strip().casefold():
                            OnlySet += [D]
            else:
                for D in client.devices:
                    if D.name.strip().casefold() == sys.argv[AllowedDevices].strip().casefold():
                        OnlySet += [D]
        elif arg == '--only-zones':
            Zones = []
            AllowedZones = (sys.argv.index(arg) + 1)
            if ' , ' in sys.argv[AllowedZones]:
                for i in sys.argv[AllowedZones].split(' , '):
                    for D in client.devices:
                        for Z in D.zones:
                            if Z.name.strip().casefold() == i.strip().casefold():
                                Zones += [Z]
            else:
                for D in client.devices:
                    for Z in D.zones:
                        if Z.name.strip().casefold() == sys.argv[AllowedZones].strip().casefold():
                            Zones += [Z]
        elif arg == '--only-leds':
            AllowedLEDs = sys.argv[(sys.argv.index(arg) + 1)]
            LEDs = []
            for s in AllowedLEDs.split(','):
                LEDs += [int(s.strip())]
        elif arg == '--speed':
            Speed = int(sys.argv[(sys.argv.index(arg) + 1)])
        elif arg == '--delay':
            Delay = int(sys.argv[(sys.argv.index(arg) + 1)])
        else:
            pass
    return(Color1, Color2, Colors, Speed, Delay, OnlySet, Zones, LEDs)

def SetStatic(Dlist):
    """A quick function I use to make sure that everything is in direct or static mode"""
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

def Debug(Output):
    if DEBUG:
        print(Output)

def InfiniteCycle(Colors, Zone, Speed, Delay, LEDs):
    RunThrough = 0
    FadeCount = 501-(Speed*10)
    ColorFades = []
    Debug(Colors)
    for i in range(len(Colors)):
        if i == len(Colors)-1:
            ReferenceIndex = 0
        else:
            ReferenceIndex = i+1
        RedShift = (Colors[i].red - Colors[ReferenceIndex].red)/(FadeCount+1)
        GreenShift = (Colors[i].green - Colors[ReferenceIndex].green)/(FadeCount+1)
        BlueShift = (Colors[i].blue - Colors[ReferenceIndex].blue)/(FadeCount+1)
        Fades = []
        Fades.append(Colors[i])
        for f in range(FadeCount):
            Debug(RGBColor(int(Colors[i].red - (RedShift*f)), int(Colors[i].green - (GreenShift*f)), int(Colors[i].blue - (BlueShift*f))))
            Fades.append(RGBColor(int(Colors[i].red - (RedShift*f)), int(Colors[i].green - (GreenShift*f)), int(Colors[i].blue - (BlueShift*f))))
        ColorFades.append(Fades)
    while True:
        for ColorFade in ColorFades:
            Debug(ColorFade)
            for Fade in ColorFade:
                Debug(Fade)
                if Zone.type == ZoneType.SINGLE:
                    Zone.colors[0] = Fade
                    Zone.show()
                elif Zone.type == ZoneType.LINEAR:
                    for i in range(Zone.length):
                        if LEDs is None or i in LEDs: 
                            Zone.colors[i] = Fade
                    Zone.show()
                elif Zone.type == ZoneType.MATRIX:
                    pass
                    #print('matrix support not done yet')
            if Delay != 0:
                time.sleep(Delay)

if __name__ == '__main__':
    C1, C2, Colors, Speed, Delay, Enabled, Zones, LEDs = UserInput()
    if Colors == None:
        Colors = []
        if C1 == None:
            Colors += [RGBColor(255,0,0)]
        else:
            Colors += [C1]
        if C2 == None:
            Colors += [RGBColor(0,0,255)]
        else:
            Colors += [C2]
    Enable = []
    if Enabled == None:
        Enable += [i for i in client.devices]
    elif Enabled != None:
        Enable = Enabled
    if Speed > 50:
        Speed = 50

    SetStatic(Enable)

    for Device in Enable:
        for zone in Device.zones:
            if Zones == None or zone in Zones:
                setattr(zone, 'length', len(zone.leds))
                Thread = threading.Thread(target=InfiniteCycle, args=(Colors, zone, Speed, Delay, LEDs), daemon=True)
                Thread.start()

    Thread.join()