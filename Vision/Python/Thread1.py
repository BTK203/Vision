
#vision files
import Settings
import Main
import Thread2
import UI
import Utilities

#required packages
import cv2
import threading
import numpy
import time

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

        while (Utilities.Stream.isOpened()):
            #execute a lot
            startTime = time.clock() # get start of loop in processor time

            returnVal, Binary = Utilities.Stream.read()
            Binary = cv2.resize(Binary, (200,200)) #resize the image to make it smaller, faster

            if returnVal == True:

                # now some simple image processing
                OriginalImage = numpy.copy(Binary)
                #DevmodeDisplayImage("Take", Binary)
                ret, Binary = cv2.threshold(Binary,Settings.THRESHOLD_LOW, Settings.THRESHOLD_HIGH ,cv2.THRESH_BINARY) #Threshold to increase image contrast            
                #DevmodeDisplayImage("Threshold", Binary)
                zeros = len(numpy.argwhere(Binary))
                if zeros > Settings.TARGET_NONZERO_PIXELS:
                    #only continue if there is something in the image
                    Utilities.TargetImage = cv2.dilate(Binary, Utilities.kernel, Binary) #dilate to close gaps
                    #DevmodeDisplayImage("Dilate", Binary)
                    Utilities.ImageHasContents = True

                else:
                    #nothing significant in image. In this case just tell thread 2 not to run
                    Utilities.ImageHasContents = False
                
            else: # Stream was unable to get the camera data. Print a message.
                print("unable to get camera data!")

            #calculate loop time if devmode
            if self.stop:
                print("Thread 1 terminating")
                return
                
            ThreadTime = time.clock() - startTime
            ThreadTime *= 1000 #convert to milliseconds
            Utilities.ThreadOneTimes.append(ThreadTime)
            Thread_One_Last_Loop_Time = time.clock()