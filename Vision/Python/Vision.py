###############################################
#                                             #
#          VISION PROCESSING!!!!              #
#    Program to do some intense vision        #
#    processing by Brach Knutson.             #
#    __________________________________       #
#    Algorithm:                               #
#    1). Get image                            #
#    2). Blur(although might not be needed)   #
#    3). Convert to HSV                       #
#    4). Using constant color, convert to bin #
#    5). Find contours                        #
#    6). run aspect ratio test on contours    #
#    7). run intensity test on contours       #
#    8). Take remaining contour and figure    #
#         out where to aim the shooter        #
#    9). Send values to other program to send #
#         to roboRIO                          #
#    ____________________________________     #
#    OTHER REMARKS:                           #
#    --yeet    the big sad                    #
#    ____________________________________     #
###############################################

import numpy
import cv2
import thread
import time

#first things first, lets set up some V4L2 stuff (gotta live me some video 4 linux 2)


#   --- CONSTANT VALUES ---   #

#Process utilities
Pipeline = "v4l2src device=dev/video0 extra-controls=\"c,exposure_auto=1, exposure_absolute=500\" ! "
Pipeline += "video/x-raw, format=BGR, framerate=30/1, width=(int)1280,height=(int)720 ! "
Pipeline += "appsink"

Stream = cv2.VideoCapture(0)
kernel = numpy.ones((5,5), numpy.float32)/25 #average the pixels to make the blur kernel

 #for output window

cv2.namedWindow("Live");
Stream.set(cv2.CAP_PROP_FRAME_WIDTH, 500)
Stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 500)
Stream.set(cv2.CAP_PROP_BRIGHTNESS, 100)
#Stream.set(cv2.CAP_PROP_SATURATION, 50) not supported


# - IMAGE PROCESSOR SETTINGS - #

#Output Settings
DISPLAY_IMAGE_OUTPUT = True #Option to display the image output for each step of the process
WRITE_IMAGE = False #output image as file will mainly be used for script configuration

#Proccess Settings
TARGET_COLOR_LOW = numpy.array( [230,0,0] ) #low color bound (BGR)
TARGET_COLOR_HIGH = numpy.array( [255,0,0] ) #high color bound(BGR)

# --- THREAD 1 UTILITY VALUES --- #
ThreadOneOut = numpy.zeros((500,500), numpy.uint8) # thread 1 output image (as cv2 Mat (but actually as numpy array))

def Thread1():
    print("Thread 1 init")
    #Thread one stuff (algorithm steps 1-5)

    Binary = None
    Contours = None
    while (Stream.isOpened()):
        #execute a lot


        
        returnVal, Binary = Stream.read()
        if returnVal == True:

            # --- now some simple image processing ---
            #thresholding

            if DISPLAY_IMAGE_OUTPUT:
                cv2.imshow("Take", Binary)
                cv2.waitKey(5)
            
            ret, Binary = cv2.threshold(Binary, 150,255 ,cv2.THRESH_BINARY) #Threshold to increase image contrast

            if DISPLAY_IMAGE_OUTPUT:
                cv2.imshow("Threshold", Binary)
                cv2.waitKey(5)
            
            Binary = cv2.dilate(Binary, kernel, Binary) #dilate to close gaps

            if DISPLAY_IMAGE_OUTPUT:
                cv2.imshow("Dilate", Binary)
                cv2.waitKey(5)

            if WRITE_IMAGE: 
                cv2.imwrite("/home/pi/output.png", Binary) #writes to output.png in home menu

            Binary = cv2.inRange(Binary, TARGET_COLOR_LOW, TARGET_COLOR_HIGH) # convert to binary

            if DISPLAY_IMAGE_OUTPUT:
                cv2.imshow("Binary",Binary)
                cv2.waitKey(5)
            
            #contouring stuff
            ThreadOneOut = numpy.zeros((500,500),numpy.uint8) # reset the threadoneout image to nothing(again)
            Binary, Contours, Hierarchy = cv2.findContours(Binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # get them contours
            cv2.drawContours(ThreadOneOut, Contours, -1, (255, 255, 0),3) # draw the contours(they will appear white because the image is binary)

            
            #display image
            if DISPLAY_IMAGE_OUTPUT:
                cv2.imshow("Live", ThreadOneOut)
                key = cv2.waitKey(5) #IMPORTANT: imshow() WILL NOT WORK WITHOUT THIS LINE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


            
            
        else:
            print("unable to get camera data!")

def Thread2():
    #Thread two stuff (algorithm steps 6-9)
    print("thread 2 init")
    #Thread two doesn't do much yet...


def Watch():
    #Watches over all threads and outputs displays if told to.
    print("yeet")
    while True:
        # do nothing (will change soon)
        time.sleep(1)


#starts the program and creates different threads and things for the things to run on.
def Vision():
    #start the stuff going
    if Stream.isOpened():
        thread.start_new_thread( Thread1, () )
        thread.start_new_thread( Thread2, () )
        Watch()
    else:
        print("WARNING: COULD NOT OPEN THE CAMERA")
        quit() #end program right then and there 

#main entry
if __name__ == '__main__':
    try:
        Vision() #STARTS THE PROGARM!!
    except:
        Stream.release()
        cv2.destroyAllWindows()
        quit()
