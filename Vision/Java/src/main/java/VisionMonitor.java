
/**
 * MAIN CLASS FOR CV APPLICATION. WATCHES OVER OTHER 2 THREADS, IMAGE PROCESSING AND CONTOUR PROCESSING. HANDLES ALL OUTPUT.
 * written by: Brach Knutson, FRC3695
 */

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
import org.opencv.imgproc.Imgproc;
import org.opencv.imgcodecs.Imgcodecs;

import java.*;

import java.lang.*;

public class VisionMonitor {

    //our two other threads that handle most cv stuff
    private ImageProcessor imgProc;
    private ContourProcessor conProc;

    //thread workers
    private Thread imgWorker;
    private Thread conWorker;

    //output window stuff
    private JFrame outputFrame;
    private JLabel frameLabel;
    ProcessTimer dispTimer = new ProcessTimer();
    //other variables used for development purposes
    private int frameNum = 0;

    public VisionMonitor() {
        //creates and initalizes the output window
        System.loadLibrary("opencv_java310");
        outputFrame = new JFrame();
        outputFrame.setLayout(new FlowLayout());
        outputFrame.setSize(600,400);
        frameLabel = new JLabel();
        outputFrame.setLocationByPlatform(true);

        //create workers
        imgProc = new ImageProcessor(this);
        conProc = new ContourProcessor();

        //create threads
        imgWorker = new Thread(imgProc);
        conWorker = new Thread(conProc);
        imgWorker.start();
        conWorker.start();
    }

    //main loop. Watches for updates to any variables at all.
    public void run() {
        while(true) {
            try {
                Output(imgProc.OUTPUT_IMAGE());
                if(!Constants.DISPLAY_IMAGE_OUTPUT)
                    Thread.sleep(25);
            } catch(Exception ex) {
                System.out.println("main loop exception");
            }
        }
    }

    private void Output(BufferedImage img) {
        //display output if the setting is enabled.
        
        if(Constants.DISPLAY_TEXT_OUTPUT) {
            boolean DisplaySuccessful = true;
            dispTimer.Start();
            //Display the image using a JFrame
            if(Constants.DISPLAY_IMAGE_OUTPUT) {
            try {
                if(imgProc.FRAME_NUMBER() != frameNum) { //there is an updated frame on the imgProc. Show it!!
                    //updates the label to show the new image, along with a frame number.
                    frameLabel.setIcon(new ImageIcon(img));
                    frameLabel.setText("Frame:" + String.valueOf(frameNum));
                    frameLabel.setLocation(0,0);
                    frameLabel.setSize(600,400);
        
                    //adds label to the frame
                    outputFrame.add(frameLabel);

                    //updates the frame to show the updated label with the updated image
                    outputFrame.setVisible(true);
                    outputFrame.revalidate();
                    outputFrame.repaint(500, 0,0,600,400);
                    outputFrame.update(outputFrame.getGraphics());
                    DisplaySuccessful = true;
                    
                    frameNum = imgProc.FRAME_NUMBER(); //sets the frame number so that we do not update whe nwe don't need to
                } else {
                    Thread.sleep(25);
                }
            } catch(Exception ex) {
                System.out.println("Could not load the image! Message: "+ex.getCause());
                ex.printStackTrace();
                DisplaySuccessful = false;
                }
            }
            //output everything as a series of lines in the console.
            System.out.println("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n----------FRAME DISPLAY SUMMARY----------");
            System.out.println("Frame: "+String.valueOf(frameNum)+"\n");
            System.out.println("THREAD 1: Image Processing:--\n");
            System.out.println("   ---Task---   "+                                        " |  Status | Time |");
            System.out.println("Frame take:      | "+SuccessByBool(imgProc.IMG_GET_IMAGE())             + " | " + String.valueOf(imgProc.IMG_TAKE_TIME()) +   " | ");
            if(Constants.DO_BLUR)
                System.out.println("Frame blur:      | "+SuccessByBool(imgProc.IMG_IMAGE_BLUR())            + " | " + String.valueOf(imgProc.IMG_BLUR_TIME()) +   " | ");
            if(Constants.DO_DILATE)
                System.out.println("Frame dialate:   | "+SuccessByBool(imgProc.IMG_IMAGE_DILATE())          + " | " + String.valueOf(imgProc.IMG_DILATE_TIME())+  " | ");
            if(Constants.DO_ERODE)
                System.out.println("Frame erode:     | "+SuccessByBool(imgProc.IMG_IMAGE_ERODE())           + " | " + String.valueOf(imgProc.IMG_ERODE_TIME()) +  " | ");
            System.out.println("Frame toHSV:     | "+SuccessByBool(imgProc.IMG_IMAGE_HSV())             + " | " + String.valueOf(imgProc.IMG_HSV_TIME()) +    " | ");
            System.out.println("Frame toBinary:  | "+SuccessByBool(imgProc.IMG_IMAGE_BIN())             + " | " + String.valueOf(imgProc.IMG_BIN_TIME()) +    " | ");
            if(Constants.DISPLAY_IMAGE_OUTPUT)
                System.out.println("Frame write:     | "+SuccessByBool(imgProc.IMG_IMAGE_WRITE())   + " | " + String.valueOf(imgProc.IMG_WRITE_TIME()) +  " | ");
            System.out.println("-------------------------------------------------------------------------------------------------");
            System.out.println("THREAD:      | "+SuccessByBool(imgProc.THREAD_SUCCESS())        + " | " + String.valueOf(imgProc.THREAD_TIME()));
        }
    }
    private String SuccessByBool(boolean success) {
        if(success) {
            return "Success";
        } else {
            return "Failiure";
        }
    }
}