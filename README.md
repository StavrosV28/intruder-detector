# intruder-detector
This project detects, classifies, and logs whenever a person(intruder) is detected within the frame of the camera and uses OpenCV motion detection to trigger YOLO classification only when motion is confirmed, logging all detections to a SQLite database.

# How It Works
- The pipeline runs in three stages:

1. Motion Detection - Each frame is converted to grayscale and passed through OpenCV's MOG2 background subtractor. MOG2 builds a statistical model of the background over time and flags pixels that deviate from it. 
2. Shadow detection is enabled to reduce false positives caused by lighting changes.
3. Contour Filtering - Contours are extracted from the motion mask. Any contour with an area smaller than 500 pixels is discarded as noise. This prevents small pixel fluctuations from triggering the next stage.
4. YOLO Classification - When motion clears the contour threshold, YOLOv8 (nano) runs inference on that frame. To avoid redundant processing, YOLO only runs every 5 frames during active motion. Detections under 70% confidence are ignored. Results are drawn on the frame and written to SQLite.

- There is also a 200-frame warm-up period at startup that lets MOG2 learn the background before detection begins. Without this, the model would flag the entire initial scene as motion.
