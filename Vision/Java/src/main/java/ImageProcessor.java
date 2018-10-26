import java.lang.Thread;

import java.lang.Thread;

import java.util.ArrayList;
import java.awt.FlowLayout;
import java.awt.image.*;
import java.awt.Graphics;
import java.io.File;
import java.util.ArrayList;
import java.awt.FlowLayout;
import java.awt.image.*;
import java.awt.Graphics;
import java.io.File;
import javax.imageio.ImageIO;
import javax.swing.JLabel;
import javax.swing.JFrame;
import javax.swing.ImageIcon;
import javax.swing.DebugGraphics;
import javax.swing.SwingConstants;

import edu.wpi.first.wpilibj.networktables.*;
import edu.wpi.first.wpilibj.tables.*;
import edu.wpi.cscore.*;

import org.opencv.core.Mat;
import org.opencv.core.Core;
import org.opencv.core.Size;
import org.opencv.core.Scalar;
import org.opencv.imgproc.Imgproc;
import org.opencv.imgcodecs.Imgcodecs;

import java.*;

import java.lang.*;

/**
 * CV IMAGE PROCESSING CLASS THAT TAKES IMAGE AND PROCESSES IT IN A DIFFERENT THREAD. 
 * written by Brach Knutson, FRC3695
 */

public class ImageProcessor implements Runnable {
    
    //success booleans that indicate the success of a process
    

    //accessories
    private ProcessTimer timer = new ProcessTimer();
    private ProcessTimer threadTimer = new ProcessTimer();

    //CV required vars. DO NOT TOUCH
    private CvSink imageSink = new CvSink("CV Image Grabber");
    private UsbCamera camera = setUsbCamera(0);

    //parent
    private VisionMonitor Master;

    //some output variables
    private BufferedImage outputImage; //the mat that this class outputs for screen view
    private long ImageTakeTime, ImageBlurTime, ImageDilateTime, ImageErodeTime, ImageHsvTime, ImageBinTime, ImageWriteTime, TotalthreadTime;
    private boolean ImageWrite = true, ThreadSuccess = true, GetImage = true, ImageHsv = true, ImageBin = true, ImageBlur = true, ImageDilate = true, ImageErode = true;

    private int frameNumber = 0;

    public ImageProcessor(VisionMonitor master) {
        Master = master;
        System.loadLibrary("opencv_java310");

        // USB Camera
        // Set the resolution for our camera, since this is over USB
        camera.setResolution(640,480);

        // This creates a CvSink for us to use. This grabs images from our selected camera, 
        // and will allow us to use those images in opencv
        
        imageSink.setSource(camera);
    }

    //the accessors. boo
    public BufferedImage OUTPUT_IMAGE() { return outputImage; }

    public int FRAME_NUMBER() { return frameNumber; }

    public long IMG_TAKE_TIME() { return ImageTakeTime; }
    public long IMG_BLUR_TIME() { return ImageBlurTime; }
    public long IMG_DILATE_TIME() { return ImageDilateTime; }
    public long IMG_ERODE_TIME() { return ImageErodeTime; }
    public long IMG_HSV_TIME() { return ImageHsvTime; }
    public long IMG_BIN_TIME() { return ImageBinTime; }
    public long IMG_WRITE_TIME() { return ImageWriteTime; }
    public long THREAD_TIME() { return TotalthreadTime; }

    //now the booleans
    //public boolean GetImage = true, ImageBlur = true, ImageDilate = true, ImageErode = true, ImageHsv = true, ImageBin = true;

    public boolean IMG_GET_IMAGE() { return GetImage; }
    public boolean IMG_IMAGE_BLUR() { return ImageBlur; }
    public boolean IMG_IMAGE_DILATE() { return ImageDilate; }
    public boolean IMG_IMAGE_ERODE() { return ImageErode; }
    public boolean IMG_IMAGE_HSV() { return ImageHsv; }
    public boolean IMG_IMAGE_BIN() { return ImageBin; }
    public boolean IMG_IMAGE_WRITE() { return ImageWrite; }
    public boolean THREAD_SUCCESS() { return ThreadSuccess; }


