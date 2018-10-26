/**
 * CONSTANTS CLASS FOR 3695 VISION PROGRAM
 * holds enumerations representing constant unchanging values that are used throughout the program.
 */

 import org.opencv.core.Scalar;
public class Constants {
    //settings for output to user.
    public static final boolean DISPLAY_TEXT_OUTPUT = true; //displays frame times as a table on the terminal. 
    public static final boolean DISPLAY_IMAGE_OUTPUT = false; //Displays the output image on a separate window. This one actually hecking chews on the CPU though

    //some options for how process is done. 
    public static final boolean DO_BLUR = false; //setting for if the image is blurred before process is carried out. might not be necessary if a blurry camera is used.
    public static final boolean DO_DILATE = false; //setting for dilating the image before looking for colors
    public static final boolean DO_ERODE = false;  //setting for eroding the image

    //numbers that are used in the process.
    //target color converted to opencv ranges: 72, 173, 173
    public static final Scalar COLOR_LOW_BOUND = new Scalar(32, 133, 133); //low boundary of color that is seen by the processor - HSV ONLY
    public static final Scalar COLOR_HIGH_BOUND = new Scalar(132, 233, 233); //high boundary of color that is seen by the processor - HSV ONLY

    public static final int ERODE_SIZE = 5;
    public static final int DILATE_SIZE = 5;

    
}