
#from utils import *
#from spotify_utils import *
from utils_light import *
import logging
from random import randint
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session
import spotipy
import spotipy.util as util

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger("flask_ask").setLevel(logging.DEBUG)

scope = 'user-top-read user-read-recently-played'

token = util.prompt_for_user_token('aaronopp', scope, client_id='dbe2a20785304190b8e35d5d6644397b', client_secret='d73cf4a1525c44e899feeeff4b840040', redirect_uri='http://localhost:5555/redirect')

output_on_osc_route = '/lx/output/enabled'
channel_1_pattern_osc_route = '/lx/channel/1/activePattern'
color_osc_route = '/lx/palette/color/hue'
speed_osc_route = '/lx/engine/speed'
blur_osc_route = '/lx/channel/1/effect/1/amount/'
bright_osc_route = '/lx/output/brightness'

patterns_full = ['AskewPlanes', 'Balance', 'Ball', 'BassPod', 'Blank', 'Bubbles', 'CrossSections', 'CubeEQ', 
                 'CubeFlash', 'Noise', 'Palette', 'Pong', 'Rings', 'ShiftingPlane', 'SoundParticles', 'SpaceTime',
                'Spheres', 'StripPlay', 'Swarm', 'Swim', 'TelevisionStatic', 'Traktor', 'ViolinWave']

patterns_lower = [x.lower() for x in patterns_full]
color_labels_encoding = ['red', 'orange', 'yellow', 'green', 'teal', 'blue', 'purple', 'magenta']
speed_labels = ['slow', 'medium', 'fast']
effect_labels = ['low', 'medium', 'high']
brightness_labels = ['off', 'dim', 'down', 'half', 'up', 'full', 'bright']

bright_unencode = [0.0, 0.3, 0.3, 0.5, 0.7, 1.0, 1.0]
speed_unencode = [0.2, 0.5, 0.8]
color_unencode = [0.0, 0.08, 0.15, 0.35, 0.48, 0.67, 0.76, 0.84]
effect_unencode = [0.0, 0.3, 0.6, 0.9]

@ask.launch
def start_ai_vj():

    welcome_msg = render_template('start')
    return question(welcome_msg)

# @ask.intent("YesIntent")
# def next_song():

#     numbers = [randint(0, 9) for _ in range(3)]

#     round_msg = render_template('round', numbers=numbers)

#     session.attributes['numbers'] = numbers[::-1]  # reverse

#     return question(round_msg)

@ask.intent("TurnOnIntent", convert={'isOn': str})
def turn_on(isOn):
    
    if isOn == 'on':
        print("yaas")
        print(isOn)
        send_osc(output_on_osc_route, 1)
        on_msg = render_template('turnon')
        return statement(on_msg)
# send osc to turn on lights
    else: 
        # turn off
        print(isOn)
        off_msg = render_template('turnoff')
        send_osc(output_on_osc_route, 0)
        return statement(off_msg)
@ask.intent("PatternIntent", convert={'pattern': str})
def change_pattern(pattern):
    

    send_osc(channel_1_pattern_osc_route, 7)
    print(pattern)
    pattern = pattern.replace(' ', '')
    if pattern == 'askewplane':
        pattern = 'askewplanes'
    if pattern == 'rain' or pattern =='ring':
        pattern = 'rings'
    print('pattern aft:', pattern)
    pattern_index = next(i for i, pat in enumerate(patterns_lower) if pattern in pat)
    print('pat index:', pattern_index)

    pattern_msg = render_template('pattern', pattern=pattern)
    #get_max_label(actual_pattern, patterns_full)
    send_osc(channel_1_pattern_osc_route, pattern_index)
    return statement(pattern_msg)
    

