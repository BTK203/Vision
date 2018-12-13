
from __future__ import division

#vision files
import Settings
import Thread1
import Main
import Utilities

#required packages
import cv2
import threading
import time
import numpy

            
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
        if Settings.DEVMODE:
            Utilities.Thread2Message = "\nArea:          " + str(Area)
            Utilities.Thread2Message += "\nSolidity:     " + str(Solidity)
            Utilities.Thread2Message += "\nAspect Ratio: " + str(AspectRatio)
        
    def GetContourData(self, contour, x,y,w,h): #returns a bunch of stuff about the contour given.
        Area = cv2.contourArea(contour)
        
        #getting solidity
        BoxArea = w * h
        Solidity = Area / BoxArea
        #getting aspect ratio
        AspectRatio = w/h
        self.DevmodeShowContour(Area, Solidity, AspectRatio) # show the area and solidity data to the UI

        return Area, AspectRatio, Solidity

    def TestContour(self, Area, Solidity, AspectRatio): #tests the contour given the parameters.
        Utilities.Thread2Message += "\nTests passed: "
        if(Area < Settings.TARGET_CONTOUR_AREA_MAX) and (Area > Settings.TARGET_CONTOUR_AREA_MIN):
            Utilities.Thread2Message += "Area"
            if(Solidity < Settings.TARGET_OBJECT_SOLIDITY_HIGH) and (Solidity > Settings.TARGET_OBJECT_SOLIDITY_LOW):
                Utilities.Thread2Message += ", Solidity"
                if(AspectRatio < Settings.TARGET_OBJECT_ASPECT_RATIO_HIGH) and (AspectRatio > Settings.TARGET_OBJECT_ASPECT_RATIO_LOW):
                    Utilities.Thread2Message += ", Aspect Ratio"
                    return True

        return False 

    #processes the contour and returns the center points
    def ProcessContour(self, x, y, w, h):
        w /= 2
        h /=2
        x += w
        y += h
        #the deviation of each coordinate
        DeviateX = abs(int(x)) - Utilities.BoxCenterX
        DeviateY = abs(int(y)) - Utilities.BoxCenterY
        if(Utilities.BoxCenterX == -1) or ((DeviateX < Settings.DEVIATION_MAX) and (DeviateY < Settings.DEVIATION_MAX)):
            centerX = int(x) #make sure they are ints or else we get an error drawing the points
            centerY = int(y)
            Utilities.Thread2Message += "\nBox Center: (" + str(Utilities.BoxCenterX) + ", " + str(Utilities.BoxCenterY) + ")"
            return centerX, centerY
        return -1, -1 #the contour does not pass the deviation test. return -1s
        
    def run(self):
        #Thread two stuff (algorithm steps 6-9)
        print("thread 2 init")

        global BoxCenterX
        global BoxCenterY
        global Thread_Two_Last_Loop_Time
        global Thread2Message

        #Test the contours to eliminate the ones that we dont want
        while Utilities.Stream.isOpened():
            startTime = time.clock()

            Thread1Image = numpy.copy(Utilities.TargetImage)
            zeros = len(numpy.argwhere(Thread1Image))

            passed = 0 #the number of contours that have passed the test, used for reference to know if we need to set the coords to -1
            if (zeros > Settings.TARGET_NONZERO_PIXELS) and (Utilities.ImageHasContents): # only continue if there are actually contours in the thing. If ImageHasContents is false that means that thread 1 did not see anything in image
                #contouring stuff
                Thread1Image = cv2.inRange(Thread1Image, Settings.TARGET_COLOR_LOW, Settings.TARGET_COLOR_HIGH) # convert to binary
                #DevmodeDisplayImage("Binary", TargetImage)
                Contours, Hierarchy = cv2.findContours(Thread1Image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # get them contours

##                if (DEVMODE) and (len(Contours) > 0): #it hecking slows the program down a lot tho D:<
##                    ThreadOneOut = numpy.zeros((500,500),numpy.uint8) # reset the threadoneout image to nothing(again)
##                    cv2.drawContours(ThreadOneOut, Contours, -1, (255, 255, 0),1) # draw the contours(they will appear white because the image is binary)
##                    DevmodeDisplayImage("Live", ThreadOneOut)
            
                if (Contours != None) and (len(Contours) > 0): # we do not want to run loop if there are no contours.
                    passed = 0 #the number of contours that have passed the test. needed to make sure values are set to -1 if none pass
                    lastBoxCenterX = Utilities.BoxCenterX
                    lastBoxCenterY = Utilities.BoxCenterY
                    
                    for contour in Contours:
                        Thread2Message = "" #reset the message so that we dont get big a lot of text
                        x,y,w,h = cv2.boundingRect(contour) 
                        Area, AspectRatio, Solidity = self.GetContourData(contour, x,y,w,h) #gets contour data such as aspect ratio, solidity, area
                        #test the area & aspect ratio
                        if self.TestContour(Area, Solidity, AspectRatio):
                            passed += 1
                            Utilities.BoxCenterX, Utilities.BoxCenterY = self.ProcessContour(x,y,w,h) #assigns the box variables

            if passed <= 0:
                Utilities.BoxCenterX = -1
                Utilities.BoxCenterY = -1

            print("Thread 2 loops")
                
            ThreadTime = time.clock() - startTime
            ThreadTime *= 1000 #convert to milliseconds
            Utilities.ThreadTwoTimes.append(ThreadTime)
            Utilities.Thread_Two_Last_Loop_Time = time.clock()

            if self.stop: #stops the loop and thread if the program is ending
                print("Thread 2 terminating")
                return
        