    public void run() {
        while(true) {
            try {
                threadTimer.Start();

                // Grab a frame. If it has a frame time of 0, there was an error.
                // Just skip and continue
                Mat inputImage = new Mat();
                Mat hsv = new Mat();
                Mat bin = new Mat();
            
                timer.Start();
                try {
                    long frameTime = imageSink.grabFrame(inputImage);
                    if (frameTime == 0) continue;
                    GetImage = true;
                } catch(Exception ex) {
                    GetImage = false;
                }
                ImageTakeTime = timer.End(); //get total time
                // Below is where you would do your OpenCV operations on the provided image
                timer.Start(); //resets and starts the timer
                try {
                    Imgproc.cvtColor(inputImage, hsv, Imgproc.COLOR_BGR2HSV);
                    ImageHsv = true;
                } catch(Exception ex) {
                    ImageHsv = false;
                }
                ImageHsvTime = timer.End();

                timer.Start();
                try {
                    //try to get binary image!
                    Core.inRange(hsv, Constants.COLOR_LOW_BOUND, Constants.COLOR_HIGH_BOUND, bin); //convert the image to binary and store it in "bin" mat
                    ImageBin = true; //nothing went wrong!
                } catch(Exception ex) {
                    ImageBin = false; //something went wrong! D:<
                }
                ImageBinTime = timer.End(); //get the time of course
  
                // Here is where you would write a processed image that you want to restreams
                
                if(Constants.DO_BLUR) {
                    timer.Start();
                    try {
                        Imgproc.blur(inputImage, inputImage, new Size(10,10));
                        ImageBlur = true; //note that blur was successful
                    } catch(Exception ex) {
                        ImageBlur = false; //the operation was NOT successful
                    }
                    ImageBlurTime = timer.End();
                }

                if(Constants.DO_ERODE) { //runs only if erode setting in Constants is set to true.
                    timer.Start();
                    try {
                        Mat kernel = Imgproc.getStructuringElement(Imgproc.MORPH_RECT, new Size(Constants.ERODE_SIZE, Constants.ERODE_SIZE));
                        Imgproc.erode(hsv, hsv, kernel);
                        ImageErode = true;
                    } catch(Exception ex) {
                        ImageErode = false;
                    }
                    ImageErodeTime = timer.End();
                }

                if(Constants.DO_DILATE) { //runs only if the dilate setting in Constants is set to true. 
                    timer.Start();
                    try { //attempts to dilate the image
                        Mat kernel = Imgproc.getStructuringElement(Imgproc.MORPH_RECT, new Size(Constants.DILATE_SIZE, Constants.DILATE_SIZE));
                        Imgproc.dilate(hsv, hsv, kernel);
                        ImageDilate = true; //success!
                    } catch(Exception ex) {
                        ImageDilate = false; //not success.
                    }
                    ImageDilateTime = timer.End();
                }

                timer.Start(); //time this too.
                if(Constants.DISPLAY_IMAGE_OUTPUT) {
                    Imgcodecs.imwrite("output.png", bin);
                    try {
                        outputImage = ImageIO.read(new File("output.png"));
                        ImageWrite = true;
                    } catch(Exception ex) {
                        ImageWrite = false;
                    }
                }
                ImageWriteTime = timer.End();
                TotalthreadTime = threadTimer.End();
                ThreadSuccess = true;
                frameNumber++;
            } catch(Exception ex) {
                ThreadSuccess = false;
            }
        }
    }


    private UsbCamera setUsbCamera(int cameraId) {
        // This gets the image from a USB camera 
        // Usually this will be on device 0, but there are other overloads
        // that can be used
        UsbCamera camera = new UsbCamera("CoprocessorCamera", cameraId);
        return camera;
    }
}