#! /usr/bin/env python3

import sys
import pytesseract
from PIL import Image
import PIL
from pynput.keyboard import Key, Controller
from pynput.mouse import Button, Controller as MouseController
import time


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
    keyboard = Controller()
    mouse = MouseController()

    ### Loop forever, monitoring the user-specified rectangle of the screen
    state = "Fighting"
    while ( True ): 
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
            keyboard.press('w')
            time.sleep(0.25)
            keyboard.release('w')
            #keyboard.press(Key.enter)
            mouse.press(Button.left)
            time.sleep(0.25)
            #keyboard.release(Key.enter)
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
            #keyboard.press(Key.enter)
            mouse.press(Button.left)
            time.sleep(0.25)
            #keyboard.release(Key.enter)
            mouse.release(Button.left)
            counter = 1
        else:
            counter = 3
        while (counter > 0):
            counter = counter - 1
            time.sleep(1)
        
