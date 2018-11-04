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
#    --the big sad                    
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
WRITE_IMAGE = False #output image as file will mainly be used for script configuration


#Devmode utilities
Devwindow = None #window where settings can be edited
TitleLabel = None

#Proccess Settings

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
def startTimer():
    global TimerStartTime
    TimerStartTime = time.clock()

def endTimer():
    return (time.clock() - TimerStartTime)


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

            if DEVMODE:
                cv2.imshow("Take", Binary)
                cv2.waitKey(5)
            
            
            ret, Binary = cv2.threshold(Binary,THRESHOLD_LOW, THRESHOLD_HIGH ,cv2.THRESH_BINARY) #Threshold to increase image contrast            
            if DEVMODE:
                cv2.imshow("Threshold", Binary)
                cv2.waitKey(5)

            zeros = len(numpy.argwhere(Binary))
            if zeros > TARGET_NONZERO_PIXELS:
                #only continue if there is something in the image
                Binary = cv2.dilate(Binary, kernel, Binary) #dilate to close gaps
                
                if DEVMODE:
                    cv2.imshow("Dilate", Binary)
                    cv2.waitKey(5)

                if WRITE_IMAGE: 
                    cv2.imwrite("/home/pi/output.png", Binary) #writes to output.png in home menu

                Binary = cv2.inRange(Binary, TARGET_COLOR_LOW, TARGET_COLOR_HIGH) # convert to binary
                
                if DEVMODE:
                    cv2.imshow("Binary",Binary)
                    cv2.waitKey(5)
                
                #contouring stuff
                Binary, Contours, Hierarchy = cv2.findContours(Binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # get them contours

                if (DEVMODE) and (len(Contours) > 0):
                    ThreadOneOut = numpy.zeros((500,500),numpy.uint8) # reset the threadoneout image to nothing(again)
                    cv2.drawContours(ThreadOneOut, Contours, -1, (255, 255, 0),1) # draw the contours(they will appear white because the image is binary)
                
                #display image
                if DEVMODE:
                    cv2.imshow("Live", ThreadOneOut)
                    key = cv2.waitKey(5) #IMPORTANT: imshow() WILL NOT WORK WITHOUT THIS LINE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            
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
                    
                        
        else:
            time.sleep(0.1) # wait for thread 1 to do its magic

            ThreadTime = time.clock() - startTime
            ThreadTime *= 1000 #convert to milliseconds
            ThreadTwoTimes.append(ThreadTime)

        

#--- UTILITY METHODS ---#
def ChangeColor(): # changes the target color range of the program. Developer mode only
    #get color input
    color_high_string = raw_input("Enter color range setting: Input a BGR color with numbers separated by commas.  \r\nHigh Bound:")
    color_low_string  = raw_input("Low Bound:")
    #compute the color
    color_high_array = color_high_string.split(',')
    color_low_array = color_low_string.split(',')

    #set the target color range to input from user
    for i in range(0,3):
        TARGET_COLOR_HIGH[i] = int(color_high_array[i])
    
    for x in range(0,3):
        TARGET_COLOR_LOW[x] = int(color_low_array[x])

    #output results
    print("Values set.")
    print("Color High:" + str(TARGET_COLOR_HIGH))
    print("Color low:" + str(TARGET_COLOR_LOW))
    print("\r\n\r\n")

def ChangeThreshold(): #changes the threshold range of the thresholding function. Developer mode only
    global THRESHOLD_LOW
    global THRESHOLD_HIGH
    high = raw_input("Enter a threshold range setting: Input a number between 0 and 255.\r\nHigh Bound:")
    low  = raw_input("Low bound:")
    THRESHOLD_LOW = int(low)
    THRESHOLD_HIGH = int(high)
    #output results
    print("Values set.")
    print("High Threshold:" + str(THRESHOLD_HIGH))
    print("Low Threshold:" + str(THRESHOLD_LOW))
    print("\r\n\r\n")


def DispCurrentValues(): #displays all the current modifiable values.
    print(" --- CURRENT VALUES --- ")
    print("Color High Bound: " + str(TARGET_COLOR_HIGH))
    print("Color Low Bound: " + str(TARGET_COLOR_LOW))
    print("Threshold High Bound: " + str(THRESHOLD_HIGH))
    print("Threshold Low Bound: "+ str(THRESHOLD_LOW))
    print("Contour Area Max: " + str(TARGET_CONTOUR_AREA_MAX))
    print("Contour Area Min: " + str(TARGET_CONTOUR_AREA_MIN))
    print("Aspect Ratio Max: " + str(TARGET_CONTOUR_ASPECT_RATIO_MAX))
    print("Aspect Ratio Min: " + str(TARGET_CONTOUR_ASPECT_RATIO_MIN))
    print("\r\n\r\n")

def DispTime():
    #calculate some time stats

    # -- thread 1 -- #
    ThreadOneAvgTime = 0 # average time for frame to elapse
    ThreadOneMaxTime = 0 #the longest time for a frame to elapse
    ThreadOneMinTime = 10000 # I think ten seconds max is a nice bet
    for time in ThreadOneTimes:
        ThreadOneAvgTime += time

        if time > ThreadOneMaxTime:
            ThreadOneMaxTime = time

        if time < ThreadOneMinTime:
            ThreadOneMinTime = time

    ThreadOneAvgTime /= len(ThreadOneTimes)

    # -- Thread Two -- #
    ThreadTwoAvgTime = 0;
    ThreadTwoMaxTime = 0
    ThreadTwoMinTime = 10000
    for time in ThreadTwoTimes:
        ThreadTwoAvgTime += time

        if time > ThreadTwoMaxTime:
            ThreadTwoMaxTime = time

        if time < ThreadTwoMinTime:
            ThreadTwoMinTime = time

    ThreadTwoAvgTime /= len(ThreadTwoTimes)
    print(" --- THREAD TIMES --- ")
    print("   - Thread 1:-   ")
    print("Average Time: "+str(ThreadOneAvgTime) + " ms")
    print("Maximum Time: "+str(ThreadOneMaxTime) + " ms")
    print("Minimum Time: "+str(ThreadOneMinTime) + " ms")
    print("   - Thread 2: -   ")
    print("Average Time: "+str(ThreadTwoAvgTime) + " ms")
    print("Maximum Time: "+str(ThreadTwoMaxTime) + " ms")
    print("Minimum Time: "+str(ThreadTwoMinTime) + " ms")

    print("\r\n\r\n")


def ShowStream():
    while Stream.isOpened():
        img = numpy.copy(OriginalImage)
        if(BoxCenterX >= 0) and (BoxCenterY >= 0):
            contours = numpy.array( [[[BoxCenterX, BoxCenterY]]] )
            cv2.drawContours(img, contours, -1, (255, 255, 0),5) # draw the contours(they will appear white because the image is binary)
        cv2.imshow("stream", img)
        cv2.waitKey(5)
        time.sleep(0.1)

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
    while True:

        if DEVMODE: # enables a command line for changing settings and things

            #Work on a GUI later, but until we get entire program down, we stick with a command line
            
            #Im sorry for this speghetti code
            cmd = raw_input("Command:")
            if cmd == "c": # changes the target color of the program
                ChangeColor()
            elif cmd == "t": # changes the target threshold of the program
                ChangeThreshold()
            elif cmd == "current": # shows the current settings of the program
                DispCurrentValues()
            elif cmd == "time": # shows thread execution time information
                DispTime()
            elif cmd == "stream":
                ShowStream()
            elif cmd == "quit": # kills the program
                Kill()
            else:
                print("That command is unrecognized.")

        else: #NOT devmode
            time.sleep(0.5)
                


#starts the program and creates different threads and things for the things to run on.
def Vision():
    #start the stuff going
    if Stream.isOpened():
        #initialize the threads
        if DEVMODE:
            print("Initializing in Developer Mode.\r\n\r\n")
        else:
            print("Initializing in Running Mode.\r\n\r\n")

        global THREAD_1
        global THREAD_2
        
        THREAD_1 = thread.start_new_thread( Thread1, () )
        THREAD_2 = thread.start_new_thread( Thread2, () )
        time.sleep(0.25)
        Watch()
    else:
        print("WARNING: COULD NOT OPEN THE CAMERA")
        quit() #end program right then and there 

#main entry
if __name__ == '__main__': #MAIN ENTRY POINT RIGHT HERE
    try:
        Vision() #STARTS THE PROGARM!!
    except:
        Kill()
