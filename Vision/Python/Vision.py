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
#    4). convert to binary 
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
#    ____________________________________


from __future__ import division
import numpy
import cv2
import threading
import time
import Tkinter as tk
from decimal import *





#   --- CONSTANT VALUES ---   #


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


# --- UTILITIES -- #

#Devmode utilities
Devwindow = None #window where settings can be edited
TitleLabel = None

#global utilities
ProgramEnding = False

# --- ALL PROGRAM UTILITY VALUES --- # basically some values that arent settings that all threads might end up using
OriginalImage = None
TimerStartTime = 0


# --- THREAD 1 UTILITY VALUES --- #
Contours = None
ThreadOneTimes = []
Thread_One_Last_Loop_Time = 0 # last loop time so main thread can see if it has frozen or not
TargetImage = None
Thread1Message = "" # this string gets displayed on the UI every loop of the main thread

# --- THREAD 2 UTILITY VALUES --- #
BoxCenterX = -1
BoxCenterY = -1
ThreadTwoTimes = []
Thread_Two_Last_Loop_Time = 0 # main thread can see if it freezes or not
ImageHasContents = True # value that thread 1 sets to tell thread two if there was anything in the image or not. Only set to false if Thread 1 saw nothing in the image.
Thread2Message = "" # this string also gets displayed on the UI every loop of the main thread


#Process utilities
Stream = cv2.VideoCapture(0)
kernel = numpy.ones((5,5), numpy.float32)/25 #average the pixels to make the blur kernel

#Threads
THREAD_1 = None
THREAD_2 = None

 #for output window
Stream.set(cv2.CAP_PROP_FRAME_WIDTH, 500) #sets the image size 
Stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 500)

# --- TKINTER UI UTILITIES --- #
Master_Window = tk.Tk()
Slider_High_R = tk.Scale(Master_Window, from_=0, to=255, orient=tk.HORIZONTAL, length=500, label="Target High Red: ")
Slider_High_G = tk.Scale(Master_Window, from_=0, to=255, orient=tk.HORIZONTAL, length=500, label="Target High Green: ")
Slider_High_B = tk.Scale(Master_Window, from_=0, to=255, orient=tk.HORIZONTAL, length=500, label="Target High Blue: ")
Slider_Low_R = tk.Scale(Master_Window, from_=0, to=255, orient=tk.HORIZONTAL, length=500, label="Target Low Red: ")
Slider_Low_G = tk.Scale(Master_Window, from_=0, to=255, orient=tk.HORIZONTAL, length=500, label="Target Low Green: ")
Slider_Low_B = tk.Scale(Master_Window, from_=0, to=255, orient=tk.HORIZONTAL, length=500, label="Target Low Blue: ")
Slider_Threshold_Max = tk.Scale(Master_Window, from_=0, to=255, orient=tk.HORIZONTAL, length=500, label="Threshold Max: ")
Slider_Threshold_Value = tk.Scale(Master_Window, from_=0, to=255, orient=tk.HORIZONTAL, length=500, label="Threshold Value: ")
Slider_Nonzero_Pixels = tk.Scale(Master_Window, from_=0, to=5000, orient=tk.HORIZONTAL, length=500, label="Target Nonzero Pixels: ")
Slider_Area_Max = tk.Scale(Master_Window, from_=0, to=50000, orient=tk.HORIZONTAL, length=500, label="Target Area Maximum: ")
Slider_Area_Min = tk.Scale(Master_Window, from_=0, to=49999, orient=tk.HORIZONTAL, length=500, label="Target Area Minimum: ")
Slider_Solidity_High = tk.Scale(Master_Window, from_=0, to=100, orient=tk.HORIZONTAL, length=500, label="Target Solidity High:")
Slider_Solidity_Low = tk.Scale(Master_Window, from_=0, to=100, orient=tk.HORIZONTAL, length=500, label="Target Solidity Low:")

#Init the text objects
Running_Mode_Text = tk.StringVar(Master_Window)
Thread1_Time_Text = tk.StringVar(Master_Window)
Thread2_Time_Text = tk.StringVar(Master_Window)
UtilText1 = tk.StringVar(Master_Window)

