###############################################
#    _____________________________________    #
#                                             #
#          VISION PROCESSING!!!!              #
#    Program to do some intense vision        #
#    processing by Brach Knutson.             #
#    _____________________________________    #
#                                             #
###############################################


#    __________________________________       
#    Algorithm:                               
#    1). Get image                          
#    2). Threshold image                      
#    3). Dilate image
#    4). convert to bin 
#    5). Find contours                        
#    6). run area test on contours    
#    7). run aspect ratio test on contours
#    8). get center point of remaining contour (if it exists)
#    9). Send values to other program to send 
#         to roboRIO (if #8 runs)
#
#
#    ____________________________________     
#    OTHER REMARKS:                           
#    --its gui time
#    --also this program is hit or miss on whether it inits correctly right now
#    ____________________________________


import numpy
import cv2
import thread
import time




#   --- CONSTANT VALUES ---   #

#Process utilities
Stream = cv2.VideoCapture(0)
kernel = numpy.ones((5,5), numpy.float32)/25 #average the pixels to make the blur kernel

#Threads
THREAD_1 = None
THREAD_2 = None

 #for output window
Stream.set(cv2.CAP_PROP_FRAME_WIDTH, 500) #sets the image size 
Stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 500)


# - IMAGE PROCESSOR SETTINGS - #

#Developer Settings
DEVMODE = True #Option to run in developer mode. Displays all output and allows for main thread to process commands. More in README.

#Devmode utilities
Devwindow = None #window where settings can be edited
TitleLabel = None


#Thread one process settings
TARGET_COLOR_LOW = numpy.array( [0,250,0] ) #low color bound (BGR)
TARGET_COLOR_HIGH = numpy.array( [0,255,0] ) #high color bound(BGR)
TARGET_NONZERO_PIXELS = 1500
THRESHOLD_LOW = 28
THRESHOLD_HIGH = 255

#Thread two process settings
TARGET_CONTOUR_AREA_MAX = 12000
TARGET_CONTOUR_AREA_MIN = 3000
TARGET_CONTOUR_ASPECT_RATIO_MAX = 1.25
TARGET_CONTOUR_ASPECT_RATIO_MIN = 0.75

# --- ALL PROGRAM UTILITY VALUES --- # basically some values that arent settings that all threads might end up using
OriginalImage = None
TimerStartTime = 0


# --- THREAD 1 UTILITY VALUES --- #
Contours = None
ThreadOneTimes = []

# --- THREAD 2 UTILITY VALUES --- #
BoxCenterX = -1
BoxCenterY = -1
ThreadTwoTimes = []


# --- THREAD UTILITY METHODS --- #

#a timer to make easy work of timing a process. Cannot have multiple timers at once

def DevmodeDisplayImage(window, image):
    #displays the current thread output image if the program is initalized in devmode. For the time being, should only be called by thread 1.
    if DEVMODE:
        cv2.imshow(window, image)
        cv2.waitKey(5)
        


# --- THREADS --- #

