import cv2
import os
import numpy as np
import time
from database import setup_db, add_child, get_child_data, update_spent

# Initialize core database connection and schema
setup_db()

def get_camera():
    """
    Initializes the system camera with failover support for multiple devices.
    """
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    return cap

def register_and_train():
    """
    Handles biometric identity enrollment and model training.
    """
    u_id = int(input("System Log: Enter New Student ID: "))
    u_name = input("System Log: Enter Student Name: ")
    u_limit = float(input("System Log: Set Credit Limit: "))
    
    cap = get_camera()
    # Loading Haar Cascade for real-time frontal face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    
    samples = []
    ids = []
    count = 0
    
    print("[INFO] Initializing biometric scanner. Capturing 30 samples...")
    while count < 30:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in faces:
            count += 1
            samples.append(gray[y:y+h, x:x+w])
            ids.append(u_id)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.imshow("Biometric Registration in Progress...", frame)
            
        if cv2.waitKey(1) & 0xFF == ord('q'): 
            break
    
    # Commit identity data to database and export trained biometric model
    add_child(u_id, u_name, u_limit, f"photos/{u_id}.jpg")
    recognizer.train(samples, np.array(ids))
    recognizer.write(f"trainer_{u_id}.yml")
    
    cap.release()
    cv2.destroyAllWindows()
    print(f"[SUCCESS] Digital ID for {u_name} generated and stored.")

def payment_mode():
    """
    Launches the live payment terminal with biometric verification protocols.
    """
    u_id_to_load = int(input("System Log: Scan User ID for transaction: "))
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    
    try:
        recognizer.read(f"trainer_{u_id_to_load}.yml")
    except Exception as e:
        print(f"[ERROR] Logic Failure: No biometric signature found for ID {u_id_to_load}.")
        return

    cap = get_camera()
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    success_msg_timer = 0

    print("[INFO] Terminal active. Press 'P' to authorize transaction.")
    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.2, 5)

        for (x, y, w, h) in faces:
            id_pred, conf = recognizer.predict(gray[y:y+h, x:x+w])
            
            if conf < 60: # Threshold for authorized identity match
                data = get_child_data(id_pred)
                name, limit, spent, _ = data
                label = f"Verified: {name} | Credits: {limit-spent}"
                color = (0, 255, 0) # Green for authorization success
            else:
                label = "Unauthorized Access"
                color = (0, 0, 255) # Red for security alert

            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        if time.time() < success_msg_timer:
            cv2.putText(frame, "TRANSACTION SUCCESSFUL", (100, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

        cv2.imshow("FaceSecure Pay Terminal v1.0", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('p'):
            update_spent(u_id_to_load, 10) # Log standard transaction unit
            success_msg_timer = time.time() + 2
        elif key == ord('q'): 
            break

    cap.release()
    cv2.destroyAllWindows()

# Main System Entry Point
if __name__ == "__main__":
    while True:
        print("\n--- FaceSecure Enterprise Operations ---")
        print("1. Enroll New Identity\n2. Start Payment Terminal\n3. System Exit")
        choice = input("Select System Protocol: ")
        
        if choice == '1': 
            register_and_train()
        elif choice == '2': 
            payment_mode()
        elif choice == '3': 
            print("[INFO] Core system offline.")
            break