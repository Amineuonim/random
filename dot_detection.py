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