#set the texts
Running_Mode_Text.set("\n\n\nRunning Mode: Developer")
Thread1_Time_Text.set("hecking time")
Thread2_Time_Text.set("hecking time")
UtilText1.set("") #Setting it to nothing because there is nothing to display currently

#now set the labels
Running_Mode_Label = tk.Label(Master_Window, textvariable=Running_Mode_Text, anchor=tk.W)
Thread1_Time_Label = tk.Label(Master_Window, textvariable=Thread1_Time_Text, anchor=tk.W)
Thread2_Time_Label = tk.Label(Master_Window, textvariable=Thread2_Time_Text, anchor=tk.W)
UtilLabel1 = tk.Label(Master_Window, textvariable=UtilText1, anchor=tk.W)


# --- THREAD UTILITY METHODS --- #

def DevmodeDisplayImage(window, image):
    #displays the current thread output image if the program is initalized in devmode. For the time being, should only be called by thread 1.
    if DEVMODE:
        cv2.imshow(window, image)
        cv2.waitKey(5)


# --- THREADS --- #

class Thread1(threading.Thread):
    stop = False

    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def terminate(self):
        self.stop = True
        print("Thread 1 attempting to terminate")
    

    def run(self):
        print("Thread 1 init")
        #Thread one stuff (algorithm steps 1-5)
        global ThreadOneTimes
        global Contours
        global OriginalImage
        global CenterPixelColor
        global TargetImage
        global Thread_One_Last_Loop_Time
        global ImageHasContents
        global Thread1Message
        
        Binary = None

        while (Stream.isOpened()):
            #execute a lot
            startTime = time.clock() # get start of loop in processor time

            returnVal, Binary = Stream.read()
            Binary = cv2.resize(Binary, (200,200)) #resize the image to make it smaller, faster

            if returnVal == True:

                # now some simple image processing
                OriginalImage = numpy.copy(Binary)
                #DevmodeDisplayImage("Take", Binary)
                ret, Binary = cv2.threshold(Binary,THRESHOLD_LOW, THRESHOLD_HIGH ,cv2.THRESH_BINARY) #Threshold to increase image contrast            
                #DevmodeDisplayImage("Threshold", Binary)
                zeros = len(numpy.argwhere(Binary))
                if zeros > TARGET_NONZERO_PIXELS:
                    #only continue if there is something in the image
                    TargetImage = cv2.dilate(Binary, kernel, Binary) #dilate to close gaps
                    #DevmodeDisplayImage("Dilate", Binary)
                    ImageHasContents = True

                else:
                    #nothing significant in image. In this case just tell thread 2 not to run
                    ImageHasContents = False
                
            else: # Stream was unable to get the camera data. Print a message.
                print("unable to get camera data!")

            #calculate loop time if devmode
            if self.stop:
                print("Thread 1 terminating")
                return
                
            ThreadTime = time.clock() - startTime
            ThreadTime *= 1000 #convert to milliseconds
            ThreadOneTimes.append(ThreadTime)
            Thread_One_Last_Loop_Time = time.clock()
            


