import cv2
import os
import numpy as np
import time
from database import setup_db, add_child, get_child_data, update_spent

# Initialize Database
setup_db()

def get_camera():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    return cap

def register_and_train():
    u_id = int(input("Enter New Student ID: "))
    u_name = input("Enter Student Name: ")
    u_limit = float(input("Set Credit Limit: "))
    
    cap = get_camera()
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    
    samples = []
    ids = []
    count = 0
    
    print("Look at the camera. Capturing 30 samples...")
    while count < 30:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in faces:
            count += 1
            samples.append(gray[y:y+h, x:x+w])
            ids.append(u_id)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.imshow("Registering...", frame)
            
        
        if cv2.waitKey(1) & 0xFF == ord('q'): break
    
    # Save to Database & Train
    add_child(u_id, u_name, u_limit, f"photos/{u_id}.jpg")
    recognizer.train(samples, np.array(ids))
    recognizer.write(f"trainer_{u_id}.yml")
    
    cap.release()
    cv2.destroyAllWindows()
    print(f"User {u_name} Registered Successfully!")

def payment_mode():
    u_id_to_load = int(input("Enter ID to scan for payment: "))
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    
    try:
        recognizer.read(f"trainer_{u_id_to_load}.yml")
    except:
        print("No face data found for this ID!")
        return

    cap = get_camera()
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    success_msg_timer = 0

    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.2, 5)

        for (x, y, w, h) in faces:
            id_pred, conf = recognizer.predict(gray[y:y+h, x:x+w])
            
            if conf < 60: # Match found
                data = get_child_data(id_pred)
                name, limit, spent, _ = data
                label = f"{name} | Bal: {limit-spent}"
                color = (0, 255, 0)
            else:
                label = "Unknown"
                color = (0, 0, 255)

            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        if time.time() < success_msg_timer:
            cv2.putText(frame, "PAYMENT SUCCESS", (150, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

        cv2.imshow("FaceSecure Pay Terminal", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('p'):
            update_spent(u_id_to_load, 10)
            success_msg_timer = time.time() + 2
        elif key == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()

# Main Menu
if __name__ == "__main__":
    while True:
        print("\n1. Register New Student\n2. Start Payment Mode\n3. Exit")
        choice = input("Select Option: ")
        if choice == '1': register_and_train()
        elif choice == '2': payment_mode()
        else: break