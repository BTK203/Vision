/**
 * PROCESS TIMER DESIGNED FOR RPI OPENCV APPLICATION
 * written by:Brach Knutson, FRC3695
 */
import java.*;

 public class ProcessTimer {
    private long startTime;
    private long endTime;

    public void Start() {
        startTime = System.nanoTime();
    }

    public long End() { //returns the time elapsed between start() and end() as a long in milliseconds
        endTime = System.nanoTime();
        long totalTime = endTime - startTime;
        totalTime /= 1000000; //convert to ms
        startTime = 0;
        endTime = 0;
        return totalTime;
    }
 }