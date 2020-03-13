#!/usr/bin/env python3
# Trying out threading
class ParadoxicalChronologicalArgumentError(Exception):
    def __init__(self):
        self.msg = 'When calling the time_diff function you need to put your starting time as the first argument and ' \
                   'your finish/end timeas the second argument otherwise the program will raise an error; or you will ' \
                   'get innacurrate output'


class InvalidTemperatureScale(Exception):
    """

    An exception class to be raised if a part of the program is asked to provide a reading in an invalid temperature
    measurement scale. Ultimately; there are three choices for the measurement scale the program can use.

        - Celsius (doesn't have to be capitalized)
        - Fahrenheit (doesn't have to be capitalized)
        - Kelvin (doesn't have to be capitalized)

        (See the documentation for get_temp in lib/sense/poll.py for more information)

    """


def time_diff(start_time, end_time):
    try:
        if end_time >= start_time:
            raise ParadoxicalChronologicalArgumentError()

        _diff = end_time - start_time
        return _diff
    except ParadoxicalChronologicalArgumentError as e:
        print(e.msg)


from .lib.conf import runtime
import PySimpleGUI as gui
import sys

from sense_emu import SenseHat

import threading
from time import sleep
from numpy import mean

from datetime import datetime
from colorsys import hsv_to_rgb

# Initialize the SenseHat class and assign it's object to a variable
sense = SenseHat()

verbose = False
pretty = False

all_stop = False

verbose_flags = ['-v', '--verbose', '--debug']

if '-v' in sys.argv:
    verbose = True
if '--verbose' in sys.argv:
    verbose = True

pretty_flags = ['-p', '--pretty', '--formatted']

for flag in pretty_flags:
    if flag in sys.argv:
        pretty = True

name = "TestModule"
notation = None

animating = False
working = conf.working
cur_temp = None

collected_temps = []
collected_hums = []
collected_pres = []

fahrenheit_flags = ['f', 'fahrenheit', 'imperial', 'us', 'u.s.', 'usa', 'u.s.a.']
centigrade_flags = ['centigrade', 'celsius', 'c', 'metric', 'europe']


def write_temp():
    with open('.cur_temp.tmp', 'w') as file:
        file.write(cur_temp)


def animate_device(device=None):
    global animating, hues, all_stop, sense
    import time
    animating = True

    while animating:

        if all_stop:
            sense.show_message('Goodbye!')
            sense.clear()
            exit()

        # Rotate the hues
        hues = [(h + 0.01) % 1.0 for h in hues]
        # Convert the hues to RGB values
        pixels = [hsv_to_rgb(h, 1.0, 1.0) for h in hues]
        # hsv_to_rgb returns 0..1 floats; convert to ints in the range 0..255
        pixels = [(scale(r), scale(g), scale(b)) for r, g, b in pixels]
        # Update the display
        sense.set_pixels(pixels)
        sleep(0.04)

    sense.clear()


def convert_to_f(temp):
    """

    Convert a float or integer that represents a Celsius temperature to fahrenheit

    """
    f = (temp * 9 / 5) + 32

    return f


def convert_to_k(temp, rounded=False):
    k = temp + 273

    if rounded:
        k = round(k, 2)

    return k


# Give us the ability to return a nice pretty temp string
def format_temp(temp, unit_scale):
    global fahrenheit_flags
    if unit_scale.lower() in fahrenheit_flags:
        temp = str(f'{notate("temp", temp, unit_scale)}')

    return temp


def show_temp(scale=None, rounded=True):
    global cur_temp, animating, all_stop, sense, verbose

    if all_stop:
        return

    animating = False
    old_temp = cur_temp
    cur_temp = sense.temp
    if rounded:
        cur_temp = round(cur_temp)

    # Clear the screen so we don't have LED's that are still multicolored lingering around
    sense.clear()
    sense.show_message(f'{format_temp(convert_to_f(cur_temp), "f")}')
    if verbose:
        print('Send message to the matrix')

    animating = True
    animation2 = threading.Thread(target=animate_device)

    _timer = threading.Timer(10, show_temp, )
    animation2.start()
    _timer.start()

    _timer.join()
    animation2.join()


