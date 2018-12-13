
import Settings
import Thread1
import Thread2
import Main


import socket
import cv2
import numpy
import time

# --- UTILITIES -- #
#Devmode utilities
Devwindow = None #window where settings can be edited
TitleLabel = None

#global utilities
ProgramEnding = False

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

# --- ALL PROGRAM UTILITY VALUES --- # basically some values that arent settings that all threads might end up using
BoxCenterX = -1
BoxCenterY = -1
OriginalImage = None
TimerStartTime = 0

# --- MAIN THREAD UTILITY VALUES --- #
MainThreadMessage = ""

# --- THREAD 1 UTILITY VALUES --- #
Contours = None
ThreadOneTimes = []
Thread_One_Last_Loop_Time = 0 # last loop time so main thread can see if it has frozen or not
TargetImage = None
Thread1Message = "" # this string gets displayed on the UI every loop of the main thread

# --- THREAD 2 UTILITY VALUES --- #
ThreadTwoTimes = []
Thread_Two_Last_Loop_Time = 0 # main thread can see if it freezes or not
ImageHasContents = True # value that thread 1 sets to tell thread two if there was anything in the image or not. Only set to false if Thread 1 saw nothing in the image.
Thread2Message = "" # this string also gets displayed on the UI every loop of the main thread

#Process utilities
Stream = cv2.VideoCapture(0) # the camera (well, the stream reading the camera)
kernel = numpy.ones((5,5), numpy.float32)/25 #average the pixels to make the blur kernel

#Threads
THREAD_1 = None
THREAD_2 = None



# --- THREAD UTILITY METHODS --- #

def DevmodeDisplayImage(window, image):
    #displays the current thread output image if the program is initalized in devmode. For the time being, should only be called by thread 1.
    if DEVMODE:
        cv2.imshow(window, image)
        cv2.waitKey(5)

def DispCurrentValues(): #displays all the current modifiable values.
    print(" --- CURRENT VALUES --- ")
    print("Color High Bound:      " + str(Settings.TARGET_COLOR_HIGH))
    print("Color Low Bound:       " + str(Settings.TARGET_COLOR_LOW))
    print("Threshold High Bound:  " + str(Settings.THRESHOLD_HIGH))
    print("Threshold Low Bound:   " + str(Settings.THRESHOLD_LOW))
    print("Target nonzero pixels: " + str(Settings.TARGET_NONZERO_PIXELS))
    print("Contour Area Max:      " + str(Settings.TARGET_CONTOUR_AREA_MAX))
    print("Contour Area Min:      " + str(Settings.TARGET_CONTOUR_AREA_MIN))
    print("Solidity High:         " + str(Settings.TARGET_OBJECT_SOLIDITY_HIGH))
    print("Solidity Low:          " + str(Settings.TARGET_OBJECT_SOLIDITY_LOW))
    print("Aspect ratio high:     " + str(Settings.TARGET_OBJECT_ASPECT_RATIO_HIGH))
    print("Aspect ratio low:      " + str(Settings.TARGET_OBJECT_ASPECT_RATIO_LOW))
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
    global Stream

    print("The program is doing the big die")
    
    Stream.release()

    if Settings.DEVMODE: #print out some final settings if in devmode   
        DispCurrentValues()

    #kill the program family
    ProgramEnding = True # main thread ending flag put up here
    THREAD_1.terminate() #raises the ending flag on the threads, telling them to stop
    THREAD_2.terminate()
    time.sleep(2) # waits for threads to stop as well as main loop
    cv2.destroyAllWindows() # disposes opencv UI windows
    print("Thread 1 running: "+str(THREAD_1.is_alive()))
    print("Thread 2 running: "+str(THREAD_2.is_alive()))

    while(THREAD_1.is_alive()) or (THREAD_2.is_alive()): # if the threads are still alive, wait for them to die
        print ("Waiting for threads to terminate...")
        print("Thread 1 running: "+str(THREAD_1.is_alive()))
        print("Thread 2 running: "+str(THREAD_2.is_alive()))
        time.sleep(1)
    
    quit() #stops running program


def CheckThreadConditions():
    #checks to see if the threads are still running. If they are not for whatever reason, reinstantiate them.
    #some thread recovery stuff so that threads can be revived if they freeze, error out, etc
    global THREAD_1
    global THREAD_2
    
    LastResponse1 = time.clock() - Thread_One_Last_Loop_Time #gets the time since the last thread update
    LastResponse2 = time.clock() - Thread_Two_Last_Loop_Time
    
    if ((not ProgramEnding) and (not THREAD_1.is_alive())) or (LastResponse1 > 1): #last response is in seconds btw
        #Thread 1 has been killed, errored out, or has frozen. Revive it.
        print("Reviving Thread 1")
        THREAD_1.terminate()
        time.sleep(0.1) # wait for thread to fully terminate
        THREAD_1 = Thread1.Thread1(1, "Thread 1", 1) #create and start a new thread 1
        THREAD_1.start() # this one actually starts thread

        UtilTextOne = "MESSAGE: Thread 1 revived."

    if ((not ProgramEnding) and (not THREAD_2.is_alive())) or (LastResponse2 > 1):
        #same thing for thread2. if it stops, revive it
        print("Reviving Thread 2")
        THREAD_2.terminate()
        time.sleep(0.1)
        THREAD_2 = Thread2.Thread2(2, "Thread 2", 2)
        THREAD_2.start()

        UtilTextOne = "MESSAGE: Thread 2 revived."
