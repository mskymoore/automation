#!/usr/local/bin/python3

# usage: autoClickIt.py [-h] -i inputImagePath [-f searchFrequency]
#                       [-d preClickDelay] [-n postClickDelayMin]
#                       [-x postClickDelayMax]
#
# optional arguments:
#   -h, --help            show this help message and exit
#   -i inputImagePath, --image inputImagePath
#                         The image to repeatedly click the center of.
#   -f searchFrequency, --frequency searchFrequency
#                         Frequency in Hz to search the screen for the image.
#   -d preClickDelay, --delay preClickDelay
#                         Delay in seconds between program seeing the input
#                         image on screen and clicking it.
#   -n postClickDelayMin, --postClickDelayMin postClickDelayMin
#                         Lower bound or random wait time after a click.
#   -x postClickDelayMax, --postClickDelayMax postClickDelayMax
#                         Upper bound of random wait time after a click.
#   -c factor, --coordinateFactor factor
#                         Divides the pyautogui reported location by this number
#                         to adjust click location. Try supplying 2 if clicks
#                         are not accurate.


import pyautogui as pg
from pynput.keyboard import Controller as keyboardController
from pynput.keyboard import Listener as _keyboardListener
from pynput.keyboard import Key
from pynput.mouse import Controller as mouseController
from pynput.mouse import Listener as _mouseListener
from argparse import ArgumentParser
from time import sleep
from os import system
from pathlib import Path
from random import uniform


parser = ArgumentParser()
parser.add_argument('-i', '--image', help='The image to repeatedly click the center of.',
                    type=str, metavar='inputImagePath', required=True)
parser.add_argument('-f', '--frequency', help='Frequency in Hz to search the screen for the image.',
                    type=int, metavar='searchFrequency', required=False, default=3, choices=range(1,11))
parser.add_argument('-d', '--delay', help='Delay in seconds between program seeing the input image on screen and clicking it.',
                    type=int, metavar='preClickDelay', required=False, default=0)
parser.add_argument('-n', '--postClickDelayMin', help='Lower bound of random wait time after a click.',
                    type=int, metavar='postClickDelayMin', required=False, default=5)
parser.add_argument('-x', '--postClickDelayMax', help='Upper bound of random wait time after a click.',
                    type=int, metavar='postClickDelayMax', required=False, default=9)
parser.add_argument('-c', '--coordinateFactor', help='Divides the pyautogui reported location by this number to adjust click \
                    location.  Try supplying 2 if clicks are not accurate.', metavar='factor', required=False, type=int,
                    default=1, choices=range(1,11))
args = parser.parse_args()


def main():

    global args
    imgPath = args.image
    preClickDelay = args.delay
    searchPeriod = 1/args.frequency
    postClickDelayMin = args.postClickDelayMin
    postClickDelayMax = args.postClickDelayMax
    coordinateFactor = args.coordinateFactor

    if not Path(imgPath).exists():
        print("\nPath supplied does not exist.\n")
        parser.print_help()
        exit(1)

    if postClickDelayMax < 0 or postClickDelayMin < 0 or preClickDelay < 0:
        print("\nDelays must be non-negative.\n")
        parser.print_help()
        exit(1)


    # boolean for mouse use status
    interfaceInUse = False


    # handle mouse events
    def in_use(*args):
        nonlocal interfaceInUse
        interfaceInUse = True


    # keyboard and mouse controllers
    keyboard = keyboardController()
    mouse = mouseController()

    # listen to mouse
    mouseListener = _mouseListener(on_move=in_use, on_click=in_use, on_scroll=in_use)
    mouseListener.start()

    # listen to keyboard
    keyboardListener = _keyboardListener(on_press=in_use, on_release=in_use)
    keyboardListener.start()

    # track how many clicks have been done
    counter = 0

    print('Active and searching...')
    while True:
        try:
            interfaceInUse = False
            # check for image at approximately 3Hz
            sleep(searchPeriod)

            # search for the image
            try:
                location = pg.locateCenterOnScreen(imgPath, confidence=0.9)
            #stuff is buggy...
            except TypeError:
                continue
            except IndexError:
                continue

            # if it's not found, continue
            if location is None:
                continue

            # delay between seeing image and clicking it
            if preClickDelay != 0:
                print(f'Image found, {preClickDelay} seconds to touch an interface and abort.')
            sleep(preClickDelay)

            if not interfaceInUse:
                # get original mouse position
                origPos = mouse.position

                # get the correct click location, suspect
                # this need is related to the resolution on this mac
                x = location.x/coordinateFactor
                y = location.y/coordinateFactor

                # click the image twice, once to activate the window
                # another time to actually click the button if it is one
                pg.click(x, y)
                pg.click(x, y)

                # put mouse back to original location
                mouse.position = origPos

                # switch back to the previously active window
                with keyboard.pressed(Key.cmd):
                    keyboard.press(Key.tab)
                    sleep(0.18)
                    keyboard.release(Key.tab)

                # update counter and inform user what has occured
                counter += 1
                print(f'Clicked it {counter} times.')

                # sleep for a random amount of time between 5 and 10 sec
                sleepTime = uniform(postClickDelayMin,postClickDelayMax)
                print(f'Sleeping for {sleepTime} seconds.')
                sleep(sleepTime)
                print('Active and searching...')

            else:
                print('Click aborted.')

        # ^C to pause, then again to quit, or any key to resume
        except KeyboardInterrupt:
            try:
                input('\nPaused, press any key to continue, or ^C to quit.')
            except KeyboardInterrupt:
                break

    # stop listening to mouse and keyboard
    mouseListener.stop()
    keyboardListener.stop()

    # clear console
    with keyboard.pressed(Key.ctrl):
        keyboard.press('l')
        keyboard.release('l')

if __name__ == '__main__':
    main()