@ask.intent("ColorIntent", convert={'color': str})
def change_color(color):
    none_msg = render_template('none')
    print(color)
    if color in speed_labels:
        change_speed_no_intent(speed)
    if color in brightness_labels:
        change_brightness_no_intent(speed)
    
    try:
        color_index = next(i for i, col in enumerate(color_labels_encoding) if color in col)
        print('found color index')

    except:
        return statement(none_msg)
    # except:
    #     try:
    #         speed_index = next(i for i, spd in enumerate(speed_labels) if speed in spd)
    #         speed_msg = render_template('speed', speed=speed)
    #         send_osc(speed_osc_route, speed_unencode[speed_index])
    #         print('in speed -> color', speed)
    #         return statement(speed_msg)
        # except:
    
            # return statement(none_msg)
    
    print(color_index)
    send_osc(color_osc_route, color_unencode[color_index])
    color_msg = render_template('color', color=color)
    return statement(color_msg)
    # else:
        # return statement(none_msg)
    #send_osc(speed_osc_route, speed_unencode[speed_index])
    #send_osc(blur_osc_route, effect_unencode[blur_index])
    #send_osc(desat_osc_route, effect_unencode[desat_index])

    # send color osc
@ask.intent("SpeedIntent", convert={'speed': str})
def change_speed(speed):
    print('speed:', speed)
    #s send speed osc
    if speed.endswith('er'):
        speed = speed[:-2]
    speed_index = next(i for i, spd in enumerate(speed_labels) if speed in spd)
    print(speed_index)
    speed_msg = render_template('speed')
    send_osc(speed_osc_route, speed_unencode[speed_index])
    print(speed)
    return statement(speed_msg)

@ask.intent("BrightnessIntent", convert={'brightness': str})
def change_brightness(brightness):
    print('bright:' , brightness)
    if brightness == "dimmer":
        brightness = brightness[:-3]
    if brightness.endswith('er'):    
        brightness = brightness[:-2]

    bright_index = next(i for i, brt in enumerate(brightness_labels) if brightness in brt)
    print(bright_index)
    bright_msg = render_template('brightness')
    send_osc(bright_osc_route, bright_unencode[bright_index])
    return statement(bright_msg)
@ask.intent("AMAZON.HelpIntent")
def help():
    print('help triggered')
    help_msg = render_template('help')
    return statement(help_msg)
@ask.intent("AMAZON.StopIntent")
def stop():
    print('stop trigg')
    send_osc(output_on_osc_route, 0)
    stop_msg = render_template('stop')
    return statement(stop_msg)
@ask.intent("AMAZON.CancelIntent")
def cancel():
    print('cancel trig')
    send_osc(output_on_osc_route, 0)
    cancel_msg = render_template('cancel')
    return statement(cancel_msg)



def change_speed_no_intent(speed):
    print('change speed no intent')
    print('speed:', speed)
    #s send speed osc
    if speed.endswith('er'):
        speed = speed[:-2]
    speed_index = next(i for i, spd in enumerate(speed_labels) if speed in spd)
    print(speed_index)
    speed_msg = render_template('speed')
    send_osc(speed_osc_route, speed_unencode[speed_index])
    print(speed)
    return statement(speed_msg)

def change_brightness_no_intent(brightness):
    print('bright:' , brightness)
    if brightness == "dimmer":
        brightness = brightness[:-3]
    if brightness.endswith('er'):    
        brightness = brightness[:-2]

    bright_index = next(i for i, brt in enumerate(brightness_labels) if brightness in brt)
    print(bright_index)
    bright_msg = render_template('brightness')
    send_osc(bright_osc_route, bright_unencode[bright_index])
    return statement(bright_msg)
# @ask.intent("AiVjIntent", convert={'isOn': boolean})
# def turn_on_ai_vj():
#     if isOn:
#         print (isOn)
#         # send osc
#     else:
#         print (isOn)

# @ask.intent("SpotifyIntent", convert={'isOn': boolean})
# def turn_on_spotify():
#     if isOn:
#         if token:
#             devices = sp.devices()
#             print (devices)

#             start_playback(device_id=devices[0])
        # destroy
# @ask.intent("AnswerIntent", convert={'first': int, 'second': int, 'third': int})
# def answer(first, second, third):

#     winning_numbers = session.attributes['numbers']

#     if [first, second, third] == winning_numbers:

#         msg = render_template('win')

#     else:

#         msg = render_template('lose')

#     return statement(msg)


if __name__ == '__main__':

    app.run(debug=True)