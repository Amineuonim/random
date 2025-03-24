
"""
so this is the script i use to detect dark dots using open cv , the main reason why i am doing this is so that i can have boiler plate code to use later in case i need it in the future. the idea behind using this is to do a facial mocap on my low end pc 
the idea was to approach this in the more traditional way by drawing dots on what you want to capture in a relatively bright background then you can use th coordinates to manipulate the mesh like you want. 
some usefull links i used are : 
learn opencv documentation : https://learnopencv.com/blob-detection-using-opencv-python-c/ 
this repository which is what i was aiming for: https://github.com/jkirsons/FacialMotionCapture_v2 
related reddit post : https://www.reddit.com/r/unrealengine/comments/tjmulx/finally_released_my_livelink_facial_mocap_tool/



"""


import cv2
import numpy as np

# Initialize camera
cam = cv2.VideoCapture(0)

def detect():
  while True:
    # launch webcam
    ret, frame = cam.read()
    if not ret:
      print("Failed to grab frame")
      break

    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Set up the SimpleBlobDetector
    detector = cv2.SimpleBlobDetector_create()

    # Detect gray blobs
    blobs = detector.detect(gray)

        # Draw detected blobs as red circles
    im_with_keypoints = cv2.drawKeypoints(gray, blobs, np.array([]), (0, 0, 255),
                                              cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    # render the dots
    cv2.imshow("Keypoints", im_with_keypoints)

    if cv2.waitKey(1) & 0xFF == ord('q'):
      break

  cam.release()
  cv2.destroyAllWindows()

detect()
