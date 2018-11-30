

import Main
import Thread1
import Thread2
import UI
import Utilities

from decimal import *
import numpy

# - IMAGE PROCESSOR SETTINGS - #

#Developer Settings
DEVMODE = True #Option to run in developer mode. Displays all output and uses UI that allows user to change settings in runtime.

#Thread one process settings
TARGET_COLOR_LOW = numpy.array( [0,220,0] ) #low color bound (BGR)
TARGET_COLOR_HIGH = numpy.array( [0,255,0] ) #high color bound(BGR)
TARGET_NONZERO_PIXELS = 1500
THRESHOLD_LOW = 57
THRESHOLD_HIGH = 255

#Thread two process settings
TARGET_CONTOUR_AREA_MAX = 20000
TARGET_CONTOUR_AREA_MIN = 3000
TARGET_OBJECT_SOLIDITY_HIGH = Decimal(0.98)
TARGET_OBJECT_SOLIDITY_LOW = Decimal(0.65)
TARGET_OBJECT_CENTER_X = 200
TARGET_OBJECT_CENTER_Y = 200
TARGET_OBJECT_ASPECT_RATIO_HIGH = Decimal(1.25)
TARGET_OBJECT_ASPECT_RATIO_LOW = Decimal(0.65)
DEVIATION_MAX = 15 #amount in pixels the target can jump for the program to believe it

#UDP settings
UDP_IP = "10.39.65.100" #RobotRIO IP to send info to
UDP_PORT = 3695 #yee yee