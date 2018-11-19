# Program to tell users some recommended values for Vision.py
# Author Brach Knutson

from __future__ import division
import numpy
import cv2
import Tkinter as tk
import tkMessageBox
import time

# --- GLOBALS --- #
KillProcess = False
Stream = cv2.VideoCapture(0) #the video stream for the camera

# --- SETTINGS --- #
THRESHOLD_HIGH = 255
THRESHOLD_VAL = 57 #im doing this in a dark room its ok

# --- UI ELEMENTS --- #
Master_Window = tk.Tk()
ColorText = None

# --- UTILITIES --- #
kernel = numpy.ones((5,5), numpy.float32)/25 # dilation kernel

Target_High = numpy.array( [0,0,0] )
Target_Low = numpy.array( [1,1,1] )


# --- UTILITY METHODS --- #
def getOtherColor():
    print("Please specify other color.")
    b = int(input("b:"))
    g = int(input("g:"))
    r = int(input("r:"))
    return b, g, r #return the colors

def PutTargetsInRange(): #puts the target color values in range (0-255)
    global Target_High
    global Target_Low
    for i in range(0,3):
        if Target_High[i] < 0: Target_High[i] = 0
        if Target_High[i] > 255: Target_High[i] = 255
        if Target_Low[i] < 0: Target_Low[i] = 0
        if Target_Low[i] > 255: Target_Low[i] = 255


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

def TakeAndProcessImage():
    global ColorText
    #takes and processes the image for contour data
    _, frame = Stream.read() #take the image first
    
    if raw_input("Would you like to use " +ColorText.get() + " To process the image? [y, n]") == "n":
        b,g,r = getOtherColor()
        Target_High[0] = b + 25 #set the targets now
        Target_High[1] = g + 25
        Target_High[2] = r + 25
        Target_Low[0] = b - 25
        Target_Low[1] = g - 25
        Target_Low[2] = r - 25
        PutTargetsInRange()
        
    _, frame = cv2.threshold(frame,THRESHOLD_VAL, THRESHOLD_HIGH, cv2.THRESH_BINARY)
    frame = cv2.resize(frame, (200,200))
    frame = cv2.dilate(frame, kernel)
    output = numpy.copy(frame) #output image to draw on and show to the user
    frame = cv2.inRange(frame, Target_Low, Target_High)
    frame, contours, hierarchy = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) > 0:
        for contour in contours:
            #go through the contours and figure out which is closest to the cursor
            x,y,w,h = cv2.boundingRect(contour) #get teh rectangle and things
            if (100 > x) and (100 > y):
                if(100 < x+w) and (100 < y+h):
                    #the cursor is over the contour!
                    ContourArea = cv2.contourArea(contour)
                    BoxArea = w * h
                    AspectRatio = w/h
                    Solidity = ContourArea / BoxArea

                    Characteristics = "Settings used: "
                    Characteristics += "\nTarget Color High:      " + str(Target_High)
                    Characteristics += "\nTarget Color Low :      " + str(Target_Low)
                    Characteristics += "\nThreshold Value  :      " + str(THRESHOLD_VAL)
                    Characteristics += "\nThreshold High   :      " + str(THRESHOLD_HIGH)

                    Characteristics += "\n\nContour Characteristics: "
                    Characteristics += "\nContour Area     :      " + str(ContourArea)
                    Characteristics += "\nContour Aspect Ratio:   " + str(AspectRatio)
                    Characteristics += "\nContour Solidity :      " + str(Solidity)

                    cv2.rectangle(output, (x,y), (x+w, y+h), (0,0,255), 5) #draw a rectangle around the contour we are targeting
                    
                    w /= 2
                    h /= 2
                    x += w
                    y += h

                    output = cv2.drawContours(output, numpy.array( [[[int(x), int(y)]]] ), -1, (255,255,0), 5) #draws dot at the center of the box
                    cv2.imshow("output", output)
                    cv2.waitKey(5)

                    tkMessageBox.showinfo("Results", Characteristics)
                    return
            
    else:
        ColorText.set("No contours were found in the image.")

    Master_Window.update()
    

# --- PROCESSes --- #

#UI Initialization

def InitUI():
    global Master_Window
    global ColorText
    cv2.namedWindow("output")
    
    tk.Label(Master_Window, text="VISION CALIBRATION\n", anchor=tk.W).pack() # title label?
    ColorText = tk.StringVar(Master_Window)
    ColorText.set("hello")
    Color = tk.Label(Master_Window, textvariable=ColorText, anchor=tk.W)
    Color.pack() #load the label into the UI

    tk.Button(Master_Window, text="Take And Process", width=50, command=TakeAndProcessImage).pack()
    tk.Button(Master_Window, text="Exit", width=50, command=Kill).pack() #exit button

#The loops
    
def Loop():
    global ColorText
    while Stream.isOpened():
        #loop through a lot
        _, frame = Stream.read()
        _, frame = cv2.threshold(frame, THRESHOLD_VAL, THRESHOLD_HIGH, cv2.THRESH_BINARY)
        frame = cv2.resize(frame, (200,200)) #resize so I actually know how big it is lmao
        frame = cv2.dilate(frame, kernel) #dilation

        #get the color of the thing at the center of the image
        r = frame[100][100][2]
        g = frame[100][100][1]
        b = frame[100][100][0]

        Target_High[0] = b + 25
        Target_High[1] = g + 25
        Target_High[2] = r + 25
        Target_Low[0] = b - 25
        Target_Low[1] = g - 25
        Target_Low[2] = r - 25
        PutTargetsInRange()

        #now draw contour and show image
        cv2.drawContours(frame, numpy.array( [[[100,100]]] ), -1, (255,255,255), 5)
        #get the colors
        ColorText.set("Color: BGR ("+ str(b) + ", " + str(g) + ", " + str(r) + ")")
        
        #final output
        cv2.imshow("output", frame)
        cv2.waitKey(5)
            
        Master_Window.update()
        

if __name__ == "__main__": #start here
    print("Initializing the UI...")
    InitUI()
    print("Starting Loop...")
    Loop()
    
