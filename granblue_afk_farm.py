#! /usr/bin/env python3

import sys
import pytesseract
from PIL import Image
import PIL
from pynput.keyboard import Key, Controller
from pynput import keyboard
from pynput.mouse import Button, Controller as MouseController
import time
import math

# Import ImageGrab if possible, might fail on Linux
try:
    from PIL import ImageGrab
    use_grab = True
except Exception as ex:
    # Some older versions of pillow don't support ImageGrab on Linux
    # In which case we will use XLib 
    if ( sys.platform == 'linux' ):
        from Xlib import display, X   
        use_grab = False
    else:
        raise ex


def screenGrab( rect ):
    """ Given a rectangle, return a PIL Image of that part of the screen.
        Handles a Linux installation with and older Pillow by falling-back
        to using XLib """
    global use_grab
    x, y, width, height = rect

    if ( use_grab ):
        image = PIL.ImageGrab.grab( bbox=[ x, y, x+width, y+height ] )
        #print("x =", x, " y= ", y, " x+width = ", x+width, " y + height = ", y + height)
    else:
        # ImageGrab can be missing under Linux
        dsp  = display.Display()
        root = dsp.screen().root
        raw_image = root.get_image( x, y, width, height, X.ZPixmap, 0xffffffff )
        image = Image.frombuffer( "RGB", ( width, height ), raw_image.data, "raw", "BGRX", 0, 1 )
        # DEBUG image.save( '/tmp/screen_grab.png', 'PNG' )
    return image


### Do some rudimentary command line argument handling
### So the user can speicify the area of the screen to watch
if ( __name__ == "__main__" ):
    input('Scripts combined by Adam Slam Fu Lew, Press Enter to begin')
    CURRENT_NUM_MODES = 2
    inMode = -1
    while(inMode <= -1 or math.isnan(inMode) or inMode >= CURRENT_NUM_MODES): 
        try:
            inMode = int(input('Select a Mode: \n0: Default\n1: Lancelot Spam\n'))
        except ValueError:
            inMode = -1
            print('Please enter a valid mode')
    
    EXE = sys.argv[0]
    del( sys.argv[0] )

    # EDIT: catch zero-args
    if ( len( sys.argv ) != 4 or sys.argv[0] in ( '--help', '-h', '-?', '/?' ) ):  # some minor help
        sys.stderr.write( EXE + ": monitors section of screen for text\n" )
        sys.stderr.write( EXE + ": Give x, y, width, height as arguments\n" )
        sys.exit( 1 )

    # TODO - add error checking
    x      = int( sys.argv[0] )
    y      = int( sys.argv[1] )
    width  = int( sys.argv[2] )
    height = int( sys.argv[3] )

    # Area of screen to monitor
    screen_rect = [ x, y, width, height ]  
    #print( EXE + ": watching " + str( screen_rect ) )
    pynkeyboard = Controller()
    mouse = MouseController()

    ### Loop forever, monitoring the user-specified rectangle of the screen
    state = "Fighting"

    exitFlag = False

    def on_press(key):
        try:
            print('alphanumeric key {0} pressed'.format(
                key.char))
        
        except AttributeError:
            print('special key {0} pressed'.format(
                key))

    def on_release(key):
        print('{0} released'.format(
            key))
        if key == keyboard.Key.esc:
            # Stop listener
            global exitFlag
            exitFlag = True
            print('exitFlag set to {0}'.format(exitFlag))
            return False

    # ...or, in a non-blocking fashion:
    listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release)
    listener.start()

    while (not exitFlag):
        image = screenGrab( screen_rect )              # Grab the area of the screen
        text  = pytesseract.image_to_string( image )   # OCR the image

        # IF the OCR found anything, write it to stdout.
        text = text.strip()
        if ( len( text ) > 0 ):
            print(text)
        text = text.lower()

        if ("evalu" in text):
            state = 'Evaluation'
        elif ("continue" in text) or ("playing" in text):
            print("Prompt to continue found")
            pynkeyboard.press('w')
            time.sleep(0.25)
            pynkeyboard.release('w')
            #pynkeyboard.press(Key.enter)
            mouse.press(Button.left)
            time.sleep(0.25)
            #pynkeyboard.release(Key.enter)
            mouse.release(Button.left)
            print("Continueing AFK Farm")
            state = 'Prompt'
        elif ("rewards" in text) or ("reviewing" in text) :
            state = "Rewards"
        else:
            if (state == "Rewards") or (state == "Prompt"):
                print("Back to combat")
                state = "Fighting"
        print(state)
        if (state == "Evaluation") or (state == "Rewards") or (state == "Prompt"):
            #pynkeyboard.press(Key.enter)
            mouse.press(Button.left)
            time.sleep(0.25)
            #pynkeyboard.release(Key.enter)
            mouse.release(Button.left)
            counter = 1
        else:
            counter = 3
        sleepTime = 1
        if (state == "Fighting" and inMode == 1):
            sleepTime = 0.25
        while (counter > 0):
            if (state == "Fighting" and inMode == 1):
                mouse.press(Button.right)
                time.sleep(0.10)
                pynkeyboard.press('r')
                time.sleep(0.10)
                pynkeyboard.press('g')
                time.sleep(0.10)
                mouse.release(Button.right)
                time.sleep(0.10)
                pynkeyboard.release('r')
                time.sleep(0.05)
                pynkeyboard.release('g')
                time.sleep(0.05)
                counter = counter - 0.5
            else:
                counter = counter - sleepTime
                time.sleep(sleepTime)
        if (state == "Fighting" and inMode == 1):
            mouse.press(Button.right)
            time.sleep(0.05)
            mouse.press(Button.middle)
            time.sleep(0.10)
            mouse.release(Button.right)
            time.sleep(0.05)
            mouse.release(Button.middle)
            time.sleep(0.05)
    print('Farming has ended, see you next time :)')            
        