class Thread2(threading.Thread):
    
    stop = False
    
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def terminate(self):
        self.stop = True
        print("Thread 2 attempting to terminate")


    def DevmodeShowContour(self, Area, Solidity, AspectRatio):
        global Thread2Message
        if DEVMODE:
            Thread2Message = "\nArea:          " + str(Area)
            Thread2Message += "\nSolidity:     " + str(Solidity)
            Thread2Message += "\nAspect Ratio: " + str(AspectRatio)
        

    def run(self):
        #Thread two stuff (algorithm steps 6-9)
        print("thread 2 init")

        global BoxCenterX
        global BoxCenterY
        global Thread_Two_Last_Loop_Time
        global Thread2Message

        #Test the contours to eliminate the ones that we dont want
        while Stream.isOpened():
            startTime = time.clock()

            Thread1Image = numpy.copy(TargetImage)
            zeros = len(numpy.argwhere(Thread1Image))
            if (zeros > TARGET_NONZERO_PIXELS) and (ImageHasContents): # only continue if there are actually contours in the thing. If ImageHasContents is false that means that thread 1 did not see anything in image
                #contouring stuff
                Thread1Image = cv2.inRange(Thread1Image, TARGET_COLOR_LOW, TARGET_COLOR_HIGH) # convert to binary
                #DevmodeDisplayImage("Binary", TargetImage)
                Thread1Image, Contours, Hierarchy = cv2.findContours(Thread1Image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # get them contours

##                if (DEVMODE) and (len(Contours) > 0): #it hecking slows the program down a lot tho D:<
##                    ThreadOneOut = numpy.zeros((500,500),numpy.uint8) # reset the threadoneout image to nothing(again)
##                    cv2.drawContours(ThreadOneOut, Contours, -1, (255, 255, 0),1) # draw the contours(they will appear white because the image is binary)
##                    DevmodeDisplayImage("Live", ThreadOneOut)
            
                if (Contours != None) and (len(Contours) > 0): # we do not want to run loop if there are no contours.
                    passed = 0 #the number of contours that have passed the test. needed to make sure values are set to -1 if none pass
                    lastBoxCenterX = BoxCenterX #these are for
                    lastBoxCenterY = BoxCenterY
                    
                    for contour in Contours:
                        Thread2Message = "" #reset the message so that we dont get big a lot of text
                        #get area & solidity
                        #area
                        Area = cv2.contourArea(contour)
                        x,y,w,h = cv2.boundingRect(contour)
                        
                        #getting solidity
                        BoxArea = w * h
                        Solidity = Area / BoxArea

                        #getting aspect ratio
                        AspectRatio = w/h

                        self.DevmodeShowContour(Area, Solidity, AspectRatio) # show the area and solidity data to the UI

                        Thread2Message += "\nTests Passed: "
                        #test the area & aspect ratio
                        if(Area < TARGET_CONTOUR_AREA_MAX) and (Area > TARGET_CONTOUR_AREA_MIN):
                            Thread2Message += "Area"
                            if(Solidity < TARGET_OBJECT_SOLIDITY_HIGH) and (Solidity > TARGET_OBJECT_SOLIDITY_LOW):
                                Thread2Message += ", Solidity"
                                if(AspectRatio < TARGET_OBJECT_ASPECT_RATIO_HIGH) and (AspectRatio > TARGET_OBJECT_ASPECT_RATIO_LOW):
                                    Thread2Message += ", Aspect Ratio"
                                    #get the center of the box
                                    w /= 2
                                    h /=2
                                    x += w
                                    y += h
                                    passed += 1
                                    #the deviation of each coordinate
                                    DeviateX = abs(int(x)) - BoxCenterX
                                    DeviateY = abs(int(y)) - BoxCenterY
                                    if(BoxCenterX == -1) or ((DeviateX < DEVIATION_MAX) and (DeviateY < DEVIATION_MAX)):
                                        BoxCenterX = int(x) #make sure they are ints or else we get an error drawing the points
                                        BoxCenterY = int(y)
                                        Thread2Message += "\nBox Center: (" + str(BoxCenterX) + ", " + str(BoxCenterY) + ")"
                            

                    if passed < 1: #no contours have passed
                        BoxCenterX = -1
                        BoxCenterY = -1

                    
                else: #After finding them contours, theres no contours. Set the coordinates to -1
                    BoxCenterX = -1
                    BoxCenterY = -1
            else: #There is nothing in the image. Since there wont be any contours lets just save us some time shall we?
                BoxCenterX = -1
                BoxCenterY = -1
                
            ThreadTime = time.clock() - startTime
            ThreadTime *= 1000 #convert to milliseconds
            ThreadTwoTimes.append(ThreadTime)
            Thread_Two_Last_Loop_Time = time.clock()

            if self.stop: #stops the loop and thread if the program is ending
                print("Thread 2 terminating")
                return
        


def DispCurrentValues(): #displays all the current modifiable values.
    print(" --- CURRENT VALUES --- ")
    print("Color High Bound:      " + str(TARGET_COLOR_HIGH))
    print("Color Low Bound:       " + str(TARGET_COLOR_LOW))
    print("Threshold High Bound:  " + str(THRESHOLD_HIGH))
    print("Threshold Low Bound:   " + str(THRESHOLD_LOW))
    print("Target nonzero pixels: " + str(TARGET_NONZERO_PIXELS))
    print("Contour Area Max:      " + str(TARGET_CONTOUR_AREA_MAX))
    print("Contour Area Min:      " + str(TARGET_CONTOUR_AREA_MIN))
    print("Solidity High:         " + str(TARGET_OBJECT_SOLIDITY_HIGH))
    print("Solidity Low:          " + str(TARGET_OBJECT_SOLIDITY_LOW))
    print("Aspect ratio high:     " + str(TARGET_OBJECT_ASPECT_RATIO_HIGH))
    print("Aspect ratio low:      " + str(TARGET_OBJECT_ASPECT_RATIO_LOW))
    print("\r\n\r\n")



# --- TIME CALCULATION METHODS --- #
#these should be pretty easy to follow... calculate a bunch of different times for the threads
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
    global ProgramEnding
    
    Stream.release()

    if DEVMODE: #print out some final settings if in devmode   
        DispCurrentValues()

    #kill the program family
    THREAD_1.terminate()
    THREAD_2.terminate()
    ProgramEnding = True
    time.sleep(2)
    cv2.destroyAllWindows()
    print("Thread 1 running: "+str(THREAD_1.is_alive()))
    print("Thread 2 running: "+str(THREAD_2.is_alive()))

    while(THREAD_1.is_alive()) or (THREAD_2.is_alive()):
        print ("Waiting for threads to terminate...")
        print("Thread 1 running: "+str(THREAD_1.is_alive()))
        print("Thread 2 running: "+str(THREAD_2.is_alive()))
        time.sleep(1)
    
    quit()


def UpdateUI():
    #method called from Watch() that updates the UI in the TKinter window.
    #import the global vars for mutation
    global TARGET_COLOR_HIGH
    global TARGET_COLOR_LOW
    global THRESHOLD_HIGH
    global THRESHOLD_LOW
    global TARGET_NONZERO_PIXELS
    global TARGET_CONTOUR_AREA_MAX
    global TARGET_CONTOUR_AREA_MIN
    global TARGET_OBJECT_SOLIDITY_HIGH
    global TARGEt_OBJECT_SOLIDITY_LOW

    global Thread1_Time_Text
    global Thread2_Time_Text
    global UtilText1

    #Update values in the master window
    Master_Window.update()
    #get all the values from the controls and put them into the process settings
    TARGET_COLOR_HIGH[2] = Slider_High_R.get()
    TARGET_COLOR_HIGH[1] = Slider_High_G.get()
    TARGET_COLOR_HIGH[0] = Slider_High_B.get()
    TARGET_COLOR_LOW[2] = Slider_Low_R.get()
    TARGET_COLOR_LOW[1] = Slider_Low_G.get()
    TARGET_COLOR_LOW[0] = Slider_Low_B.get()
    THRESHOLD_HIGH = Slider_Threshold_Max.get()
    THRESHOLD_LOW= Slider_Threshold_Value.get()
    TARGET_NONZERO_PIXELS = Slider_Nonzero_Pixels.get()
    TARGET_CONTOUR_AREA_MAX = Slider_Area_Max.get()
    TARGET_CONTOUR_AREA_MIN = Slider_Area_Min.get()
##    TARGET_OBJECT_SOLIDITY_HIGH = Slider_Solidity_High.get() / 100 #these ones must be divided by 100 since they are decimals shown as percentages
##    TARGET_OBJECT_SOLIDITY_LOW = Slider_Solidity_Low.get() / 100

    #update labels with some time and dev stats
    Thread1TimeStats = "System timer: " + str(time.clock()) + " Seconds\n\n--- THREAD 1 TIMES ---\n"
    Thread2TimeStats = "--- THREAD 2 TIMES ---\n"
    UtilTextOne = ""

    #calculate the times for the processes and put them into strings to be displayed in the window
    Thread1TimeStats += "Last Recorded loop: " + str(ThreadOneTimes[len(ThreadOneTimes) -1]) + "ms\n"
    Thread1TimeStats += " Average Loop Time: " + str(Thread1AverageTime()) + "ms\n"
    Thread1TimeStats += " Longest Loop Time: " + str(Thread1MaxTime()) + "ms\n"
    Thread1TimeStats += "Shortest Loop Time: " + str(Thread1MinTime()) + "ms\n\n"
    
    Thread2TimeStats += "Last Recorded loop: " + str(ThreadTwoTimes[len(ThreadTwoTimes) -1]) + "ms\n"
    Thread2TimeStats += " Average Loop Time: " + str(Thread2AverageTime()) + "ms\n"
    Thread2TimeStats += " Longest Loop Time: " + str(Thread2MaxTime()) + "ms\n"
    Thread2TimeStats += "Shortest Loop Time: " + str(Thread2MinTime()) + "ms\n\n"

    #Update the Utility Label based on some events and which mode the program is running in. 

    if not THREAD_1.is_alive():
        UtilTextOne += "\nWARNING: Thread 1 has stopped running!"

    if not THREAD_2.is_alive():
        UtilTextOne += "\nWARNING: Thread 2 has stopped running!"
    
    UtilTextOne += "recognized box center: (" + str(BoxCenterX) + ", " + str(BoxCenterY) + ")"
    
    #now set the labels
    Thread1_Time_Text.set(Thread1TimeStats)
    Thread2_Time_Text.set(Thread2TimeStats)
    UtilText1.set("Thread 1: "+ Thread1Message + "\nThread 2: " + Thread2Message + "\nMain: " + UtilTextOne) #Set the thread messages

#END METHOD


def UpdateOutputImage():
    #show output image with point drawn
    img = numpy.copy(OriginalImage) #copy the original image taken by thread 1
    if (BoxCenterX > -1) and (BoxCenterY > -1):
        cv2.drawContours(img, numpy.array( [[[BoxCenterX, BoxCenterY]]] ), -1, (255,255,0), 5) #draw the contour center point
        
    cv2.imshow("Output", img) # show the image in the window
    cv2.waitKey(5)
#END METHOD


def CheckThreadConditions():
    #checks to see if the threads are still running. If they are not for whatever reason, reinstantiate them.
    #some thread recovery stuff so that threads can be revived if they freeze, error out, etc
    global THREAD_1
    global THREAD_2
    global UtilText1
    
    LastResponse1 = time.clock() - Thread_One_Last_Loop_Time
    LastResponse2 = time.clock() - Thread_Two_Last_Loop_Time
    
    if ((not ProgramEnding) and (not THREAD_1.is_alive())) or (LastResponse1 > 1): #last response is in seconds btw
        #Thread 1 has been killed, errored out, or has frozen. Revive it.
        THREAD_1.terminate()
        time.sleep(0.1) # wait for thread to fully terminate
        THREAD_1 = Thread1(1, "Thread 1", 1) #create and start a new thread 1
        THREAD_1.start() # this one actually starts thread

        UtilTextOne = "MESSAGE: Thread 1 revived."
        UtilText1.set(UtilTextOne)

    if ((not ProgramEnding) and (not THREAD_2.is_alive())) or (LastResponse2 > 1):
        #same thing for thread2. if it errors out, revive it
        THREAD_2.terminate()
        time.sleep(0.1)
        THREAD_2 = Thread2(2, "Thread 2", 2)
        THREAD_2.start()

        UtilTextOne = "MESSAGE: Thread 2 revived."
        UtilText1.set(UtilTextOne)
#END METHOD


def Watch():
    #Watches over all threads and outputs displays if told to.
    #threads in case one of them errors out
    print("Waiting for threads to initalize")
    time.sleep(1.5) #give the threads a little more time to start
    print("Starting...")
    while True:

        if ProgramEnding: #but first lets check to see if the ending flag is up
                print("Vision man is going away now...")
                Master_Window.destroy() # say goodbye to settings and output window
                break #stop loop is the program ending flag is upif ProgramEnding: #but first lets check to see if the ending flag is up
    
        if DEVMODE: # grabs settings from the settings window and applies them

            # --- UPDATE UI --- #
            UpdateUI()

            # --- IMAGING --- #
            UpdateOutputImage()
            
        CheckThreadConditions()
        #send values to the RoboRIO here.

        
#END METHOD

# --- BUTTON EVENTS --- #
def QuitButtonClicked(): # kills the program
    print("Killing the program...")
    Kill()


#starts the program and creates different threads and things for the things to run on.
def Vision():
    #start the stuff going
    if Stream.isOpened():
        #initialize the threads
        if DEVMODE: #gives you the good stuff, but a bit harder on the CPU
            #first import the global tkinter utilities
            global Master_Window
            global Slider_High_R
            global Slider_High_G
            global Slider_High_B

            global Slider_Low_R
            global Slider_Low_G
            global Slider_Low_B

            global Slider_Threshold_Max
            global Slider_Threshold_Value
            global Slider_Nonzero_Pixels
            global Slider_Area_Max
            global Slider_Area_Min
            global Slider_Solidity_High
            global Slider_Solidity_Low

            global Running_Mode_Label
            global Thread1_Time_Label
            global Thread2_Time_Label
            global UtilLabel1
            
            global Running_Mode_Text
            global Thread1_Time_Text
            global Thread2_Time_Text
            global UtilText1
            
            print("Initializing in Developer Mode.\r\n\r\n")
            #tkinter!!!

            #--- set and grid the UI elements --- #

            Slider_High_R.set(TARGET_COLOR_HIGH[2])
            Slider_High_G.set(TARGET_COLOR_HIGH[1])
            Slider_High_B.set(TARGET_COLOR_HIGH[0])
            Slider_Low_R.set(TARGET_COLOR_LOW[2])
            Slider_Low_G.set(TARGET_COLOR_LOW[1])
            Slider_Low_B.set(TARGET_COLOR_LOW[0])
            Slider_Threshold_Max.set(THRESHOLD_HIGH)
            Slider_Threshold_Value.set(THRESHOLD_LOW)
            Slider_Nonzero_Pixels.set(TARGET_NONZERO_PIXELS)
            Slider_Area_Max.set(TARGET_CONTOUR_AREA_MAX)
            Slider_Area_Min.set(TARGET_CONTOUR_AREA_MIN)
            Slider_Solidity_High.set(TARGET_OBJECT_SOLIDITY_HIGH * 100) #multiply by 100 to get percentages instead of decimals
            Slider_Solidity_Low.set(TARGET_OBJECT_SOLIDITY_LOW * 100)
            #now pack all the new sliders and things into the window to be displayed
            Slider_High_R.grid(row=0, column=0)
            Slider_High_G.grid(row=1, column=0)
            Slider_High_B.grid(row=2, column=0)
            Slider_Low_R.grid(row=3,column=0)
            Slider_Low_G.grid(row=4,column=0)
            Slider_Low_B.grid(row=5, column=0)
            Slider_Threshold_Max.grid(row=6, column=0)
            Slider_Threshold_Value.grid(row=7, column=0)
            Slider_Nonzero_Pixels.grid(row=8, column=0)
            Slider_Area_Max.grid(row=9, column=0)
            Slider_Area_Min.grid(row=10, column=0)
            Slider_Solidity_High.grid(row=11, column=0)
            Slider_Solidity_Low.grid(row=12,column=0)
            tk.Button(Master_Window, text="Kill Program", width=50, command=QuitButtonClicked).grid(row=8, column=1)

            #grid the labels and things
            #pack the labels
            Running_Mode_Label.grid(row=0, column=1)
            Thread1_Time_Label.grid(row=2, column=1)
            Thread2_Time_Label.grid(row=4, column=1)
            UtilLabel1.grid(row=6, column=1)
                  
        else:
            print("Initializing in Running Mode.\r\n\r\n") #runner mode is lighter on CPU but does not give you any feedback whatsoever (it just gives you the center box point)

        global THREAD_1
        global THREAD_2

        print("Hello. I am the vision man.")
        print("Making Threads")
        THREAD_1 = Thread1(1, "Thread 1", 1) # creates and starts new thread running Thread1(), to take and process the images
        THREAD_2 = Thread2(2, "Thread 2", 2) # creates and starts new thread running Thread2(), to process contours and come up with a center point

        print("Starting Threads")
        #start the threads
        THREAD_1.start()
        THREAD_2.start()

        print("Starting watch loop")
        Watch() #starts master loop
    else:
        print("WARNING: COULD NOT OPEN THE CAMERA")
        quit() #end program right then and there 

#main entry
if __name__ == '__main__': #MAIN ENTRY POINT RIGHT HERE
    try:
        Vision() #STARTS THE PROGARM!!
    except KeyboardInterrupt:
        Kill() #displays set values and quits