def notate(v_type, num, unit_scale=None):
    """

    Attach the proper notation to the end of your data values.

    """
    _notation = None

    if v_type.lower() == 'pres' or v_type.lower() == 'pressure' or v_type.lower() == 'p':
        _notation = 'mBar'

    if v_type.lower() == 'temp' or v_type.lower() == 'temperature' or v_type.lower() == 't':

        if unit_scale is None:
            _notation = ' °C'
        elif unit_scale == 'f':
            _notation = ' °F'
        elif unit_scale == 'k':
            _notation = ' °K'

    if v_type.lower() == 'hum' or v_type.lower() == 'humidity' or v_type.lower() == 'h':
        _notation = '%'

    notated = str(f'{num}{_notation}')
    return notated


def get_temp(unit_scale='f', rounded=False, get_formatted=True):
    """

    A function to get the current ambient temperature from the temperature sensor on the SenseHat

    :type rounded: Boolean
    :param unit_scale: String
        Ultimately what you put in here will/should boil down to three choices:

        - Celsius (doesn't have to be capitalized)
            - Will also accept:
                - c
                - centigrade
                - metric
                - europe

        - Fahrenheit (doesn't have to be capitalized)
            - Will also accept:
                - f
                - imperial
                - us, u.s.
                - usa, u.s.a.

        - Kelvin (doesn't have to be capitalized)
            - Will also accept:
                - k

    :param rounded: Boolean
        This is a boolean indicating whether or not the returned temperature reading should be rounded. (The default for
        this parameter is False)


    :param get_formatted: Boolean
        This is a boolean that defaults to True. This acts as a flag for the function which will tell it whether a
        single value should be returned from the sensor data or if a Tuple should be returned with both formatted and
        un-formatted values


    :returns: Float or Tuple (Float, String)

    """
    global collected_temps, notation, sense, cur_temp
    _temp = sense.temp
    temp = _temp

    if unit_scale is None:
        unit_scale = 'f'

    if unit_scale in fahrenheit_flags:
        _temp = convert_to_f(_temp)
        if verbose:
            print(_temp)

    if rounded:
        temp = round(_temp, 2)

    if get_formatted:
        temp = format_temp(_temp, unit_scale)

    cur_temp = temp
    write_temp()

    collected_temps.append(_temp)
    # print(_temp)

    return temp, _temp


def format_hum(_hum, rounded=False):
    """

    Will return with a formatted version of the humidity number you provide for the first parameter.

    :param _hum: The number you'd like formatted as a relative humidity reading. This could mean just adding a
        percentage symbol or (if True is provided for the "rounded" parameter) rounding the number down to something
        more easily readable by a human.

    :param rounded: Boolean
        (Defaults to False) Provide a rounded copy of the value provided in the first parameter in the final return
        string.

    :returns: String

    """
    if rounded:
        _hum = round(_hum, 2)
    humidity = notate('h', _hum, None)

    return humidity


def get_hum():
    """

    A method to contact the Sense Hat and gather humidity data.

    This will return a tuple which contains the humidity data in two forms. The first value in the tuple will be the
    raw, unrounded version of the sensor read's result the second will be presented as asked.

    ToDO:
        - Add call to the humidity sensor's temperature reading

    """
    global collected_hums, verbose, sense

    _hum = sense.humidity
    collected_hums.append(_hum)
    f_hum = notate('h', _hum)
    if verbose:
        print(f'Got humidity: {_hum}, {f_hum}')
    return _hum, f_hum


def format_pres(_pres, rounded=False):
    """

    A method to format pressure data into a more readable value

    :param _pres: Should be an integer that needs to be formatted as atmospheric pressure in mBars

    """
    if rounded:
        _pres = round(_pres, 2)
    pressure = notate('p', _pres, None)

    return pressure


def get_pres():
    """

    A method to call gather atmospheric pressure data from the sensors on the Sense Hat.

    This method will poll the atmospheric pressure sensor on the Sense Hat. This sensor will return with the atmospheric
    pressure as measured in mBars. Once we have the data

    :returns: Tuple (raw pressure data, formatted pressure)

    ToDo:
        - Add call to pressure sensor's temperature reading
    """
    global collected_pres, sense

    _pres = sense.pressure
    collected_pres.append(_pres)
    f_pres = notate('p', _pres, None)
    if verbose:
        print(f'Got pressure: {_pres}, {f_pres}')
    return _pres


def clean_exit():
    from os import remove
    from os.path import isfile

    if isfile('.cur_temp.tmp'):
        remove('.cur_temp.tmp')


def stop_working():
    """

    A method to tell our threads to stop.

    """
    global working, all_stop, conf

    working = False
    conf.working = False
    all_stop = True

    print('Stopping the working')

    # Do a little cleanup work

    clean_exit()


