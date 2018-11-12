# Program to tell users some recommended values for Vision.py
# Author Brach Knutson

import numpy
import cv2
import Tkinter as tk
import time

# --- GLOBALS --- #
KillProcess = False
Stream = cv2.VideoCapture(0) #the video stream for the camera

# --- SETTINGS --- #
THRESHOLD_HIGH = 255
THRESHOLD_VAL = 28 #im doing this in a dark room its ok

# --- UI ELEMENTS --- #
Master_Window = tk.Tk()
ColorText = None

# --- BUTTON EVENTS -- #
def Kill():
    global KillProcess
    global Stream
    print("Killing...")
    KillProcess = True;
    Stream.release()
    time.sleep(1)
    cv2.destroyAllWindows()
    print("Goodbye family")
    quit() #button event that kills the program


# --- PROCESS --- #

def InitUI():
    global Master_Window
    global ColorText
    cv2.namedWindow("output")
    
    tk.Label(Master_Window, text="VISION CALIBRATION\n", anchor=tk.W).pack() # title label?
    ColorText = tk.StringVar(Master_Window)
    ColorText.set("hello")
    Color = tk.Label(Master_Window, textvariable=ColorText, anchor=tk.W)
    Color.pack() #load the label into the UI

    tk.Button(Master_Window, text="Exit", width=50, command=Kill).pack() #exit button
    

def Loop():
    global ColorText
    while Stream.isOpened():
        #loop through a lot
        _, frame = Stream.read()
        #process image
        _, frame = cv2.threshold(frame, THRESHOLD_VAL, THRESHOLD_HIGH, cv2.THRESH_BINARY)
        #resize it so I actually know how big it is lmao
        frame = cv2.resize(frame, (400,400))

        #get the colors
        r = frame[200][200][2]
        g = frame[200][200][1]
        b = frame[200][200][0]

        #now draw contour and show image
        cv2.drawContours(frame, numpy.array( [[[200,200]]] ), -1, (255,255,255), 5)
        #get the colors
        ColorText.set("Color: BGR ("+ str(r) + ", " + str(g) + ", " + str(b) + ")")
        
        cv2.imshow("output", frame)
        cv2.waitKey(5)
        Master_Window.update()


if __name__ == "__main__": #start here
    print("Init UI")
    InitUI()
    print("Starting main loop...")
    Loop()
    
