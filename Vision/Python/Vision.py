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
#    3).              #
#    4). Using constant color, convert to bin 
#    5). Find contours                        
#    6). run aspect ratio test on contours    
#    7). run intensity test on contours       
#    8). Take remaining contour and figure    
#         out where to aim the shooter        
#    9). Send values to other program to send 
#         to roboRIO
#
#
#    ____________________________________     
#    OTHER REMARKS:                           
#    --yeet    the big sad                    
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
TARGET_COLOR_LOW = numpy.array( [0,250,0] ) #low color bound (BGR)
TARGET_COLOR_HIGH = numpy.array( [0,255,0] ) #high color bound(BGR)

THRESHOLD_LOW = 35
THRESHOLD_HIGH = 255


# --- THREAD 1 UTILITY VALUES --- #
ThreadOneOut = numpy.zeros((500,500), numpy.uint8) # thread 1 output image (as cv2 Mat (but actually as numpy array))
ThreadOneTimes = []

def Thread1():
    print("Thread 1 init")
    #Thread one stuff (algorithm steps 1-5)
    global ThreadOneTimes
    global ThreadOneOut

    Binary = None
    Contours = None
    while (Stream.isOpened()):
        #execute a lot
        startTime = time.clock()
        
        returnVal, Binary = Stream.read()

        if returnVal == True:

            # --- now some simple image processing ---
            #thresholding

            if DEVMODE:
                cv2.imshow("Take", Binary)
                cv2.waitKey(5)
            
            ret, Binary = cv2.threshold(Binary,THRESHOLD_LOW, THRESHOLD_HIGH ,cv2.THRESH_BINARY) #Threshold to increase image contrast

            if DEVMODE:
                cv2.imshow("Threshold", Binary)
                cv2.waitKey(5)
            
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
            ThreadOneOut = numpy.zeros((500,500),numpy.uint8) # reset the threadoneout image to nothing(again)
            Binary, Contours, Hierarchy = cv2.findContours(Binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # get them contours
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
            ThreadTime /= 1000 #convert to milliseconds
            ThreadOneTimes.append(ThreadTime)

        

def Thread2():
    #Thread two stuff (algorithm steps 6-9)
    print("thread 2 init")
    #Thread two doesn't do much yet...




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
    print("Color High:")
    print(TARGET_COLOR_HIGH)
    print("Color low:")
    print(TARGET_COLOR_LOW)
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
    print("High Threshold:")
    print(THRESHOLD_HIGH)
    print("Low Threshold:")
    print(THRESHOLD_LOW)
    print("\r\n\r\n")


def DispCurrentValues(): #displays all the current modifiable values.
    print(" --- CURRENT VALUES --- ")
    print("Color High Bound:")
    print(TARGET_COLOR_HIGH)
    print("Color Low Bound:")
    print(TARGET_COLOR_LOW)
    print("Threshold High Bound:")
    print(THRESHOLD_HIGH)
    print("Threshold Low Bound:")
    print(THRESHOLD_LOW)
    print("\r\n\r\n")

def DispTime():
    #calculate some time stats
    ThreadOneAvgTime = 0 # average time for frame to elapse
    ThreadOneMaxTime = 0 #the longest time for a frame to elapse
    ThreadOneMinTime = 10000 # I think ten seconds max is a nice bet
    for i in ThreadOneTimes:
        ThreadOneAvgTime += i

        if i > ThreadOneMaxTime:
            ThreadOneMaxTime = i

        if i < ThreadOneMinTime:
            ThreadOneMinTime = i

    ThreadOneAvgTime /= len(ThreadOneTimes)
    
    print(" --- THREAD TIMES --- ")
    print("   - Thread 1:    -   ")
    print("Average Time: "+str(ThreadOneAvgTime) + " ms")
    print("Maximum Time: "+str(ThreadOneMaxTime) + " ms")
    print("Minimum Time: "+str(ThreadOneMinTime) + " ms")

    print("\r\n\r\n")

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
            elif cmd == "quit": # kills the program
                Kill()
            else:
                print("That command is unrecognized.")
                


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
if __name__ == '__main__':
    try:
        Vision() #STARTS THE PROGARM!!
    except:
        Kill()