def poll_device(temp_scale='f', device=None, rounded=False):
    """

    A function that polls the given device

    """
    import time

    global collected_temps, working, animating
    working = True

    while working:

        _temp = get_temp(temp_scale, rounded)
        _hum = get_hum()
        _pres = get_pres()
        item_count = len(collected_temps) + 1
        data_entry = {
            item_count: [
                _temp,
                _hum,
                _pres

            ]
        }
        sleep(0.1)
        item_num = len(collected_temps)
        if verbose:
            print(f'{item_num} sensor reads. Last read was: {_temp}')


hues = [
    0.00, 0.00, 0.06, 0.13, 0.20, 0.27, 0.34, 0.41,
    0.00, 0.06, 0.13, 0.21, 0.28, 0.35, 0.42, 0.49,
    0.07, 0.14, 0.21, 0.28, 0.35, 0.42, 0.50, 0.57,
    0.15, 0.22, 0.29, 0.36, 0.43, 0.50, 0.57, 0.64,
    0.22, 0.29, 0.36, 0.44, 0.51, 0.58, 0.65, 0.72,
    0.30, 0.37, 0.44, 0.51, 0.58, 0.66, 0.73, 0.80,
    0.38, 0.45, 0.52, 0.59, 0.66, 0.73, 0.80, 0.87,
    0.45, 0.52, 0.60, 0.67, 0.74, 0.81, 0.88, 0.95,
]

hum_stats = []


def scale(v):
    return int(v * 255)


def main(*argv):
    global verbose
    verbose = False
    run_time = argv[0]
    if ['--verbose', '-v'] in argv:
        verbose = True
    timer = threading.Timer(int(run_time), stop_working)
    timer2 = threading.Timer(15, show_temp)
    print("Main      : Before creating working thread")
    poll = threading.Thread(name='POLL_DEVICE', target=poll_device, args=('f', None, True))
    print('Main      : working thread created, creating animate thread')
    animation = threading.Thread(target=animate_device)
    print('Main      : Animation thread created, before running threads')
    animation.start()
    poll.start()
    timer.start()
    timer2.start()
    print("Main      : Wait for the thread to finish")
    poll.join()
    animating = False
    print('Main      : Threads are finished! Clearing device screen.')

    t_average = mean(collected_temps)
    formatted_t_avg = format_temp(t_average, 'f')
    t_lowest = min(collected_temps)
    formatted_t_lowest = format_temp(t_lowest, 'f')
    t_highest = max(collected_temps)
    print(f'Average temperature was {formatted_t_avg}')
    print(f'The lowest temperature recorded was {formatted_t_lowest}')
    print(f'The highest temperature recorded was {t_highest}')

    h_average = mean(collected_hums)
    f_h_average = format_hum(h_average, True)
    h_lowest = min(collected_hums)
    f_h_lowest = format_hum(h_lowest, True)
    h_highest = max(collected_hums)
    f_h_highest = format_hum(h_highest, True)
    print(f'Average humidity was: {f_h_average}')
    print(f'The lowest humidity recorded was: {f_h_lowest}')
    print(f'The highest humidity recorded was: {f_h_highest}')

    p_average = mean(collected_pres)
    f_p_average = format_pres(p_average, True)
    p_lowest = min(collected_pres)
    f_p_lowest = format_pres(p_lowest, True)
    p_highest = max(collected_pres)
    f_p_highest = format_pres(p_highest, True)
    print(f'Average pressure was: {p_average}')
    print(f'The lowest pressure recorded was: {f_p_lowest}')
    print(f'The highest pressure recorded was {f_p_highest}')

    data_log = zip(collected_temps, collected_hums, collected_pres)
    data_log = list(data_log)
    if verbose:
        print(data_log)
    else:
        from os import path, getcwd
        from pathlib import Path
        import time

        timestr = time.strftime("%Y%m%d-%H%M%S")
        logpath = str(getcwd() + f'/logs/')
        p_lib = Path(logpath)
        p_lib.absolute()
        if not path.exists(p_lib):
            p_path = Path(p_lib)
            print(p_path)
            p_lib.mkdir(parents=True)

        else:
            print('It exists')

        with open(p_lib.joinpath(p_lib, f'{timestr}.log'), "a") as file:
            for entry in data_log:
                file.write(str(entry) + '\n')
    print('All done')
