import cv2

# APNE MOBILE KA IP YAHAN LIKHEIN (DroidCam app se dekh kar)
# Example: http://192.168.10.5:4747/video
url = "http://192.168.18.10:4747/video" 

print("Connecting to DroidCam...")
cap = cv2.VideoCapture(url)

if not cap.isOpened():
    print("Error: DroidCam connect nahi ho raha! Check karein ke Mobile aur Laptop ek hi WiFi par hain.")
else:
    print("Zabardast! Video stream shuru ho gayi hai.")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    cv2.imshow("DROIDCAM_LIVE", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()