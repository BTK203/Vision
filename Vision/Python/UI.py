
#other vision files
import Settings
import Thread1
import Thread2
import Main
import Utilities

#required packages
import Tkinter as tk
import time

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


def UpdateUI():
    #method called from Watch() that updates the UI in the TKinter window.
    #Update values in the master window
    Master_Window.update()
    #get all the values from the controls and put them into the process settings
    Settings.TARGET_COLOR_HIGH[2] = Slider_High_R.get()
    Settings.TARGET_COLOR_HIGH[1] = Slider_High_G.get()
    Settings.TARGET_COLOR_HIGH[0] = Slider_High_B.get()
    Settings.TARGET_COLOR_LOW[2] = Slider_Low_R.get()
    Settings.TARGET_COLOR_LOW[1] = Slider_Low_G.get()
    Settings.TARGET_COLOR_LOW[0] = Slider_Low_B.get()
    Settings.THRESHOLD_HIGH = Slider_Threshold_Max.get()
    Settings.THRESHOLD_LOW= Slider_Threshold_Value.get()
    Settings.TARGET_NONZERO_PIXELS = Slider_Nonzero_Pixels.get()
    Settings.TARGET_CONTOUR_AREA_MAX = Slider_Area_Max.get()
    Settings.TARGET_CONTOUR_AREA_MIN = Slider_Area_Min.get()

    #update labels with some time and dev stats
    Thread1TimeStats = "System timer: " + str(time.clock()) + " Seconds\n\n--- THREAD 1 TIMES ---\n"
    Thread2TimeStats = "--- THREAD 2 TIMES ---\n"
    UtilTextOne = ""

    #calculate the times for the processes and put them into strings to be displayed in the window
    Thread1TimeStats += "Last Recorded loop: " + str(Utilities.ThreadOneTimes[len(ThreadOneTimes) -1]) + "ms\n"
    Thread1TimeStats += " Average Loop Time: " + str(Utilities.Thread1AverageTime()) + "ms\n"
    Thread1TimeStats += " Longest Loop Time: " + str(Utilities.Thread1MaxTime()) + "ms\n"
    Thread1TimeStats += "Shortest Loop Time: " + str(Utilities.Thread1MinTime()) + "ms\n\n"
    #the thread 2 time stuff
    Thread2TimeStats += "Last Recorded loop: " + str(Utilities.ThreadTwoTimes[len(ThreadTwoTimes) -1]) + "ms\n"
    Thread2TimeStats += " Average Loop Time: " + str(Utilities.Thread2AverageTime()) + "ms\n"
    Thread2TimeStats += " Longest Loop Time: " + str(Utilities.Thread2MaxTime()) + "ms\n"
    Thread2TimeStats += "Shortest Loop Time: " + str(Utilities.Thread2MinTime()) + "ms\n\n"

    #Update the Utility Label based on some events and which mode the program is running in. 

    if not THREAD_1.is_alive():
        Utilities.UtilTextOne += "\nWARNING: Thread 1 has stopped running!"

    if not THREAD_2.is_alive():
        Utilities.UtilTextOne += "\nWARNING: Thread 2 has stopped running!"
    
    Utilities.UtilTextOne += "recognized box center: (" + str(BoxCenterX) + ", " + str(BoxCenterY) + ")"
    
    #now set the labels
    Thread1_Time_Text.set(Thread1TimeStats)
    Thread2_Time_Text.set(Thread2TimeStats)
    UtilText1.set("Thread 1: "+ Thread1Message + "\nThread 2: " + Thread2Message + "\nMain: " + UtilTextOne) #Set the thread messages

def UpdateOutputImage():
    #show output image with point drawn
    img = numpy.copy(OriginalImage) #copy the original image taken by thread 1
    if (BoxCenterX > -1) and (BoxCenterY > -1):
        cv2.drawContours(img, numpy.array( [[[BoxCenterX, BoxCenterY]]] ), -1, (255,255,0), 5) #draw the contour center point
        
    cv2.imshow("Output", img) # show the image in the window
    cv2.waitKey(5)


def InitUI():
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

    # --- set and grid the UI elements --- #

    Slider_High_R.set(Settings.TARGET_COLOR_HIGH[2])
    Slider_High_G.set(Settings.TARGET_COLOR_HIGH[1])
    Slider_High_B.set(Settings.TARGET_COLOR_HIGH[0])
    Slider_Low_R.set(Settings.TARGET_COLOR_LOW[2])
    Slider_Low_G.set(Settings.TARGET_COLOR_LOW[1])
    Slider_Low_B.set(Settings.TARGET_COLOR_LOW[0])
    Slider_Threshold_Max.set(Settings.THRESHOLD_HIGH)
    Slider_Threshold_Value.set(Settings.THRESHOLD_LOW)
    Slider_Nonzero_Pixels.set(Settings.TARGET_NONZERO_PIXELS)
    Slider_Area_Max.set(Settings.TARGET_CONTOUR_AREA_MAX)
    Slider_Area_Min.set(Settings.TARGET_CONTOUR_AREA_MIN)
    Slider_Solidity_High.set(Settings.TARGET_OBJECT_SOLIDITY_HIGH * 100) #multiply by 100 to get percentages instead of decimals
    Slider_Solidity_Low.set(Settings.TARGET_OBJECT_SOLIDITY_LOW * 100)

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
    tk.Button(Master_Window, text="Kill Program", width=50, command=Utilities.Kill).grid(row=8, column=1)

    #grid the labels and things
    #pack the labels
    Running_Mode_Label.grid(row=0, column=1)
    Thread1_Time_Label.grid(row=2, column=1)
    Thread2_Time_Label.grid(row=4, column=1)
    UtilLabel1.grid(row=6, column=1)
                    