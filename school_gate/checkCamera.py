import cv2

print(cv2.__version__)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Unable to access the camera.")
else:
    print("Camera is accessible.")
cap.release()
