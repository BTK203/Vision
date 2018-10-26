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

import java.*;

public class Main {

  //boolean values that entail whether a certain operation of the program was successful or not

  
  public static void main(String[] args) {
    // Loads our OpenCV library. This MUST be included
    System.out.println("Main entry runs.");
    System.loadLibrary("opencv_java310");
    System.out.println("runner instantiated.");
    VisionMonitor runner = new VisionMonitor();
    System.out.println("runner run method called.");
    runner.run();
    // Connect NetworkTables, and get access to the publishing table

    /**
      
      //---NETWORK TABLES TO PUT IN LATER, WE JUST FOCUSING ON FINDING STUFF RIGHT NOW
      
    NetworkTable.setClientMode();
    // Set your team number here


    NetworkTable.setTeam(9999);

    NetworkTable.initialize();

    */
    
    // This is the network port you want to stream the raw received image to
    // By rules, this has to be between 1180 and 1190, so 1185 is a good choice
    
    //int streamPort = 1185;

    // This stores our reference to our mjpeg server for streaming the input image
    
    //MjpegServer inputStream = new MjpegServer("MJPEG Server", streamPort);

    // Selecting a Camera
    // Uncomment one of the 2 following camera options
    // The top one receives a stream from another device, and performs operations based on that
    // On windows, this one must be used since USB is not supported
    // The bottom one opens a USB camera, and performs operations on that, along with streaming
    // the input image so other devices can see it
    
      

    /***********************************************/

    
    

    

    // This creates a CvSource to use. This will take in a Mat image that has had OpenCV operations
    // operations 
    //CvSource imageSource = new CvSource("CV Image Source", VideoMode.PixelFormat.kMJPEG, 640, 480, 30);
    //MjpegServer cvStream = new MjpegServer("CV Image Stream", 1186);
    //cvStream.setSource(imageSource);

    // All Mats and Lists should be stored outside the loop to avoid allocations
    // as they are expensive to creat

    // Infinitely process image


  }
}