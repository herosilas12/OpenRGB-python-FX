# OpenRGB-python-FX

## Effect List

* Rainbow wave (rainbow.py)

* Spectrum cycling (cycle.py) (Credit to James Potkukelkka on discord for this one)

* Gradient cycling (GradCycle.py)

* Breathing

* Ambient (credit to usrErr0r on discord for this one, Not working on linux due to ImageGrab not having an import)

* Rain (**Massive** thanks and credit to Bahorn on discord for this one)

* Cram

* Chase (Per request of Titanium on Discord)

* Chase Fade (Created by @ Fmstrat on GitHub) (Supports multi-color and rolling colors (matrix wave) for smooth scrolling across LEDs)

* Rave (Basically multiple instances of rain with different colors that make a cool effect, Discovered by Saint Mischievous on discord)

* Stary Night (Per request of BrandonPotter on the discord)

* TempAware (Created by @ M_Ouz on the discord) (Only tracks GPU temp atm)

If you would like a specific effect then DM me on discord (CoffeeIsLife)

## Usage

* start the openRGB sdk server, otherwise this *will not work*

* you may need to install the sdk binding ```pip install openrgb-python``` or ```pip3 install openrgb-python``` (you may also need to add --user at the end for linux)

* clone the repository or download the effect you want

* cd into the folder with the python files

* run using ```python3 file.py``` or ```python file.py```

* enjoy the effect :)

### Most effects support flags, See the table below for details

Effect (left to right), Flag (top to bottom)

|           | Ambient| Breathing | Chase | Chase Fade | Cram | Cycle | Gradcycle | Rain | Rainbow wave | Rave| Stary Night (Twinkle) | TempAware |
|-----------|--------|-----------|-------|------------|------|-------|-----------|------|--------------|-----|-----------------------|-----------|
|C1         | No     | Yes       | Yes   | Yes        | Yes  | No    | Yes       | Yes  | No           | No  | Yes                   | No        |
|C2         | No     | No        | Yes   | Yes        | No   | No    | Yes       | No   | No           | No  | No                    | No        |
|Colors     | No     | No        | No    | Yes        | No   | No    | No        | No   | No           | No  | No                    | No        |
|Speed      | No     | Yes       | No    | Yes        | No   | No    | Yes       | No   | Yes          | No  | No                    | No        |
|Delay      | No     | No        | No    | Yes        | No   | No    | No        | No   | No           | No  | No                    | No        |
|Reversed   | No     | No        | Yes   | Yes        | No   | No    | Yes       | Yes  | Yes          | Yes | No                    | No        |
|Only-Set   | No     | Yes       | Yes   | Yes        | Yes  | Yes   | Yes       | Yes  | Yes          | Yes | Yes                   | No        |
|Only-Zones | No     | No        | No    | Yes        | No   | No    | No        | No   | No           | No  | No                    | No        |

* ``--C1``: AKA Color 1. Usage is ``python file.py --C1 Value(0 - 255) Value(0 - 255) Value(0-255)`` or ``python file --C1 0 0 255``

* ``--C2``: AKA Color 2. Same Usage as C1 but with a different flag

* ``--colors``: An optional replacement for C1 and C2 on effects that support it when you want to use more than 2 colors. Usage is ``python file.py --colors "255 0 0, 0 255 0, 0 0 255"``

* ``--speed``: Self explanitory, It is kinda hard to implement or I am lazy so it isn't in a lot of effects. Usage is ``python file.py --speed int`` (any number is fine but I haven't tested over 50)

* ``--delay``: When an effect is between transitions or fades, set the number of seconds it should wait to start the next transition or fade. Usage is ``python file.py --delay int``

* ``--reversed``: Reverses effects for specific devices. Usage is ``python file.py --reversed "example device"`` or ``python file.py --reversed "device 1 , device 2`` for multiple devices. seperate the devices by `` , ``(space comma space)

* ``--only-set``: Used if you only want to apply the effect to one device. I made it a goal for all effects to use this flag. Enables all devices if the flag isn't called. Also same usage as --reversed but with a different flag

* ``--only-zones``: Used if you only want to apply the effect to specific zones. Enables all zones if the flag isn't called. Also same usage as --reversed but with a different flag

## Writing effects

For an Effect to be added it need to follow a set of guidelines

1. Must be somewhat legible

2. Have support for single device effects (see most of the already added effects for an example)

3. Must support being added as a module (The effect is a function(``def effect(args):``) and it is run through a ``if __name__ == "__main__":`` statement)

4. if a zone type is not supported then make sure that you add an if statement that just doesn't set that particular zone (see rainbow.py)

If you have an effect please create an MR with the effect or just @ me on discord about it and I will make any nescissary changes and add it (with credit to you in the readme of course)

Effects are stored in their own .py file for now

```python
import openrgb , time , string , colorsys , sys
from openrgb.utils import RGBColor , ModeData , DeviceType , ZoneType

client = openrgb.OpenRGBClient()

Dlist = client.devices
```

is a good starting point

Since I want this to be a fairly easy process you can just create the effect loop and I will modify it to fit the guidelines if you feel stressed about trying to meet all of the requests

## Notes

While this is system wide, there are some limitations.

if the device isn't in openRGB then the effect *will not* apply to it

currently rainbow is poorly optimized due to a lack of big brainedness on my part (I did do some optimizations that allows me to use .show() and that made it more readable for other people)

Ambient grabs the entire screen leading to some shade of white or black. hopefully this will get fixed soon

## *Special Usage**

### TempAware

You may need to set a full path for the DLL if it doesn't run correctly

Python also uses escape characters so if you need to use a \ (Backslash) then you will need to use 2 of them (``\\`` == ``\`` in python)

## Todo

* Add matrix zone support for some effects (rainbow wave and gradcycle) (included in chase wave)

* Smooth out some of the effects (rainbow wave)

* Create GUI for launching effects (most effects are built as functions so incorporating them wouldn't be that hard)
