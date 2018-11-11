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
import Tkinter as tk




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
DEVMODE = True #Option to run in developer mode. Displays all output and uses UI that allows user to change settings in runtime.
CALIBRATION_MODE = False

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


# --- UTILITIES -- #

#Devmode utilities
Devwindow = None #window where settings can be edited
TitleLabel = None

#Calibration mode utilities
CenterPixelColor = numpy.array( [0,0,0] ) #The output color of the calibration mode process.

# --- TKINTER UI UTILITIES --- #
Master_Window = None #Settings window which contains all the controls and information output
Slider_High_R = None #Slider for user control of target red value.
Slider_High_G = None #Slider for user control of target green value.
Slider_High_B = None #Slider for user control of target blue value.

Slider_Low_R = None #Slider for user control of low target red value.
Slider_Low_G = None #Slider for user contorl of low target green value.
Slider_Low_B = None #Slider for user control of low target blue value.

Slider_Threshold_Max = None #Slider for user control of threshold max value
Slider_Threshold_Value = None #Slider for user control of thereshold regular value
Slider_Nonzero_Pixels = None #Slider for user control of the number of nonzero pixels needed to continue processing
Slider_Area_Max = None #Slider for user control of the maximum area of contours
Slider_Area_Min = None #Slider for user control of minimum area of the contours

Running_Mode_Label = None #Label that displays the current program running mode. Can be Developer or Calibration
Thread1_Time_Label = None #Label that displays the time stats for thread 1.
Thread2_Time_Label = None #Label that displays the time stats for thread 2.
UtilLabel1 = None #A label that can display messages, warnings, or errors if devmode is enabled, but will display the center pixel color if in calibration mode.

Running_Mode_Text = None #Text for Running mode label.
Thread1_Time_Text = None #Text for thread1time label
Thread2_Time_Text = None #Text for thread2time label
UtilText1 = None #Text for utillabel


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
    global CenterPixelColor
    
    Binary = None

    while (Stream.isOpened()):
        #execute a lot
        startTime = time.clock() # get start of loop in processor time

        returnVal, Binary = Stream.read()        
        if returnVal == True:

            if not CALIBRATION_MODE:
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

            else: #Calibration mode is enabled. Threshold image and display with contour at center point.
                ret, Binary = cv2.threshold(Binary, THRESHOLD_LOW, THRESHOLD_HIGH, cv2.THRESH_BINARY) #thresholds image
                Binary = cv2.resize(Binary, (400,400))
                CenterPixelColor[2] = Binary[200][200][2] #Center pixel Red color
                CenterPixelColor[1] = Binary[200][200][1] #Center pixel green color
                CenterPixelColor[0] = Binary[200][200][0] #Center pixel blue color

                cv2.drawContours(Binary, numpy.array( [[[200,200]]] ), -1, (255,255,255), 3) #draws a contour at the center of the image for user reference.

                
                cv2.imshow("Threshold", Binary)
                cv2.waitKey(5)
            
        else: # Stream was unable to get the camera data. Print a message.
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
        if (Contours != None) and (not CALIBRATION_MODE): # we do not want to run loop if there are no contours. Thread not needed in calibration mode. 
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
    global TARGET_COLOR_LOW
    global THRESHOLD_HIGH
    global THRESHOLD_LOW
    global TARGET_NONZERO_PIXELS
    global TARGET_CONTOUR_AREA_MAX
    global TARGET_CONTOUR_AREA_MIN
    global TARGET_CONTOUR_ASPECT_RATIO_MAX
    global TARGET_CONTOUR_ASPECT_RATIO_MIN

    global Running_Mode_Label
    global Thread1_Time_Text
    global Thread2_Time_Text
    global UtilText1
    time.sleep(2) #give the threads a little more time to start
    while True:

        if DEVMODE or CALIBRATION_MODE: # grabs settings from the settings window and applies them
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

            #update labels with some time and dev stats
            RunningMode = "Running Mode: " #first init the vars
            Thread1TimeStats = "--- THREAD 1 TIMES ---\n"
            Thread2TimeStats = "--- THREAD 2 TIMES ---\n"
            UtilTextOne = ""

            #now set the vars
            if DEVMODE:
                RunningMode += "Developer"
            elif CALIBRATION_MODE:
                RunningMode += "Calibration"
            RunningMode += "\n"

            Thread1TimeStats += "Last Recorded loop: " + str(ThreadOneTimes[len(ThreadOneTimes) -1]) + "\n"
            Thread1TimeStats += " Average Loop Time: " + str(Thread1AverageTime()) + "\n"
            Thread1TimeStats += " Longest Loop Time: " + str(Thread1MaxTime()) + "\n"
            Thread1TimeStats += "Shortest Loop Time: " + str(Thread1MinTime()) + "\n\n"
            
            Thread2TimeStats += "Last Recorded loop: " + str(ThreadTwoTimes[len(ThreadTwoTimes) -1]) + "\n"
            Thread2TimeStats += " Average Loop Time: " + str(Thread2AverageTime()) + "\n"
            Thread2TimeStats += " Longest Loop Time: " + str(Thread2MaxTime()) + "\n"
            Thread2TimeStats += "Shortest Loop Time: " + str(Thread2MinTime()) + "\n\n"

            if CALIBRATION_MODE:
                UtilTextOne = "Center Pixel Color: BGR" + str(CenterPixelColor)
            
            #now set the labels
            Running_Mode_Text.set(RunningMode)
            Thread1_Time_Text.set(Thread1TimeStats)
            Thread2_Time_Text.set(Thread2TimeStats)
            UtilText1.set(UtilTextOne)
            
                        
        else: #NOT devmode
            time.sleep(0.5)

        #send values to the RoboRIO here.
        

