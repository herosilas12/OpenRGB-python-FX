import openrgb, time, sys, threading
from statistics import mean
from openrgb.utils import RGBColor, ModeData, DeviceType, ZoneType

client = openrgb.OpenRGBClient()

Dlist = client.devices

DEBUG = False

def UserInput():
    Color1 = Color2 = Colors = ReversedDevice = OnlySet = Zones = None
    Speed = 50
    Delay = 1
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
        elif arg == '--reversed':
            ReversedDevices = (sys.argv.index(arg) + 1)
            ReversedDevice = []
            if ' , ' in sys.argv[ReversedDevices]:
                for i in sys.argv[ReversedDevices].split(' , '):
                    for D in client.devices:
                        if D.name.strip().casefold() == i.strip().casefold():
                            ReversedDevice += [D]
            else:
                for D in client.devices:
                    if D.name.strip().casefold() == sys.argv[ReversedDevices].strip().casefold():
                        ReversedDevice += [D]
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
        elif arg == '--speed':
            Speed = int(sys.argv[(sys.argv.index(arg) + 1)])
        elif arg == '--delay':
            Delay = int(sys.argv[(sys.argv.index(arg) + 1)])
        else:
            pass
    return(Color1, Color2, Colors, Speed, Delay, ReversedDevice, OnlySet, Zones)

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

def InfiniteCycle(Colors, Zone, Passes, Speed, Delay):
    RunThrough = 0
    FadeCount = 5 * Passes
    ColorFades = []
    for i in range(1, len(Colors), 1):
        RedShift = (Colors[i].red - Colors[0].red)/(FadeCount+1)
        GreenShift = (Colors[i].green - Colors[0].green)/(FadeCount+1)
        BlueShift = (Colors[i].blue - Colors[0].blue)/(FadeCount+1)
        Fades = []
        for f in range(FadeCount, 0, -1):
            Fades.append(RGBColor(int(Colors[0].red + (RedShift*f)), int(Colors[0].green + (GreenShift*f)), int(Colors[0].blue + (BlueShift*f))))
        ColorFades.append(Fades)
    ColorFadeIndex = 0
    while True:
        ZOType = Zone.type
        if ZOType == ZoneType.SINGLE:
            RunThrough += 1
            if (RunThrough%3) == 0:
                if Zone.colors[0] == Colors[0]:
                    Zone.colors[0] = (Colors[1])
                elif Zone.colors[0] == Colors[1]:
                    Zone.colors[0] = (Colors[0])
                elif (Zone.colors[0] != Colors[0]) & (Zone.colors[0] != Colors[1]):
                    Zone.colors[0] = (Colors[1])
                Zone.show()
        elif ZOType == ZoneType.LINEAR:
            if Zone.reverse:
                Index = Zone.length-Zone.index-1
            else:
                Index = Zone.index
            Debug(f"{Index} =======")
            for i in range(Zone.length):
                Zone.colors[i] = Colors[0]
            for p in range(1, Passes+1, 1):
                Debug("B:-----------")
                for f in range(int(FadeCount/Passes)):
                    if Index < Zone.length-(f+1) and Index+(f+1) >= 0:
                        if Zone.reverse:
                            Zone.colors[Index+(f+1)] = ColorFades[ColorFadeIndex][f*Passes+p-1]
                            Debug(f'i:{Index+(f+1)} p:{p} f:{f} f*Passes+p-1:{f*Passes+p-1} Fade:{ColorFades[ColorFadeIndex][f*Passes+p-1]}')
                        else:
                            Zone.colors[Index+(f+1)] = ColorFades[ColorFadeIndex][f*Passes+Passes-p]
                            Debug(f'i:{Index+(f+1)} p:{p} f:{f} f*Passes+Passes-p:{f*Passes+Passes-p} Fade:{ColorFades[ColorFadeIndex][f*Passes+Passes-p]}')
                if Index >= 0 and Index < Zone.length:
                    Zone.colors[Index] = Colors[ColorFadeIndex+1]
                    Debug(Index)
                for f in range(int(FadeCount/Passes)):
                    if Index > f and Index-(f+1) < Zone.length:
                        if Zone.reverse:
                            Zone.colors[Index-(f+1)] = ColorFades[ColorFadeIndex][f*Passes+Passes-p]
                            Debug(f'i:{Index-(f+1)} p:{p} f:{f} f*Passes+Passes-p:{f*Passes+Passes-p} Fade:{ColorFades[ColorFadeIndex][f*Passes+Passes-p]}')
                        else:
                            Zone.colors[Index-(f+1)] = ColorFades[ColorFadeIndex][f*Passes+p-1]
                            Debug(f'i:{Index-(f+1)} p:{p} f:{f} f*Passes+p-1:{f*Passes+p-1} Fade:{ColorFades[ColorFadeIndex][f*Passes+p-1]}')
                Zone.show()
                Debug("E:-----------")
            Zone.index += 1
            if Zone.index == Zone.length+6:
                Zone.index = -6
                if ColorFadeIndex < len(ColorFades)-1:
                    ColorFadeIndex += 1
                else:
                    ColorFadeIndex = 0
                if Delay != 0:
                    time.sleep(Delay)
        elif ZOType == ZoneType.MATRIX:
            pass
            #print('matrix support not done yet')

if __name__ == '__main__':
    Debug(client.devices)
    C1, C2, Colors, Speed, Delay, Reversed, Enabled, Zones = UserInput()
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
    Passes = 51 - Speed
    if Passes < 1:
        Passes = 1

    SetStatic(Enable)

    for Device in Enable:
        Debug(Device.zones)
        ReverseBool = False
        if Reversed != None:
            for R in Reversed:
                if R == Device:
                    ReverseBool = True
                    continue
                else:
                    ReverseBool = False
        for zone in Device.zones:
            if Zones == None or zone in Zones:
                setattr(zone, 'index', -6)
                setattr(zone, 'length', len(zone.leds))
                setattr(zone, 'reverse', ReverseBool)
                Thread = threading.Thread(target=InfiniteCycle, args=(Colors, zone, Passes, Speed, Delay), daemon=True)
                Thread.start()

    Thread.join()
