

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
TARGET_NONZERO_PIXELS = 1500 #amount of non-zero pixels that need to be in the image for processing to continue. Simply to save time
THRESHOLD_LOW = 57 # Threshold value to go by, defines how strict the thesholding function has to be
THRESHOLD_HIGH = 255 # leave this here. Trust me.

#Thread two process settings
TARGET_CONTOUR_AREA_MAX = 20000 #maximum area of the target contour
TARGET_CONTOUR_AREA_MIN = 3000 #minimum area of the target contour
TARGET_OBJECT_SOLIDITY_HIGH = Decimal(0.98) #The solidity of the object (solidity = bounding-box-area / contour-area)
TARGET_OBJECT_SOLIDITY_LOW = Decimal(0.65) #low solidity 
TARGET_OBJECT_CENTER_X = 200 #default center for deviation
TARGET_OBJECT_CENTER_Y = 200 # also
TARGET_OBJECT_ASPECT_RATIO_HIGH = Decimal(1.25) # high aspect ratio of the target contour
TARGET_OBJECT_ASPECT_RATIO_LOW = Decimal(0.65) #low aspect ratio of the target contour
DEVIATION_MAX = 15 #amount in pixels the target can jump for the program to believe it

#UDP settings
UDP_IP = "10.36.95.100" #RobotRIO IP to send info to
UDP_PORT = 3695 #yee yee