# --- BUTTON EVENTS --- #
def DevmodeButtonClicked(): #Switches to normal devmode output if the program is in calibration mode.
    global DEVMODE
    global CALIBRATION_MODE
    DEVMODE = True
    CALIBRATION_MODE = False

def CalibrateButtonClicked(): #switches to calibration mode if the program is in devmode.
    global DEVMODE
    global CALIBRATION_MODE
    DEVMODE = False
    CALIBRATION_MODE = True
    #now since its calibration mode, we only want the thresholding window with the contour. Destroy all other windows.
    cv2.destroyAllWindows() #we can do this because the programs just going to create another one.

def QuitButtonClicked(): # kills the program
    print("Killing the program...")
    Kill()


#starts the program and creates different threads and things for the things to run on.
def Vision():
    #start the stuff going
    if Stream.isOpened():
        #initialize the threads
        if DEVMODE or CALIBRATION_MODE: #gives you the good stuff, but a bit harder on the CPU
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

            # --- INITALIZE THE CONTROLS --- #
            #Create the sliders and controls to be put into the window
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
            #Set the values for each of the controls
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
            #now pack all the new sliders and things into the window to be displayed
            Slider_High_R.pack()
            Slider_High_G.pack()
            Slider_High_B.pack()
            Slider_Low_R.pack()
            Slider_Low_G.pack()
            Slider_Low_B.pack()
            Slider_Threshold_Max.pack()
            Slider_Threshold_Value.pack()
            Slider_Nonzero_Pixels.pack()
            Slider_Area_Max.pack()
            Slider_Area_Min.pack()

            # --- INITALIZE THE LABELS --- #
            #well... actually the text variables
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

            #pack the labels
            Running_Mode_Label.pack()
            Thread1_Time_Label.pack()
            Thread2_Time_Label.pack()
            UtilLabel1.pack()

            # --- INITIALIZE THE BUTTONS --- #
            #p.s: not putting the buttons into variables since Im not grabbing any data. They will exist in TK.
            tk.Button(Master_Window, text="Devmode Enable", width=50, command=DevmodeButtonClicked).pack()
            tk.Button(Master_Window, text="Calibration Mode Enable", width=50, command=CalibrateButtonClicked).pack()
            tk.Button(Master_Window, text="Kill Program", width=50, command=QuitButtonClicked).pack()
                  
        else:
            print("Initializing in Running Mode.\r\n\r\n") #runner mode is lighter on CPU but does not give you any feedback whatsoever (it just gives you the center box point)

        global THREAD_1
        global THREAD_2

        print("Hello. I am the vision man.")
        THREAD_1 = thread.start_new_thread( Thread1, () ) # creates and starts new thread running Thread1(), to take and process the images
        THREAD_2 = thread.start_new_thread( Thread2, () ) # creates and starts new thread running Thread2(), to process contours and come up with a center point
        time.sleep(0.25) #waits a little for threads to initalize
        Watch() #starts master loop
    else:
        print("WARNING: COULD NOT OPEN THE CAMERA")
        quit() #end program right then and there 

#main entry
if __name__ == '__main__': #MAIN ENTRY POINT RIGHT HERE
    #try:
        Vision() #STARTS THE PROGARM!!
    #except:
        #Kill() #displays set values and quits
