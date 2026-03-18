import cv2
import os
from database import setup_db, add_child, get_child_data, update_spent

# --- ERROR-FREE CAMERA LOADER ---
def find_available_camera():
    # 1. Sabse pehle Mobile IP ka rasta (List mein sabse pehle)
    # 2. Phir Laptop Camera (0)
    # 3. Phir External/USB Cameras (1, 2)
    sources = [
        "http://192.168.100.101:4747/video", 
        0, 
        1, 
        2
    ]
    
    for src in sources:
        print(f"Trying Camera Source: {src}...")
        cap = cv2.VideoCapture(src)
        
        # Check karte hain ke kya camera sach mein frame de raha hai
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"Success! Connected to source: {src}")
                return cap
            else:
                cap.release()
    
    return None

setup_db()

# --- REGISTRATION ---
print("\n--- FaceSecure Pay: Multi-Device Support ---")
u_id = int(input("Enter ID: "))
u_name = input("Enter Name: ")
u_limit = float(input("Set Limit: "))
add_child(u_id, u_name, u_limit, f"photos/{u_id}.jpg")

# --- AUTO-DETECTION ---
cap = find_available_camera()

if cap is None:
    print("\n[!] FATAL ERROR: Kisi bhi source se camera nahi mila.")
    print("Check karein: 1. Camera plug-in hai? 2. Koi aur app camera toh nahi use kar rahi?")
else:
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    print("\n[SYSTEM ONLINE] Scanning for faces...")

    while True:
        success, img = cap.read()
        if not success: break

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        data = get_child_data(u_id)

        if len(faces) > 0 and data:
            name, limit, spent, _ = data
            balance = limit - spent
            for (x, y, w, h) in faces:
                # Designing the HUD (Heads-up Display)
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(img, f"{name.upper()} | ${balance}", (x, y-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.imshow("FaceSecure Pay - Universal View", img)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('p'):
            update_spent(u_id, 10)
            print("Payment $10: Done")
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()