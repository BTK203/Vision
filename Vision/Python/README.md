<h1>PYTHON CODE:</h1>
--
Some information:<br>
1. Use "StartLifecam.sh" to start the entire program. Settings set in "StartLifecam.sh" may need to be modified or completely changed based on what camera is being used.
<br>
2. Program looks for an object in image defined by process setting variables. Center of object is calculated and stored in "BoxCenterX" and "BoxCenterY" in pixels 

COMMAND LINE COMMANDS:
--
Since this is a rough version, I won't work too hard on a GUI for updating values at runtime yet. Here are commands for Dev mode:
"c" - allows user to change target colors during runtime
"t" - allows user to change target threshold during runtime
"time" - returns a summary of how much time threads are taking
"current" - shows all values that can be modified (so right now its color and threshold)
"stream" - shows live stream from camera. If the target is found, a point is drawn on the center.
"quit" - exits the program