def Thread1():
    print("Thread 1 init")
    #Thread one stuff (algorithm steps 1-5)
    global ThreadOneTimes
    global Contours
    global OriginalImage
    
    Binary = None

    while (Stream.isOpened()):
        #execute a lot
        startTime = time.clock() # get start of loop in processor time

        returnVal, Binary = Stream.read()        
        if returnVal == True:

            # --- now some simple image processing ---
            #thresholding

            OriginalImage = numpy.copy(Binary)
            DevmodeDisplayImage("Take", Binary)
            
            ret, Binary = cv2.threshold(Binary,THRESHOLD_LOW, THRESHOLD_HIGH ,cv2.THRESH_BINARY) #Threshold to increase image contrast            
            DevmodeDisplayImage("Threshold", Binary)

            zeros = len(numpy.argwhere(Binary))
            if zeros > TARGET_NONZERO_PIXELS:
                #only continue if there is something in the image
                Binary = cv2.dilate(Binary, kernel, Binary) #dilate to close gaps
                DevmodeDisplayImage("Dilate", Binary)

                Binary = cv2.inRange(Binary, TARGET_COLOR_LOW, TARGET_COLOR_HIGH) # convert to binary
                DevmodeDisplayImage("Binary", Binary)

                zeros = len(numpy.argwhere(Binary))
                if zeros > TARGET_NONZERO_PIXELS:
                    #contouring stuff
                    Binary, Contours, Hierarchy = cv2.findContours(Binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # get them contours

                    if (DEVMODE) and (len(Contours) > 0):
                        ThreadOneOut = numpy.zeros((500,500),numpy.uint8) # reset the threadoneout image to nothing(again)
                        cv2.drawContours(ThreadOneOut, Contours, -1, (255, 255, 0),1) # draw the contours(they will appear white because the image is binary)
                        DevmodeDisplayImage("Live", ThreadOneOut)

            else:
                #nothing significant in image. Update the box center to (-1, -1) to indicate it
                BoxCenterX = -1
                BoxCenterY = -1
            
        else:
            print("unable to get camera data!")

        #calculate loop time if devmode
        if DEVMODE: 
            ThreadTime = time.clock() - startTime
            ThreadTime *= 1000 #convert to milliseconds
            ThreadOneTimes.append(ThreadTime)

        

def Thread2():
    #Thread two stuff (algorithm steps 6-9)
    print("thread 2 init")

    global BoxCenterX
    global BoxCenterY
    #Test the contours to eliminate the ones that we dont want
    while Stream.isOpened():
        startTime = time.clock()
        x,y,w,h = 0,0,0,0
        if Contours != None:
            localContours = numpy.copy(Contours)
            for contour in localContours:
                #get area & aspect ratio
                Area = cv2.contourArea(contour)
                x,y,w,h = cv2.boundingRect(contour)
                AspectRatio = w/h

                #test the area & aspect ratio
                if not((Area > TARGET_CONTOUR_AREA_MIN) and (Area < TARGET_CONTOUR_AREA_MAX) and (Area > TARGET_CONTOUR_ASPECT_RATIO_MIN) and (Area < TARGET_CONTOUR_ASPECT_RATIO_MAX)):
                    #if it does not pass it is removed from the array
                    localContours = numpy.delete(localContours, contour, axis=0)
            #after for loop, calculate the center of the bounding box, if it is not empty
            if(len(localContours) > 0):
                if len(localContours) == 1:
                    #calculate the center of the bounding box
                    w /= 2 #the center width
                    h /= 2 #the center height
                    BoxCenterX = w + x
                    BoxCenterY = h + y
            else:
                BoxCenterX = -1 # target not found
                BoxCenterY = -1
                    
                        
        time.sleep(0.1) # wait for thread 1 to do its magic

        ThreadTime = time.clock() - startTime
        ThreadTime *= 1000 #convert to milliseconds
        ThreadTwoTimes.append(ThreadTime)
    


def DispCurrentValues(): #displays all the current modifiable values.
    print(" --- CURRENT VALUES --- ")
    print("Color High Bound: " + str(TARGET_COLOR_HIGH))
    print("Color Low Bound: " + str(TARGET_COLOR_LOW))
    print("Threshold High Bound: " + str(THRESHOLD_HIGH))
    print("Threshold Low Bound: "+ str(THRESHOLD_LOW))
    print("Target nonzero pixels: " + str(TARGET_NONZERO_PIXELS))
    print("Contour Area Max: " + str(TARGET_CONTOUR_AREA_MAX))
    print("Contour Area Min: " + str(TARGET_CONTOUR_AREA_MIN))
    print("Aspect Ratio Max: " + str(TARGET_CONTOUR_ASPECT_RATIO_MAX))
    print("Aspect Ratio Min: " + str(TARGET_CONTOUR_ASPECT_RATIO_MIN))
    print("\r\n\r\n")



# --- TIME CALCULATION METHODS --- #
def Thread1AverageTime():
    avg = 0
    for time in ThreadOneTimes:
        avg += time

    avg /= len(ThreadOneTimes)
    return avg
    

def Thread1MaxTime():
    maximum = 0
    for time in ThreadOneTimes:
        if time > maximum:
            maximum = time

    return maximum

def Thread1MinTime():
    minimum = 10000 # I think 10 seconds tops is a generous max
    for time in ThreadOneTimes:
        if time < minimum:
            minimum = time

    return minimum

def Thread2AverageTime():
    avg = 0
    for time in ThreadTwoTimes:
        avg += time

    avg /= len(ThreadTwoTimes)
    return avg

def Thread2MaxTime():
    maximum = 0
    for time in ThreadTwoTimes:
        if time > maximum:
            maximum = time

    return maximum

def Thread2MinTime():
    minimum = 10000
    for time in ThreadTwoTimes:
        if time < minimum:
            minimum = time

    return minimum


# --- UTILITY METHODS --- #

def Kill():
    #releases some resources and stops the program
    Stream.release()
    cv2.destroyAllWindows()

    if DEVMODE: #print out some final settings if in devmode   
        DispCurrentValues()

    #kill the program family
    quit()

def Watch():
    #Watches over all threads and outputs displays if told to.
    print("Starting...")

    #import global settings into method
    global TARGET_COLOR_HIGH
    global THRESHOLD_HIGH
    global THRESHOLD_LOW
    global TARGET_NONZERO_PIXELS
    global TARGET_CONTOUR_AREA_MAX
    global TARGET_CONTOUR_AREA_MIN
    global TARGET_CONTOUR_ASPECT_RATIO_MAX
    global TARGET_CONTOUR_ASPECT_RATIO_MIN
    time.sleep(2) #give the threads a little time to start
    while True:

        if DEVMODE: # grabs settings from the settings window and applies them
            #first lets calculate some time stats
            #prepare dashboard image to display information ( if only overlay works ): )
            dashboard = numpy.zeros((300,500), numpy.uint8)

            #O HECK YES ITS TIME TO PUT TOGETHER THE TIMETABLE!!!!!
            
            #time for thread 1 loop times
            cv2.putText(dashboard, "--- TIME ---", (0,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
            cv2.putText(dashboard, "Thread 1 latest loop time: ", (0,40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
            cv2.putText(dashboard, str(ThreadOneTimes[len(ThreadOneTimes) - 1]), (300,40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150,255,150)) # welp, its supposed to be green...
            cv2.putText(dashboard, "Thread 1 average loop time: ", (0,60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
            cv2.putText(dashboard, str(Thread1AverageTime()), (300,60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150,255,150)) # welp, its supposed to be green...
            cv2.putText(dashboard, "Thread 1 largest loop time: ", (0,80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
            cv2.putText(dashboard, str(Thread1MaxTime()), (300,80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150,255,150)) # welp, its supposed to be green...
            cv2.putText(dashboard, "Thread 1 smallest loop time: ", (0,100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
            cv2.putText(dashboard, str(Thread1MinTime()), (300,100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150,255,150)) # welp, its supposed to be green...

            #Thread 2 loop times
            cv2.putText(dashboard, "Thread 2 latest loop time: ", (0,140), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
            cv2.putText(dashboard, str(ThreadOneTimes[len(ThreadTwoTimes) - 1]), (300,140), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150,255,150)) # welp, its supposed to be green...
            cv2.putText(dashboard, "Thread 2 average loop time: ", (0,160), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
            cv2.putText(dashboard, str(Thread2AverageTime()), (300,160), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150,255,150)) # welp, its supposed to be green...
            cv2.putText(dashboard, "Thread 2 largest loop time: ", (0,180), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
            cv2.putText(dashboard, str(Thread2MaxTime()), (300,180), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150,255,150)) # welp, its supposed to be green...
            cv2.putText(dashboard, "Thread 2 smallest loop time: ", (0,200), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
            cv2.putText(dashboard, str(Thread2MinTime()), (300,200), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150,255,150)) # welp, its supposed to be green...

            #show the stream with the dot drawn if target is found
            img = numpy.copy(OriginalImage)
            if(BoxCenterX >= 0) and (BoxCenterY >= 0):
                contours = numpy.array( [[[BoxCenterX, BoxCenterY]]] ) #artifically make the contours because circle function started flexing on me
                cv2.drawContours(img, contours, -1, (255, 255, 0),5) # draws the contours onto the image
                
            #get the trackbar positions and assign them to their respective settings
            TARGET_COLOR_HIGH[2] = cv2.getTrackbarPos("Target High Red", "Settings")
            TARGET_COLOR_HIGH[1] = cv2.getTrackbarPos("Target High Green", "Settings")
            TARGET_COLOR_HIGH[0] = cv2.getTrackbarPos("Target High Blue", "Settings")
            TARGET_COLOR_LOW[2] = cv2.getTrackbarPos("Target Low Red", "Settings")
            TARGET_COLOR_LOW[1] = cv2.getTrackbarPos("Target Low Green", "Settings")
            TARGET_COLOR_LOW[0] = cv2.getTrackbarPos("Target Low Blue", "Settings")
            THRESHOLD_HIGH = cv2.getTrackbarPos("Target Threshold Max", "Settings")
            THRESHOLD_LOW = cv2.getTrackbarPos("Target Threshold Value", "Settings")
            TARGET_NONZERO_PIXELS = cv2.getTrackbarPos("Target Nonzero pixels", "Settings")
            TARGET_CONTOUR_AREA_MAX = cv2.getTrackbarPos("Target Area Max", "Settings")
            TARGET_CONTOUR_AREA_MIN = cv2.getTrackbarPos("Target Area Min", "Settings")
            
            cv2.imshow("Settings", dashboard)
            cv2.imshow("Output", img)
            cv2.waitKey(5)
            time.sleep(0.5)
                        
        else: #NOT devmode
            time.sleep(0.5)
                

def DoNothing(x): pass #heckin nothing. This is the method called when trackbars are changed.

#starts the program and creates different threads and things for the things to run on.
def Vision():
    #start the stuff going
    if Stream.isOpened():
        #initialize the threads
        if DEVMODE: #gives you the good stuff, but a bit harder on the CPU
            print("Initializing in Developer Mode.\r\n\r\n")
            #we really using the OpenCV GUI for this one

            #First initialize the windows with coordinates so that we don't spit out random windows and make it hard to look at
            cv2.namedWindow("Take")
            cv2.namedWindow("Threshold")
            cv2.namedWindow("Dilate")
            cv2.namedWindow("Binary")
            cv2.namedWindow("Live")
            cv2.namedWindow("Output")

            #position windows
            cv2.moveWindow("Take", 450, 0)
            cv2.moveWindow("Threshold", 850, 0)
            cv2.moveWindow("Dilate", 1250,0)
            cv2.moveWindow("Binary", 450, 450)
            cv2.moveWindow("Live", 850, 450)
            cv2.moveWindow("Output", 1250, 450)
            
            cv2.namedWindow("Settings", cv2.WINDOW_NORMAL) #init the gui window
            cv2.moveWindow("Settings", 0,0)
            cv2.resizeWindow("Settings", 400,1000)
            #create the trackbars (Im sorry I dont know how to resize them xDDD)
            cv2.createTrackbar("Target High Red", "Settings", TARGET_COLOR_HIGH[2], 255, DoNothing)
            cv2.createTrackbar("Target High Green", "Settings", TARGET_COLOR_HIGH[1], 255, DoNothing)
            cv2.createTrackbar("Target High Blue", "Settings", TARGET_COLOR_HIGH[0], 255, DoNothing)
            cv2.createTrackbar("Target Low Red", "Settings", TARGET_COLOR_LOW[2], 255, DoNothing)
            cv2.createTrackbar("Target Low Green", "Settings", TARGET_COLOR_LOW[1], 255, DoNothing)
            cv2.createTrackbar("Target Low Blue", "Settings", TARGET_COLOR_LOW[0], 255, DoNothing)
            cv2.createTrackbar("Target Threshold Max", "Settings", THRESHOLD_HIGH, 255, DoNothing)
            cv2.createTrackbar("Target Threshold Value", "Settings", THRESHOLD_LOW, 255, DoNothing)
            cv2.createTrackbar("Target Nonzero pixels", "Settings", TARGET_NONZERO_PIXELS, 5000, DoNothing)
            cv2.createTrackbar("Target Area Max", "Settings", TARGET_CONTOUR_AREA_MAX, 50000, DoNothing)
            cv2.createTrackbar("Target Area Min", "Settings", TARGET_CONTOUR_AREA_MIN, 49999, DoNothing)
                  
        else:
            print("Initializing in Running Mode.\r\n\r\n") #runner mode is lighter on CPU but does not give you basically any feedback whatsoever (it just gives you the center box point)

        global THREAD_1
        global THREAD_2

        print("little hellO")
        THREAD_1 = thread.start_new_thread( Thread1, () )
        THREAD_2 = thread.start_new_thread( Thread2, () )
        time.sleep(0.25)
        Watch()
    else:
        print("WARNING: COULD NOT OPEN THE CAMERA")
        quit() #end program right then and there 

#main entry
if __name__ == '__main__': #MAIN ENTRY POINT RIGHT HERE
    #try:
        Vision() #STARTS THE PROGARM!!
    #except:
        #Kill() #displays set values and quits
