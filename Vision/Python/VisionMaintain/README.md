<h1>PYTHON CODE:</h1>
--
Some information:<br>
1. Use "StartLifecam.sh" to start the entire program. Settings set in "StartLifecam.sh" may need to be modified or completely changed based on what camera is being used.
<br>
2. Program looks for an object in image defined by process setting variables. Center of object is calculated and stored in "BoxCenterX" and "BoxCenterY" in pixels 

The settings and what they mean
--
TARGET_COLOR_LOW: The low bound of target color of object in BGR (numpy array) <br>
TARGET_COLOR_HIGH: The high bound of target color of object in BGR (numpy array) <br>
TARGET_NONZERO_PIXELS: The number of not black pixels that need to be detected after thresholding for the program to continue processing the image<br>
THRESHOLD_LOW: The low value for the cv2.threshold function<br>
THRESHOLD_HIGH: The max value for the cv2.threshold function<br>
TARGET_CONTOUR_AREA_MAX: The maximum area in pixels that the object is. Any object that is not in area range is eliminated.<br>
TARGET_CONTOUR_AREA_MIN: The minimum area in pixels that the object is.<br>
TARGET_CONTOUR_ASPECT_RATIO_MAX: The maximum value for aspect ratio that the object is. Any object that is not in aspect ratio range is eliminated.<br>
TARGET_CONTOUR_ASPECT_RATIO_MIN: The minimum value for aspect ratio that the object is.<br>
